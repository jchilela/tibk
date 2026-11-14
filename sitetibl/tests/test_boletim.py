"""Testes do boletim digital (app ``boletim``)."""
import sys
from copy import copy
from datetime import date, time, timedelta
from io import StringIO
from unittest import mock

if sys.version_info >= (3, 14):
    # O Django 4.2.5 não suporta Python 3.14: o cliente de testes copia o
    # contexto dos templates e BaseContext.__copy__ rebenta. Aplica-se aqui
    # (só nos testes) a mesma correcção que o Django publicou upstream.
    # Em produção (Docker, Python 3.10) isto não é executado.
    from django.template import context as _ctx

    def _base_context_copy(self):
        duplicate = _ctx.BaseContext()
        duplicate.__class__ = self.__class__
        duplicate.__dict__ = copy(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    _ctx.BaseContext.__copy__ = _base_context_copy

from django.contrib.auth.models import Group, Permission, User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from boletim.models import (
    Boletim, ConfiguracaoBoletim, FuncaoBoletim, ItemModeloOrdemCulto, ItemOrdemCulto,
    ModeloOrdemCulto, PedidoOracao, ProgramaSemanal,
)
from boletim.services import normalizar_telefone
from sitetibl.models import (
    Actividade, Anuncio, CasoPastoral, Escala, Funcao, Irmao, Listaactividades,
    NotificacaoSistema, VisitanteRecorrente,
)

CACHE_TESTES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                            'LOCATION': 'boletim-testes'}}


@override_settings(CACHES=CACHE_TESTES, BOLETIM_LIMITE_SUBMISSOES=5, BOLETIM_TRUST_PROXY=False)
class BoletimBase(TestCase):
    def setUp(self):
        cache.clear()
        # As escalas disparam email/SMS ao irmão: desligado nos testes.
        patcher = mock.patch('sitetibl.signals.enviar_notificacao_irmao_escalado')
        patcher.start()
        self.addCleanup(patcher.stop)

        self.hoje = date.today()
        self.lista = Listaactividades.objects.create(designacao='Culto Dominical')
        self.irmao = Irmao.objects.create(
            nome='Joaquim', apelido='Sebastião', sexo='M',
            telefone='923111222', telefonewhatsapp='934555666',
            email='joaquim.sebastiao@exemplo.ao',
        )

    def criar_actividade(self, d, inicio=time(9, 0), tema='A fé que vence'):
        return Actividade.objects.create(
            designacao=self.lista, data=d, inicio=inicio, fim=time(11, 0),
            tema=tema, versosbiblicos='Salmos 29:1-4', hinos='Hino 10',
        )

    def criar_boletim(self, d, estado=Boletim.ESTADO_PUBLICADO, **campos):
        return Boletim.objects.create(actividade=self.criar_actividade(d), estado=estado, **campos)

    def url_data(self, d):
        return reverse('boletim:data', args=[d.isoformat()])

    def utilizador(self, *codenames):
        u = User.objects.create_user(username=f'u{User.objects.count()}', password='x')
        for cn in codenames:
            app, codename = cn.split('.')
            u.user_permissions.add(Permission.objects.get(content_type__app_label=app, codename=codename))
        return u


class PaginaPublicaTest(BoletimBase):
    def test_rascunho_nao_e_publico(self):
        b = self.criar_boletim(self.hoje, estado=Boletim.ESTADO_RASCUNHO)
        self.assertEqual(self.client.get(self.url_data(self.hoje)).status_code, 404)
        self.assertEqual(self.client.get(reverse('boletim:pdf', args=[self.hoje.isoformat()])).status_code, 404)
        self.assertNotContains(self.client.get(reverse('boletim:actual')), b.titulo_pt + '</h1>')

    def test_data_invalida_da_404(self):
        self.assertEqual(self.client.get('/boletim/2026-13-45/').status_code, 404)

    def test_actual_escolhe_proximo_publicado(self):
        passado =self.criar_boletim(self.hoje - timedelta(days=7))
        passado.actividade.tema = 'Tema passado'
        passado.actividade.save()
        rascunho = self.criar_boletim(self.hoje + timedelta(days=1), estado=Boletim.ESTADO_RASCUNHO)
        rascunho.actividade.tema = 'Tema rascunho'
        rascunho.actividade.save()
        proximo = self.criar_boletim(self.hoje + timedelta(days=3))
        proximo.actividade.tema = 'Tema próximo'
        proximo.actividade.save()
        depois = self.criar_boletim(self.hoje + timedelta(days=10))
        depois.actividade.tema = 'Tema depois'
        depois.actividade.save()

        r = self.client.get(reverse('boletim:actual'))
        self.assertContains(r, 'Tema próximo')
        self.assertNotContains(r, 'Tema rascunho')
        self.assertNotContains(r, 'Tema passado')

    def test_actual_sem_futuro_mostra_ultimo(self):
        for dias, tema in ((14, 'Tema antigo'), (7, 'Tema último')):
            b = self.criar_boletim(self.hoje - timedelta(days=dias))
            b.actividade.tema = tema
            b.actividade.save()
        r = self.client.get(reverse('boletim:actual'))
        self.assertContains(r, 'Tema último')
        self.assertNotContains(r, 'Tema antigo')

    def test_actual_sem_boletins(self):
        r = self.client.get(reverse('boletim:actual'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Ainda não há nenhum boletim publicado.')

    def test_hoje_conta_como_proximo(self):
        b = self.criar_boletim(self.hoje)
        b.actividade.tema = 'Tema de hoje'
        b.actividade.save()
        self.assertContains(self.client.get(reverse('boletim:actual')), 'Tema de hoje')

    def test_anuncios_filtrados_por_data_e_publico(self):
        d = self.hoje
        self.criar_boletim(d)
        base = {'quemanuncia': self.irmao, 'publico': True}
        Anuncio.objects.create(data=d, data_inicio=d - timedelta(days=3), data_fim=d + timedelta(days=3),
                               titulo='Anúncio no período', texto='a', ordem=2, **base)
        Anuncio.objects.create(data=d, data_inicio=d, titulo='Anúncio do dia', texto='b', ordem=1, **base)
        Anuncio.objects.create(data=d, data_inicio=d - timedelta(days=10), data_fim=d - timedelta(days=1),
                               titulo='Anúncio expirado', texto='c', **base)
        Anuncio.objects.create(data=d, data_inicio=d + timedelta(days=1), data_fim=d + timedelta(days=5),
                               titulo='Anúncio futuro', texto='d', **base)
        Anuncio.objects.create(data=d - timedelta(days=7), data_inicio=d - timedelta(days=7),
                               titulo='Anúncio de outra semana', texto='e', **base)
        Anuncio.objects.create(data=d, data_inicio=d, titulo='Anúncio interno', texto='f',
                               quemanuncia=self.irmao, publico=False)

        r = self.client.get(self.url_data(d))
        conteudo = r.content.decode()
        self.assertIn('Anúncio no período', conteudo)
        self.assertIn('Anúncio do dia', conteudo)
        for titulo in ('Anúncio expirado', 'Anúncio futuro', 'Anúncio de outra semana', 'Anúncio interno'):
            self.assertNotIn(titulo, conteudo)
        # Ordenados pelo campo ordem.
        self.assertLess(conteudo.index('Anúncio do dia'), conteudo.index('Anúncio no período'))

    def test_so_aparecem_escalas_com_funcao_boletim(self):
        b = self.criar_boletim(self.hoje)
        pregador = Funcao.objects.create(designacao='Pregador')
        som = Funcao.objects.create(designacao='Som')
        FuncaoBoletim.objects.create(funcao=pregador, rotulo_pt='Pregação', rotulo_en='Preacher')
        tecnico = Irmao.objects.create(nome='Técnico', apelido='Invisível', sexo='M')
        Escala.objects.create(irmao=self.irmao, actividade=b.actividade, funcao=pregador)
        Escala.objects.create(irmao=tecnico, actividade=b.actividade, funcao=som)

        r = self.client.get(self.url_data(self.hoje))
        self.assertContains(r, 'Pregação')
        self.assertContains(r, 'Joaquim Sebastião')
        self.assertNotContains(r, 'Invisível')
        self.assertNotContains(r, '>Som<')

    def test_pagina_publica_nao_expoe_contactos(self):
        b = self.criar_boletim(self.hoje)
        f = Funcao.objects.create(designacao='Dirigente')
        FuncaoBoletim.objects.create(funcao=f, rotulo_pt='Dirigente do Culto')
        Escala.objects.create(irmao=self.irmao, actividade=b.actividade, funcao=f)
        Anuncio.objects.create(data=self.hoje, data_inicio=self.hoje, titulo='Aviso', texto='Texto',
                               quemanuncia=self.irmao, publico=True)
        urls = [reverse('boletim:actual'), self.url_data(self.hoje), reverse('boletim:arquivo'),
                reverse('boletim:visitante'), reverse('boletim:oracao')]
        # O nome de quem está escalado pode aparecer...
        self.assertContains(self.client.get(self.url_data(self.hoje)), 'Joaquim Sebastião')
        # ...mas nunca os contactos.
        for url in urls:
            conteudo = self.client.get(url).content.decode()
            for segredo in (self.irmao.telefone, self.irmao.telefonewhatsapp, self.irmao.email):
                self.assertNotIn(segredo, conteudo, f'{segredo} exposto em {url}')

    def test_open_graph(self):
        self.criar_boletim(self.hoje)
        r = self.client.get(self.url_data(self.hoje))
        self.assertContains(r, 'property="og:title"')
        self.assertContains(r, 'property="og:description"')
        self.assertContains(r, 'A fé que vence')

    def test_dois_cultos_no_mesmo_dia(self):
        b1 = self.criar_boletim(self.hoje, titulo_pt='Culto em Português')
        act2 = self.criar_actividade(self.hoje, inicio=time(11, 30))
        b2 = Boletim.objects.create(actividade=act2, estado=Boletim.ESTADO_PUBLICADO, titulo_pt='Culto em Inglês')
        r = self.client.get(self.url_data(self.hoje))
        self.assertContains(r, '<h1>Culto em Português</h1>', html=False)
        self.assertContains(r, f'?culto={b2.id}')
        r = self.client.get(self.url_data(self.hoje) + f'?culto={b2.id}')
        self.assertContains(r, '<h1>Culto em Inglês</h1>', html=False)
        self.assertEqual(b1.estado, Boletim.ESTADO_PUBLICADO)

    def test_cache_invalidada_ao_gravar(self):
        b = self.criar_boletim(self.hoje)
        self.assertNotContains(self.client.get(self.url_data(self.hoje)), 'Novo título')
        b.titulo_pt = 'Novo título'
        b.save()
        self.assertContains(self.client.get(self.url_data(self.hoje)), 'Novo título')
        Anuncio.objects.create(data=self.hoje, data_inicio=self.hoje, titulo='Anúncio de última hora',
                               texto='x', quemanuncia=self.irmao, publico=True)
        self.assertContains(self.client.get(self.url_data(self.hoje)), 'Anúncio de última hora')
        cfg = ConfiguracaoBoletim.obter()
        cfg.facebook_url = 'https://www.facebook.com/tiblu'
        cfg.save()
        self.assertContains(self.client.get(self.url_data(self.hoje)), 'https://www.facebook.com/tiblu')

    def test_arquivo_lista_publicados_com_gravacao(self):
        self.criar_boletim(self.hoje - timedelta(days=7), link_gravacao='https://youtu.be/abc')
        self.criar_boletim(self.hoje - timedelta(days=14), estado=Boletim.ESTADO_RASCUNHO, titulo_pt='Rascunho X')
        r = self.client.get(reverse('boletim:arquivo'))
        self.assertContains(r, 'https://youtu.be/abc')
        self.assertNotContains(r, 'Rascunho X')

    def test_pagina_leve(self):
        b = self.criar_boletim(self.hoje)
        for i in range(12):
            ItemOrdemCulto.objects.create(boletim=b, ordem=i, titulo_pt=f'Item {i}')
        r = self.client.get(self.url_data(self.hoje))
        self.assertLess(len(r.content), 100 * 1024)
        self.assertNotIn(b'<script src=', r.content)


class LinguaTest(BoletimBase):
    def test_lang_en_usa_campos_en_e_cai_para_pt(self):
        b = self.criar_boletim(self.hoje, titulo_pt='Ordem do Culto', titulo_en='Order of Service')
        ItemOrdemCulto.objects.create(boletim=b, ordem=1, titulo_pt='Prelúdio', titulo_en='Prelude')
        ItemOrdemCulto.objects.create(boletim=b, ordem=2, titulo_pt='Oração pastoral', titulo_en='')
        Anuncio.objects.create(data=self.hoje, data_inicio=self.hoje, titulo='Retiro', titulo_en='Retreat',
                               texto='Inscrições abertas', texto_en='', quemanuncia=self.irmao, publico=True)

        r = self.client.get(self.url_data(self.hoje) + '?lang=en')
        conteudo = r.content.decode()
        self.assertIn('Order of Service', conteudo)
        self.assertIn('Prelude', conteudo)
        self.assertNotIn('Prelúdio', conteudo)
        self.assertIn('Oração pastoral', conteudo)        # EN vazio → PT
        self.assertIn('Retreat', conteudo)
        self.assertIn('Inscrições abertas', conteudo)     # EN vazio → PT
        self.assertIn('Order of service', conteudo)       # rótulo fixo em EN
        self.assertIn('lang="en"', conteudo)
        self.assertEqual(r.cookies['boletim_lang'].value, 'en')

        # O cookie mantém a língua sem ?lang=
        r = self.client.get(self.url_data(self.hoje))
        self.assertContains(r, 'Prelude')

        r = self.client.get(self.url_data(self.hoje) + '?lang=pt')
        self.assertContains(r, 'Prelúdio')

    def test_pt_por_omissao(self):
        b = self.criar_boletim(self.hoje)
        ItemOrdemCulto.objects.create(boletim=b, ordem=1, titulo_pt='Prelúdio', titulo_en='Prelude')
        r = self.client.get(self.url_data(self.hoje))
        self.assertContains(r, 'Prelúdio')
        self.assertContains(r, 'Ordem do culto')


class PdfIcsTest(BoletimBase):
    def test_pdf_com_campos_vazios(self):
        act = self.criar_actividade(self.hoje, tema='')
        act.versosbiblicos = ''
        act.save()
        Boletim.objects.create(actividade=act, estado=Boletim.ESTADO_PUBLICADO, titulo_en='')
        r = self.client.get(reverse('boletim:pdf', args=[self.hoje.isoformat()]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/pdf')
        self.assertTrue(r.content.startswith(b'%PDF'))

    def test_pdf_completo_com_caracteres_especiais(self):
        b = self.criar_boletim(self.hoje, leitura_referencia='João 3:16', leitura_texto_pt='Porque Deus amou o mundo <de tal> maneira & ...',
                               hino_letra='Linha 1\nLinha 2', notas_sermao='Notas')
        ItemOrdemCulto.objects.create(boletim=b, ordem=1, titulo_pt='Prelúdio', detalhe='Hino 10')
        ProgramaSemanal.objects.create(dia_semana=2, hora_inicio=time(18, 0), titulo_pt='Oração')
        r = self.client.get(reverse('boletim:pdf', args=[self.hoje.isoformat()]) + '?lang=en')
        self.assertEqual(r['Content-Type'], 'application/pdf')
        self.assertTrue(r.content.startswith(b'%PDF'))

    def test_ics_de_anuncio_com_actividade(self):
        act = self.criar_actividade(self.hoje + timedelta(days=5))
        a = Anuncio.objects.create(data=self.hoje, data_inicio=self.hoje, titulo='Retiro, jovens; 2026',
                                   texto='Texto', quemanuncia=self.irmao, publico=True, actividade=act)
        r = self.client.get(reverse('boletim:anuncio_ics', args=[a.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r['Content-Type'].startswith('text/calendar'))
        conteudo = r.content.decode()
        self.assertIn('BEGIN:VEVENT', conteudo)
        self.assertIn('SUMMARY:Retiro\\, jovens\\; 2026', conteudo)
        # 09:00 em Luanda (UTC+1) = 08:00 UTC
        self.assertIn(f"DTSTART:{act.data:%Y%m%d}T080000Z", conteudo)

    def test_ics_indisponivel_sem_actividade_ou_privado(self):
        a = Anuncio.objects.create(data=self.hoje, data_inicio=self.hoje, texto='x',
                                   quemanuncia=self.irmao, publico=True)
        self.assertEqual(self.client.get(reverse('boletim:anuncio_ics', args=[a.pk])).status_code, 404)
        a.actividade = self.criar_actividade(self.hoje)
        a.publico = False
        a.save()
        self.assertEqual(self.client.get(reverse('boletim:anuncio_ics', args=[a.pk])).status_code, 404)


class FormulariosPublicosTest(BoletimBase):
    def setUp(self):
        super().setUp()
        self.secretaria = User.objects.create_user('sec', password='x')
        self.secretaria.groups.add(Group.objects.create(name='Secretaria'))
        self.pastor = User.objects.create_user('pastor', password='x')
        self.pastor.groups.add(Group.objects.create(name='Pastor'))
        self.outro = User.objects.create_user('outro', password='x')

    def dados_visitante(self, **extra):
        dados = {'nome': 'Maria Visitante', 'telefone': '+244 923 456 789', 'email': '',
                 'primeira_vez': 'sim', 'como_soube': 'Amigos', 'consentimento': 'on', 'website': ''}
        dados.update(extra)
        return dados

    def test_normalizar_telefone(self):
        self.assertEqual(normalizar_telefone('+244 923-456-789'), '923456789')
        self.assertEqual(normalizar_telefone('00244923456789'), '923456789')
        self.assertEqual(normalizar_telefone('923 456 789'), '923456789')

    def test_visitante_novo(self):
        r = self.client.post(reverse('boletim:visitante'), self.dados_visitante())
        self.assertRedirects(r, reverse('boletim:visitante') + '?enviado=1')
        v = VisitanteRecorrente.objects.get()
        self.assertEqual(v.telefone, '923456789')
        self.assertEqual(v.numero_visitas, 1)
        self.assertEqual(v.primeira_visita, self.hoje)
        self.assertEqual(v.ultima_visita, self.hoje)
        self.assertIn('Consentimento', v.observacao)
        destinatarios = set(NotificacaoSistema.objects.values_list('destinatario__username', flat=True))
        self.assertEqual(destinatarios, {'sec', 'pastor'})
        self.assertContains(self.client.get(reverse('boletim:visitante') + '?enviado=1'), 'Obrigado pela sua visita')

    def test_visitante_existente_mesmo_telefone(self):
        existente = VisitanteRecorrente.objects.create(
            nome='Maria', telefone='923 456 789', numero_visitas=2,
            primeira_visita=self.hoje - timedelta(days=30), ultima_visita=self.hoje - timedelta(days=7),
        )
        self.client.post(reverse('boletim:visitante'), self.dados_visitante(telefone='00244923456789'))
        self.assertEqual(VisitanteRecorrente.objects.count(), 1)
        existente.refresh_from_db()
        self.assertEqual(existente.numero_visitas, 3)
        self.assertEqual(existente.ultima_visita, self.hoje)
        self.assertEqual(existente.primeira_visita, self.hoje - timedelta(days=30))

    def test_consentimento_obrigatorio(self):
        dados = self.dados_visitante()
        del dados['consentimento']
        r = self.client.post(reverse('boletim:visitante'), dados)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(VisitanteRecorrente.objects.count(), 0)

    def test_honeypot(self):
        r = self.client.post(reverse('boletim:visitante'), self.dados_visitante(website='http://spam'))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(VisitanteRecorrente.objects.count(), 0)
        r = self.client.post(reverse('boletim:oracao'), {'pedido': 'spam', 'website': 'x'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(PedidoOracao.objects.count(), 0)
        self.assertEqual(NotificacaoSistema.objects.count(), 0)

    def test_limite_de_submissoes(self):
        for i in range(5):
            self.client.post(reverse('boletim:visitante'), self.dados_visitante(telefone=f'92345678{i}'))
        self.assertEqual(VisitanteRecorrente.objects.count(), 5)
        r = self.client.post(reverse('boletim:visitante'), self.dados_visitante(telefone='923456789'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Não foi possível processar o seu pedido neste momento')
        self.assertNotContains(r, 'limite')
        self.assertEqual(VisitanteRecorrente.objects.count(), 5)
        # Outro IP continua a poder submeter.
        r = self.client.post(reverse('boletim:visitante'), self.dados_visitante(telefone='923000111'),
                             REMOTE_ADDR='10.0.0.99')
        self.assertEqual(VisitanteRecorrente.objects.count(), 6)

    def test_pedido_oracao(self):
        r = self.client.post(reverse('boletim:oracao'), {'pedido': 'Pela saúde da minha mãe', 'confidencial': 'on'})
        self.assertEqual(r.status_code, 302)
        p = PedidoOracao.objects.get()
        self.assertTrue(p.confidencial)
        self.assertEqual(len(p.ip_hash), 64)
        self.assertNotIn('127.0.0.1', p.ip_hash)
        notifs = NotificacaoSistema.objects.all()
        self.assertEqual({n.destinatario.username for n in notifs}, {'pastor'})
        self.assertNotIn('saúde', notifs[0].mensagem)

    def test_formularios_tem_csrf(self):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        r = c.post(reverse('boletim:oracao'), {'pedido': 'x'})
        self.assertEqual(r.status_code, 403)
        self.assertContains(self.client.get(reverse('boletim:oracao')), 'csrfmiddlewaretoken')


class GestaoTest(BoletimBase):
    def test_sem_permissao_recebe_403(self):
        b = self.criar_boletim(self.hoje)
        p = PedidoOracao.objects.create(pedido='x')
        self.client.force_login(self.utilizador())
        urls = [
            reverse('boletim:gestao_lista'), reverse('boletim:gestao_novo'),
            reverse('boletim:gestao_editar', args=[b.pk]), reverse('boletim:gestao_preview', args=[b.pk]),
            reverse('boletim:gestao_anuncio_novo'),
            reverse('boletim:gestao_oracao_lista'), reverse('boletim:gestao_oracao_detalhe', args=[p.pk]),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 403, url)
        self.assertEqual(self.client.post(reverse('boletim:gestao_publicar', args=[b.pk])).status_code, 403)

    def test_anonimo_redireccionado_para_login(self):
        r = self.client.get(reverse('boletim:gestao_lista'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('login', r['Location'])

    def test_criar_a_partir_de_actividade_e_modelo(self):
        act = self.criar_actividade(self.hoje + timedelta(days=1))
        modelo = ModeloOrdemCulto.objects.create(nome='Culto dominical')
        ItemModeloOrdemCulto.objects.create(modelo=modelo, ordem=1, titulo_pt='Prelúdio', titulo_en='Prelude')
        ItemModeloOrdemCulto.objects.create(modelo=modelo, ordem=2, titulo_pt='Leitura', detalhe='Salmos 29')
        self.client.force_login(self.utilizador('boletim.add_boletim', 'boletim.change_boletim', 'boletim.view_boletim'))
        r = self.client.post(reverse('boletim:gestao_novo'), {'actividade': act.pk, 'modelo': modelo.pk})
        b = Boletim.objects.get(actividade=act)
        self.assertRedirects(r, reverse('boletim:gestao_editar', args=[b.pk]))
        self.assertEqual(b.estado, Boletim.ESTADO_RASCUNHO)
        self.assertEqual(b.leitura_referencia, 'Salmos 29:1-4')
        self.assertEqual(b.hino_referencia, 'Hino 10')
        self.assertEqual(list(b.itens.values_list('titulo_pt', flat=True)), ['Prelúdio', 'Leitura'])
        self.assertEqual(self.client.get(reverse('boletim:gestao_editar', args=[b.pk])).status_code, 200)

    def test_publicar_despublicar_e_preview(self):
        b = self.criar_boletim(self.hoje, estado=Boletim.ESTADO_RASCUNHO)
        self.client.force_login(self.utilizador('boletim.change_boletim', 'boletim.view_boletim'))
        r = self.client.get(reverse('boletim:gestao_preview', args=[b.pk]))
        self.assertContains(r, 'Pré-visualização')
        self.client.post(reverse('boletim:gestao_publicar', args=[b.pk]), {'accao': 'publicar'})
        b.refresh_from_db()
        self.assertEqual(b.estado, Boletim.ESTADO_PUBLICADO)
        self.assertIsNotNone(b.publicado_em)
        self.assertEqual(self.client.get(self.url_data(self.hoje)).status_code, 200)
        self.client.post(reverse('boletim:gestao_publicar', args=[b.pk]), {'accao': 'despublicar'})
        self.assertEqual(self.client.get(self.url_data(self.hoje)).status_code, 404)

    def test_editar_itens_e_mensagem_whatsapp(self):
        b = self.criar_boletim(self.hoje)
        f = Funcao.objects.create(designacao='Pregador')
        FuncaoBoletim.objects.create(funcao=f, rotulo_pt='Pregador')
        Escala.objects.create(irmao=self.irmao, actividade=b.actividade, funcao=f)
        item = ItemOrdemCulto.objects.create(boletim=b, ordem=1, titulo_pt='Antigo')
        self.client.force_login(self.utilizador('boletim.change_boletim', 'boletim.view_boletim'))
        url = reverse('boletim:gestao_editar', args=[b.pk])
        r = self.client.get(url)
        self.assertContains(r, 'Pregador: Joaquim Sebastião')
        self.assertContains(r, 'Tema: A fé que vence')
        self.assertContains(r, self.url_data(self.hoje))
        dados = {
            'titulo_pt': 'Ordem do Culto', 'titulo_en': 'Order of Service',
            'itens-TOTAL_FORMS': '3', 'itens-INITIAL_FORMS': '1', 'itens-MIN_NUM_FORMS': '0', 'itens-MAX_NUM_FORMS': '1000',
            'itens-0-id': item.pk, 'itens-0-boletim': b.pk, 'itens-0-ordem': '5', 'itens-0-titulo_pt': 'Antigo', 'itens-0-DELETE': 'on',
            'itens-1-ordem': '2', 'itens-1-titulo_pt': 'Bênção', 'itens-1-boletim': b.pk,
            'itens-2-ordem': '1', 'itens-2-titulo_pt': 'Prelúdio', 'itens-2-boletim': b.pk,
        }
        r = self.client.post(url, dados)
        self.assertRedirects(r, url)
        self.assertEqual(list(b.itens.values_list('titulo_pt', flat=True)), ['Prelúdio', 'Bênção'])

    def test_anuncio_criado_na_gestao(self):
        b = self.criar_boletim(self.hoje)
        self.irmao.user = self.utilizador('sitetibl.add_anuncio', 'boletim.view_boletim')
        self.irmao.save()
        self.client.force_login(self.irmao.user)
        r = self.client.post(reverse('boletim:gestao_anuncio_novo') + f'?voltar={b.pk}', {
            'titulo': 'Baptismos', 'texto': 'Domingo que vem', 'data_inicio': self.hoje.isoformat(),
            'publico': 'on', 'ordem': '0', 'quemanuncia': self.irmao.pk,
        })
        self.assertRedirects(r, reverse('boletim:gestao_editar', args=[b.pk]), fetch_redirect_response=False)
        a = Anuncio.objects.get(titulo='Baptismos')
        self.assertEqual(a.data, self.hoje)
        self.assertContains(self.client.get(self.url_data(self.hoje)), 'Baptismos')

    def test_converter_pedido_em_caso_pastoral(self):
        p = PedidoOracao.objects.create(pedido='Oração pela família', confidencial=False)
        u = self.utilizador('boletim.view_pedidooracao', 'boletim.change_pedidooracao', 'sitetibl.add_casopastoral')
        self.client.force_login(u)
        url = reverse('boletim:gestao_oracao_detalhe', args=[p.pk])
        self.assertContains(self.client.get(url), 'Converter em caso pastoral')
        p.refresh_from_db()
        self.assertEqual(p.estado, 'lido')
        r = self.client.post(url, {'accao': 'converter', 'membro': self.irmao.pk, 'tipo': 'aconselhamento',
                                   'prioridade': 'normal', 'titulo': 'Pedido de oração'})
        self.assertRedirects(r, url)
        p.refresh_from_db()
        caso = CasoPastoral.objects.get()
        self.assertEqual(p.estado, 'convertido')
        self.assertEqual(p.caso_pastoral, caso)
        self.assertTrue(caso.confidencial)
        self.assertEqual(caso.membro, self.irmao)

    def test_sem_permissao_de_caso_nao_converte(self):
        p = PedidoOracao.objects.create(pedido='x')
        self.client.force_login(self.utilizador('boletim.view_pedidooracao', 'boletim.change_pedidooracao'))
        url = reverse('boletim:gestao_oracao_detalhe', args=[p.pk])
        self.assertNotContains(self.client.get(url), 'Converter em caso pastoral')
        r = self.client.post(url, {'accao': 'converter', 'membro': self.irmao.pk, 'tipo': 'outro',
                                   'prioridade': 'normal', 'titulo': 't'})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(CasoPastoral.objects.count(), 0)

    def test_menu_lateral_por_permissao(self):
        self.client.force_login(self.utilizador('boletim.view_boletim'))
        r = self.client.get(reverse('boletim:gestao_lista'))
        self.assertContains(r, reverse('boletim:gestao_lista'))
        self.assertNotContains(r, reverse('boletim:gestao_oracao_lista'))


class SeederPermissoesTest(TestCase):
    def test_matriz_de_permissoes(self):
        from sitetibl.management.commands.seed_base_data import Command
        cmd = Command(stdout=StringIO())
        cmd.seed_groups()

        def perms(grupo):
            return set(Group.objects.get(name=grupo).permissions
                       .filter(content_type__app_label='boletim').values_list('codename', flat=True))

        todas = set(Permission.objects.filter(content_type__app_label='boletim').values_list('codename', flat=True))
        self.assertEqual(perms('Administrador'), todas)
        self.assertEqual(perms('Pastor'), todas)
        sec = perms('Secretaria')
        self.assertIn('change_boletim', sec)
        self.assertIn('change_configuracaoboletim', sec)
        self.assertFalse({p for p in sec if p.endswith('_pedidooracao')})
        for grupo in ('Financeiro', 'Líder de Departamento', 'Vice-Líder de Departamento',
                      'Líder de Célula', 'Membros Baptizados', 'Membro Geral', 'Secretário Geral'):
            self.assertEqual(perms(grupo), set(), grupo)
