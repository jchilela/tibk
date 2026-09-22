from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from sitetibl.models import Ocorrencia, Sitio


class OcorrenciaPublicaTest(TestCase):
    def test_pagina_registo_publica_acessivel_sem_login(self):
        response = self.client.get(reverse('sitetibl:registar_ocorrencia'))
        self.assertEqual(response.status_code, 200)

    def test_submeter_ocorrencia_anonima_cria_registo(self):
        sitio = Sitio.objects.create(designacao='Templo Principal', tipo='1')
        response = self.client.post(reverse('sitetibl:registar_ocorrencia'), {
            'tipo_reportante': 'visitante',
            'nome_reportante': '',
            'telefone_reportante': '',
            'categoria': 'seguranca',
            'titulo': 'Porta danificada',
            'descricao': 'A porta lateral do templo está com a fechadura partida.',
            'local': sitio.id,
        })
        self.assertEqual(Ocorrencia.objects.count(), 1)
        ocorrencia = Ocorrencia.objects.first()
        self.assertEqual(ocorrencia.estado, 'pendente')
        self.assertEqual(ocorrencia.local, sitio)
        self.assertIsNotNone(ocorrencia.data_ocorrencia)
        self.assertIsNotNone(ocorrencia.hora_ocorrencia)
        self.assertTrue(ocorrencia.protocolo.startswith('OC-'))
        self.assertRedirects(
            response,
            reverse('sitetibl:ocorrencia_sucesso', args=[ocorrencia.protocolo]),
        )

    def test_telefone_invalido_gera_erro(self):
        response = self.client.post(reverse('sitetibl:registar_ocorrencia'), {
            'tipo_reportante': 'membro',
            'telefone_reportante': '123',
            'categoria': 'outro',
            'titulo': 'Teste',
            'descricao': 'Descricao de teste',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ocorrencia.objects.count(), 0)
        self.assertContains(response, 'exatamente 9 números')

    def test_honeypot_preenchido_bloqueia_submissao(self):
        response = self.client.post(reverse('sitetibl:registar_ocorrencia'), {
            'tipo_reportante': 'visitante',
            'website': 'http://spam.example.com',
            'categoria': 'outro',
            'titulo': 'Spam bot',
            'descricao': 'Descricao gerada por bot.',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ocorrencia.objects.count(), 0)

    def test_throttle_bloqueia_segunda_submissao_imediata(self):
        dados = {
            'tipo_reportante': 'visitante',
            'categoria': 'outro',
            'titulo': 'Primeira ocorrencia',
            'descricao': 'Descricao de teste suficientemente longa.',
        }
        response1 = self.client.post(reverse('sitetibl:registar_ocorrencia'), dados)
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(Ocorrencia.objects.count(), 1)

        dados['titulo'] = 'Segunda ocorrencia'
        response2 = self.client.post(reverse('sitetibl:registar_ocorrencia'), dados)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(Ocorrencia.objects.count(), 1)

    def test_local_pre_selecionado_via_querystring(self):
        sitio = Sitio.objects.create(designacao='Célula Central', tipo='2')
        response = self.client.get(reverse('sitetibl:registar_ocorrencia') + f'?local={sitio.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{sitio.id}" selected')

    def test_protocolo_gerado_automaticamente_e_unico(self):
        for i in range(3):
            Ocorrencia.objects.create(
                categoria='outro',
                titulo=f'Ocorrencia {i}',
                descricao='Descricao de teste',
            )
        protocolos = list(Ocorrencia.objects.values_list('protocolo', flat=True))
        self.assertEqual(len(protocolos), len(set(protocolos)))

    def test_pagina_sucesso_mostra_protocolo(self):
        ocorrencia = Ocorrencia.objects.create(
            categoria='sugestao',
            titulo='Sugestão de melhoria',
            descricao='Sugiro melhorar a sinalização.',
        )
        response = self.client.get(
            reverse('sitetibl:ocorrencia_sucesso', args=[ocorrencia.protocolo])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ocorrencia.protocolo)

    def test_consultar_ocorrencia_sem_login_encontra_registo(self):
        ocorrencia = Ocorrencia.objects.create(
            categoria='seguranca',
            titulo='Consulta pública',
            descricao='Teste de consulta.',
        )
        response = self.client.get(
            reverse('sitetibl:consultar_ocorrencia') + f'?protocolo={ocorrencia.protocolo}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ocorrencia.protocolo)
        self.assertContains(response, ocorrencia.titulo)

    def test_consultar_ocorrencia_protocolo_inexistente(self):
        response = self.client.get(
            reverse('sitetibl:consultar_ocorrencia') + '?protocolo=OC-000000-9999'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhuma ocorrência encontrada')


class OcorrenciaGestaoTest(TestCase):
    def setUp(self):
        from sitetibl.models import Irmao, Departamento

        self.user = User.objects.create_user(username='gestor_oc', password='Teste@123')
        self.irmao = Irmao.objects.create(nome='Gestor', apelido='Segurança', user=self.user)
        self.dept_seguranca = Departamento.objects.create(
            designacao='Departamento de Segurança',
            lider_departamento=self.irmao,
        )

        self.client = Client()
        self.client.login(username='gestor_oc', password='Teste@123')

        self.ocorrencia = Ocorrencia.objects.create(
            categoria='manutencao',
            titulo='Lâmpada fundida',
            descricao='Lâmpada do corredor principal fundida.',
        )

    def test_gestao_ocorrencias_requer_login(self):
        client_anonimo = Client()
        response = client_anonimo.get(reverse('sitetibl:gestao_ocorrencias'))
        self.assertEqual(response.status_code, 302)

    def test_gestao_ocorrencias_lista_registo(self):
        response = self.client.get(reverse('sitetibl:gestao_ocorrencias'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ocorrencia.protocolo)

    def test_atualizar_estado_para_resolvida(self):
        response = self.client.post(
            reverse('sitetibl:atualizar_estado_ocorrencia', args=[self.ocorrencia.id]),
            {'estado': 'resolvida', 'nota': 'Lâmpada substituída.'},
        )
        self.ocorrencia.refresh_from_db()
        self.assertEqual(self.ocorrencia.estado, 'resolvida')
        self.assertEqual(self.ocorrencia.nota_resolucao, 'Lâmpada substituída.')
        self.assertIsNotNone(self.ocorrencia.data_resolucao)
        self.assertEqual(self.ocorrencia.resolvido_por, self.user)
        self.assertRedirects(response, reverse('sitetibl:gestao_ocorrencias'))

    def test_qrcode_pagina_e_imagem(self):
        response = self.client.get(reverse('sitetibl:ocorrencia_qrcode'))
        self.assertEqual(response.status_code, 200)

        response_img = self.client.get(reverse('sitetibl:ocorrencia_qrcode_imagem'))
        self.assertEqual(response_img.status_code, 200)
        self.assertEqual(response_img['Content-Type'], 'image/png')

    def test_membro_comum_sem_acesso_a_gestao(self):
        from sitetibl.models import Irmao

        outro_user = User.objects.create_user(username='membro_comum', password='Teste@123')
        Irmao.objects.create(nome='Membro', apelido='Comum', user=outro_user)
        client_outro = Client()
        client_outro.login(username='membro_comum', password='Teste@123')

        response = client_outro.get(reverse('sitetibl:gestao_ocorrencias'))
        self.assertEqual(response.status_code, 403)

    def test_secretario_do_departamento_seguranca_tem_acesso(self):
        from django.contrib.auth.models import Group
        from sitetibl.models import Irmao, Mandato

        secretario_user = User.objects.create_user(username='secretario_seg', password='Teste@123')
        secretario_irmao = Irmao.objects.create(nome='Secretário', apelido='Segurança', user=secretario_user)
        Mandato.objects.create(irmao=secretario_irmao, departamento=self.dept_seguranca, funcao='secretario')

        client_secretario = Client()
        client_secretario.login(username='secretario_seg', password='Teste@123')
        response = client_secretario.get(reverse('sitetibl:gestao_ocorrencias'))
        self.assertEqual(response.status_code, 200)

    def test_administrador_mantem_acesso(self):
        from django.contrib.auth.models import Group

        admin_group = Group.objects.create(name='Administrador')
        admin_user = User.objects.create_user(username='admin_geral', password='Teste@123')
        admin_user.groups.add(admin_group)

        client_admin = Client()
        client_admin.login(username='admin_geral', password='Teste@123')
        response = client_admin.get(reverse('sitetibl:gestao_ocorrencias'))
        self.assertEqual(response.status_code, 200)

    def test_qrcode_especifico_por_local(self):
        sitio = Sitio.objects.create(designacao='Templo Sede', tipo='1')
        response = self.client.get(
            reverse('sitetibl:ocorrencia_qrcode') + f'?local_id={sitio.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'?local={sitio.id}')

        response_img = self.client.get(
            reverse('sitetibl:ocorrencia_qrcode_imagem') + f'?local_id={sitio.id}'
        )
        self.assertEqual(response_img.status_code, 200)
        self.assertEqual(response_img['Content-Type'], 'image/png')

    def test_relatorio_ocorrencias_html(self):
        response = self.client.get(reverse('sitetibl:relatorio_ocorrencias'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ocorrencia.protocolo)

    def test_relatorio_ocorrencias_html_requer_permissao(self):
        outro_user = User.objects.create_user(username='sem_acesso_rel', password='Teste@123')
        client_outro = Client()
        client_outro.login(username='sem_acesso_rel', password='Teste@123')
        response = client_outro.get(reverse('sitetibl:relatorio_ocorrencias'))
        self.assertEqual(response.status_code, 403)

    def test_relatorio_ocorrencias_pdf(self):
        response = self.client.get(
            reverse('sitetibl:relatorio_ocorrencias_pdf') + '?periodo=mensal&ano=todos'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_relatorio_ocorrencias_periodos_validos(self):
        for periodo in ['semanal', 'mensal', 'trimestral', 'anual']:
            response = self.client.get(
                reverse('sitetibl:relatorio_ocorrencias') + f'?periodo={periodo}&ano=todos'
            )
            self.assertEqual(response.status_code, 200)

    def test_acta_ocorrencias_get_formulario(self):
        response = self.client.get(reverse('sitetibl:acta_ocorrencias_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Acta de Ocorrências')

    def test_acta_ocorrencias_post_gera_pdf(self):
        response = self.client.post(reverse('sitetibl:acta_ocorrencias_pdf'), {
            'periodo': 'mensal',
            'ano': 'todos',
            'deliberacoes': 'Reforçar rondas nocturnas.',
            'nome_responsavel': 'Líder Teste',
            'nome_secretario': 'Secretário Teste',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_acta_ocorrencias_requer_permissao(self):
        outro_user = User.objects.create_user(username='sem_acesso_acta', password='Teste@123')
        client_outro = Client()
        client_outro.login(username='sem_acesso_acta', password='Teste@123')
        response = client_outro.get(reverse('sitetibl:acta_ocorrencias_pdf'))
        self.assertEqual(response.status_code, 403)
