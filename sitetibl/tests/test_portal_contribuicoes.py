from datetime import date
from unittest.mock import patch

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from sitetibl.forms import ContribuicaoForm
from sitetibl.models import Contribuicao, Irmao, Municipio, Provincia, Sitio


class PortalContribuicoesBaseTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='membro_teste', password='Teste@123',
            first_name='Membro', last_name='Teste',
        )

        luanda, _ = Provincia.objects.get_or_create(
            nome='Luanda', defaults={'codigo': 'LDA'},
        )
        mun, _ = Municipio.objects.get_or_create(
            nome='Luanda', defaults={'provincia': luanda},
        )
        sede, _ = Sitio.objects.get_or_create(
            designacao='Sede', defaults={'provincia': luanda, 'municipio': mun, 'tipo': '1'},
        )

        self.irmao = Irmao.objects.create(
            nome='Membro', apelido='Teste', sexo='M',
            email='membro@tibl.local', telefone='923000111',
            municipio=mun, provincia=luanda, localcongregacao=sede,
            categoria='membro_batizado', batizado=True,
            user=self.user,
        )

        self.financeiro = User.objects.create_user(
            username='financeiro_teste', password='Teste@123', is_superuser=True,
        )

        self.client.login(username='membro_teste', password='Teste@123')


class ContribuicaoFormTest(PortalContribuicoesBaseTest):
    def test_valor_zero_e_rejeitado(self):
        form = ContribuicaoForm(data={
            'tipo': 'dizimo', 'valor': '0', 'moeda': 'AKZ', 'data': '2026-10-01',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)

    def test_valor_negativo_e_rejeitado(self):
        form = ContribuicaoForm(data={
            'tipo': 'dizimo', 'valor': '-100', 'moeda': 'AKZ', 'data': '2026-10-01',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)

    def test_valor_positivo_e_aceite(self):
        form = ContribuicaoForm(data={
            'tipo': 'dizimo', 'valor': '5000', 'moeda': 'AKZ', 'data': '2026-10-01',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_comprovativo_com_extensao_falsificada_e_rejeitado(self):
        comprovativo_falso = SimpleUploadedFile(
            'comprovativo.jpg', b'nao e uma imagem jpeg real', content_type='image/jpeg',
        )
        form = ContribuicaoForm(
            data={'tipo': 'dizimo', 'valor': '5000', 'moeda': 'AKZ', 'data': '2026-10-01'},
            files={'comprovativo': comprovativo_falso},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('comprovativo', form.errors)

    def test_comprovativo_com_conteudo_valido_e_aceite(self):
        comprovativo_real = SimpleUploadedFile(
            'comprovativo.png', b'\x89PNG\r\n\x1a\n' + b'0' * 20, content_type='image/png',
        )
        form = ContribuicaoForm(
            data={'tipo': 'dizimo', 'valor': '5000', 'moeda': 'AKZ', 'data': '2026-10-01'},
            files={'comprovativo': comprovativo_real},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_comprovativo_demasiado_grande_e_rejeitado(self):
        from sitetibl.forms import COMPROVATIVO_TAMANHO_MAXIMO_MB

        conteudo_grande = b'\x89PNG\r\n\x1a\n' + b'0' * (COMPROVATIVO_TAMANHO_MAXIMO_MB * 1024 * 1024 + 1)
        comprovativo_grande = SimpleUploadedFile(
            'comprovativo.png', conteudo_grande, content_type='image/png',
        )
        form = ContribuicaoForm(
            data={'tipo': 'dizimo', 'valor': '5000', 'moeda': 'AKZ', 'data': '2026-10-01'},
            files={'comprovativo': comprovativo_grande},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('comprovativo', form.errors)


class ContribuicaoNotificacaoTest(PortalContribuicoesBaseTest):
    def setUp(self):
        super().setUp()
        self.contribuicao = Contribuicao.objects.create(
            irmao=self.irmao, tipo='dizimo', valor=5000, moeda='AKZ', estado='pendente',
        )
        self.client.logout()
        self.client.login(username='financeiro_teste', password='Teste@123')

    @patch('sitetibl.contribuicoes_notificacoes.enviar_sms')
    def test_confirmar_contribuicao_notifica_membro_por_email_e_sms(self, mock_sms):
        response = self.client.post(
            reverse('sitetibl:confirmar_contribuicao', args=[self.contribuicao.id]),
            {'nota': 'Comprovativo validado.'},
        )
        self.assertEqual(response.status_code, 302)
        self.contribuicao.refresh_from_db()
        self.assertEqual(self.contribuicao.estado, 'confirmada')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.irmao.email, mail.outbox[0].to)
        mock_sms.assert_called_once()

    @patch('sitetibl.contribuicoes_notificacoes.enviar_sms')
    def test_rejeitar_contribuicao_notifica_membro_por_email_e_sms(self, mock_sms):
        response = self.client.post(
            reverse('sitetibl:rejeitar_contribuicao', args=[self.contribuicao.id]),
            {'nota': 'Comprovativo ilegível.'},
        )
        self.assertEqual(response.status_code, 302)
        self.contribuicao.refresh_from_db()
        self.assertEqual(self.contribuicao.estado, 'rejeitada')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.irmao.email, mail.outbox[0].to)
        mock_sms.assert_called_once()

    @patch('sitetibl.contribuicoes_notificacoes.enviar_sms')
    @patch('sitetibl.contribuicoes_notificacoes.send_mail', side_effect=Exception('SMTP indisponivel'))
    def test_falha_no_envio_nao_quebra_confirmacao(self, mock_send_mail, mock_sms):
        response = self.client.post(
            reverse('sitetibl:confirmar_contribuicao', args=[self.contribuicao.id]),
            {'nota': ''},
        )
        self.assertEqual(response.status_code, 302)
        self.contribuicao.refresh_from_db()
        self.assertEqual(self.contribuicao.estado, 'confirmada')


class ContribuicaoGraficoTest(PortalContribuicoesBaseTest):
    def setUp(self):
        super().setUp()
        Contribuicao.objects.create(
            irmao=self.irmao, tipo='dizimo', valor=5000, moeda='AKZ',
            estado='confirmada', data=date(date.today().year, 1, 15),
        )
        Contribuicao.objects.create(
            irmao=self.irmao, tipo='oferta', valor=2000, moeda='AKZ',
            estado='pendente', data=date(date.today().year, 1, 20),
        )
        Contribuicao.objects.create(
            irmao=self.irmao, tipo='dizimo', valor=3000, moeda='AKZ',
            estado='confirmada', data=date(date.today().year, 3, 10),
        )

    def test_contexto_contem_dados_do_grafico_de_doze_meses(self):
        response = self.client.get(reverse('sitetibl:minhas_contribuicoes'))
        self.assertEqual(response.status_code, 200)

        grafico = response.context['grafico_contribuicoes']
        self.assertEqual(len(grafico['labels']), 12)
        self.assertEqual(len(grafico['data']), 12)
        self.assertEqual(grafico['ano'], date.today().year)
        self.assertEqual(grafico['data'][0], 7000.0)   # Jan: 5000 + 2000
        self.assertEqual(grafico['data'][1], 0.0)      # Fev: sem dados
        self.assertEqual(grafico['data'][2], 3000.0)   # Mar: 3000

    def test_template_renderiza_canvas_e_dados_json(self):
        response = self.client.get(reverse('sitetibl:minhas_contribuicoes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="graficoContribuicoes"')
        self.assertContains(response, 'id="grafico-contribuicoes-data"')

    def test_kpi_meses_activos_conta_meses_com_contribuicoes_confirmadas(self):
        response = self.client.get(reverse('sitetibl:minhas_contribuicoes'))
        self.assertEqual(response.status_code, 200)
        # Jan e Mar têm contribuições confirmadas; a pendente de Jan não conta duas vezes
        self.assertEqual(response.context['meses_activos'], 2)


class ContribuicaoReciboPdfTest(PortalContribuicoesBaseTest):
    def setUp(self):
        super().setUp()
        self.confirmada = Contribuicao.objects.create(
            irmao=self.irmao, tipo='dizimo', valor=5000, moeda='AKZ',
            estado='confirmada',
        )
        self.pendente = Contribuicao.objects.create(
            irmao=self.irmao, tipo='oferta', valor=2000, moeda='AKZ',
            estado='pendente',
        )

        outro_user = User.objects.create_user(
            username='outro_membro', password='Teste@123',
        )
        self.outro_irmao = Irmao.objects.create(
            nome='Outro', apelido='Membro', sexo='F',
            municipio=self.irmao.municipio, provincia=self.irmao.provincia,
            localcongregacao=self.irmao.localcongregacao,
            categoria='membro_batizado', batizado=True,
            user=outro_user,
        )
        self.contrib_outro = Contribuicao.objects.create(
            irmao=self.outro_irmao, tipo='dizimo', valor=1000, moeda='AKZ',
            estado='confirmada',
        )

    def test_membro_descarrega_recibo_da_propria_contribuicao_confirmada(self):
        response = self.client.get(
            reverse('sitetibl:contribuicao_recibo_pdf', args=[self.confirmada.id]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('recibo_contribuicao_', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_recibo_de_contribuicao_pendente_redireciona(self):
        response = self.client.get(
            reverse('sitetibl:contribuicao_recibo_pdf', args=[self.pendente.id]),
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse('sitetibl:detalhe_contribuicao', args=[self.pendente.id]),
            response['Location'],
        )

    def test_membro_nao_acede_recibo_de_outro_membro(self):
        response = self.client.get(
            reverse('sitetibl:contribuicao_recibo_pdf', args=[self.contrib_outro.id]),
        )
        self.assertEqual(response.status_code, 404)

    def test_financeiro_acede_recibo_de_qualquer_membro(self):
        self.client.logout()

    def test_link_recibo_aparece_na_lista_para_linhas_confirmadas(self):
        response = self.client.get(reverse('sitetibl:minhas_contribuicoes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse('sitetibl:contribuicao_recibo_pdf', args=[self.confirmada.id]),
        )
        self.assertNotContains(
            response,
            reverse('sitetibl:contribuicao_recibo_pdf', args=[self.pendente.id]),
        )


class ContribuicoesExtratoPdfTest(PortalContribuicoesBaseTest):
    def setUp(self):
        super().setUp()
        self.ano = date.today().year
        Contribuicao.objects.create(
            irmao=self.irmao, tipo='dizimo', valor=5000, moeda='AKZ',
            estado='confirmada', data=date(self.ano, 1, 15),
        )
        Contribuicao.objects.create(
            irmao=self.irmao, tipo='oferta', valor=2000, moeda='AKZ',
            estado='confirmada', data=date(self.ano, 3, 10),
        )
        # Pendente não deve entrar no extrato
        Contribuicao.objects.create(
            irmao=self.irmao, tipo='dizimo', valor=9999, moeda='AKZ',
            estado='pendente', data=date(self.ano, 4, 5),
        )
        # Ano diferente não deve entrar no extrato
        Contribuicao.objects.create(
            irmao=self.irmao, tipo='dizimo', valor=7777, moeda='AKZ',
            estado='confirmada', data=date(self.ano - 1, 6, 1),
        )

    def test_extrato_anual_devolve_pdf(self):
        response = self.client.get(
            reverse('sitetibl:contribuicoes_extrato_pdf', args=[self.ano]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(
            f'extrato_contribuicoes_{self.ano}',
            response['Content-Disposition'],
        )
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_extrato_ano_sem_contribuicoes_ainda_devolve_pdf(self):
        response = self.client.get(
            reverse('sitetibl:contribuicoes_extrato_pdf', args=[self.ano + 5]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_extrato_requer_autenticacao(self):
        self.client.logout()
        response = self.client.get(
            reverse('sitetibl:contribuicoes_extrato_pdf', args=[self.ano]),
        )
        self.assertEqual(response.status_code, 302)
