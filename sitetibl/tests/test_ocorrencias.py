from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group

from sitetibl.models import Ocorrencia


class OcorrenciaPublicaTest(TestCase):
    def test_pagina_registo_publica_acessivel_sem_login(self):
        response = self.client.get(reverse('sitetibl:registar_ocorrencia'))
        self.assertEqual(response.status_code, 200)

    def test_submeter_ocorrencia_anonima_cria_registo(self):
        response = self.client.post(reverse('sitetibl:registar_ocorrencia'), {
            'nome_reportante': '',
            'contacto_reportante': '',
            'categoria': 'seguranca',
            'titulo': 'Porta danificada',
            'descricao': 'A porta lateral do templo está com a fechadura partida.',
            'local': 'Templo principal',
        })
        self.assertEqual(Ocorrencia.objects.count(), 1)
        ocorrencia = Ocorrencia.objects.first()
        self.assertEqual(ocorrencia.estado, 'pendente')
        self.assertTrue(ocorrencia.protocolo.startswith('OC-'))
        self.assertRedirects(
            response,
            reverse('sitetibl:ocorrencia_sucesso', args=[ocorrencia.protocolo]),
        )

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


class OcorrenciaGestaoTest(TestCase):
    def setUp(self):
        self.grupo = Group.objects.create(name='Gestão de Ocorrências')
        self.user = User.objects.create_user(username='gestor_oc', password='Teste@123')
        self.user.groups.add(self.grupo)

        from django.contrib.auth.models import Permission
        perm = Permission.objects.get(codename='view_ocorrencia')
        self.user.user_permissions.add(perm)

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
