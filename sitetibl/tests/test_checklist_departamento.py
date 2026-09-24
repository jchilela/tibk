from datetime import date, time

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from sitetibl.views import _can_toggle_item, _departamentos_do_irmao

from sitetibl.models import (
    Actividade, ChecklistActividade, Departamento, Irmao, ItemChecklist,
    Listaactividades, Mandato, Municipio, Provincia, Sitio,
)


class ChecklistDepartamentoTest(TestCase):
    def setUp(self):
        luanda, _ = Provincia.objects.get_or_create(nome='Luanda', defaults={'codigo': 'LDA'})
        mun, _ = Municipio.objects.get_or_create(nome='Luanda', defaults={'provincia': luanda})
        sede, _ = Sitio.objects.get_or_create(
            designacao='Sede Checklist',
            defaults={'provincia': luanda, 'municipio': mun, 'tipo': '1'},
        )
        self.comunicacao = Departamento.objects.create(designacao='Comunicacao', abreviacao='COM')
        self.louvor = Departamento.objects.create(designacao='Louvor', abreviacao='LOU')

        self.lider = self._irmao('lider', 'Com', sede, 'lider.ckl@tibl.local')
        self.membro = self._irmao('Ana', 'Som', sede, 'ana.ckl@tibl.local')
        self.outro = self._irmao('Paulo', 'Louvor', sede, 'paulo.ckl@tibl.local')

        Mandato.objects.create(irmao=self.lider, departamento=self.comunicacao, funcao='lider')
        Mandato.objects.create(irmao=self.membro, departamento=self.comunicacao, funcao='membro')
        Mandato.objects.create(irmao=self.outro, departamento=self.louvor, funcao='lider')

        lista = Listaactividades.objects.create(designacao='Comunicacao semanal')
        self.sabado = Actividade.objects.create(
            designacao=lista, inicio=time(9, 0), fim=time(12, 0), data=date(2026, 9, 19),
        )
        self.sabado_seguinte = Actividade.objects.create(
            designacao=lista, inicio=time(9, 0), fim=time(12, 0), data=date(2026, 9, 26),
            parent_event=self.sabado,
        )
        self.url = reverse('sitetibl:checklist_actividade', args=[self.sabado.id])

    def _irmao(self, nome, apelido, sede, email):
        user = User.objects.create_user(username=email.split('@')[0], password='Teste@123')
        return Irmao.objects.create(
            nome=nome, apelido=apelido, sexo='F', email=email,
            municipio=sede.municipio, provincia=sede.provincia,
            localcongregacao=sede, categoria='membro_batizado', user=user,
        )

    def test_responsavel_cria_e_a_serie_repete_por_marcar(self):
        self.client.force_login(self.lider.user)
        resposta = self.client.post(self.url, {
            'criar_checklist': '1',
            'departamento': self.comunicacao.id,
        })
        self.assertEqual(resposta.status_code, 302)
        origem = ChecklistActividade.objects.get(actividade=self.sabado, departamento=self.comunicacao)
        seguinte = ChecklistActividade.objects.get(actividade=self.sabado_seguinte, departamento=self.comunicacao)

        self.client.post(reverse('sitetibl:adicionar_item_checklist', args=[origem.id]), {
            'descricao': 'Abrir o som',
            'responsavel': self.membro.id,
            'ordem': 1,
        })
        item_origem = origem.items.get()
        item_seguinte = seguinte.items.get()
        self.assertEqual(item_origem.responsavel, self.membro)
        self.assertFalse(item_seguinte.concluido)
        self.assertEqual(item_seguinte.descricao, 'Abrir o som')

    def test_membro_so_marca_o_seu_item_e_nao_ve_outro_departamento(self):
        checklist = ChecklistActividade.objects.create(actividade=self.sabado, departamento=self.comunicacao)
        ChecklistActividade.objects.create(actividade=self.sabado, departamento=self.louvor)
        meu = ItemChecklist.objects.create(checklist=checklist, descricao='Abrir o som', responsavel=self.membro)
        alheio = ItemChecklist.objects.create(checklist=checklist, descricao='Projectar o texto', responsavel=self.lider)

        pedido = RequestFactory().get(self.url)
        pedido.user = self.membro.user
        departamentos = list(_departamentos_do_irmao(self.membro))
        self.assertIn(self.comunicacao, departamentos)
        self.assertNotIn(self.louvor, departamentos)
        self.assertTrue(_can_toggle_item(pedido, meu))
        self.assertFalse(_can_toggle_item(pedido, alheio))

        self.client.force_login(self.membro.user)
        marcar = self.client.post(
            reverse('sitetibl:toggle_item_checklist', args=[meu.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(marcar.status_code, 200)
        meu.refresh_from_db()
        self.assertTrue(meu.concluido)

        recusado = self.client.post(
            reverse('sitetibl:toggle_item_checklist', args=[alheio.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(recusado.status_code, 403)

    def test_membro_nao_cria_checklist(self):
        self.client.force_login(self.membro.user)
        resposta = self.client.post(self.url, {
            'criar_checklist': '1',
            'departamento': self.comunicacao.id,
        })
        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(ChecklistActividade.objects.filter(departamento=self.comunicacao).exists())
