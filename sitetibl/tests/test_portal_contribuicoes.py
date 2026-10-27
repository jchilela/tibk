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
