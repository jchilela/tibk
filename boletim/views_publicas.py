"""Páginas públicas do boletim (sem login).

Regras:
- só se expõem os dados preparados em ``services.contexto_boletim`` e
  ``services.configuracao_publica`` (dicionários simples);
- as páginas do boletim, o arquivo e o PDF ficam 5 minutos na cache do
  Django e são invalidados por signals (ver ``boletim/signals.py``);
- os formulários nunca vão para a cache (têm token CSRF).
"""
from datetime import date

from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.cache import patch_cache_control, patch_vary_headers
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from boletim import cache as boletim_cache
from boletim import services
from boletim.forms import CartaoVisitanteForm, PedidoOracaoForm
from boletim.ics import gerar_ics
from boletim.models import PedidoOracao
from boletim.pdf import gerar_pdf
from boletim.textos import TEXTOS, data_extenso, gravar_cookie_lingua, lingua_do_pedido, tr
from sitetibl.models import Anuncio


# ── Utilitários ──────────────────────────────────────────────

def _finalizar(response, lingua, mudou, publico=True):
    patch_vary_headers(response, ['Cookie'])
    if publico:
        patch_cache_control(response, max_age=60)
    if mudou:
        gravar_cookie_lingua(response, lingua)
    return response


def _url_lingua(request, lingua_destino):
    # Só se mantêm os parâmetros conhecidos: o link vai para a cache e não
    # deve arrastar parâmetros arbitrários (fbclid, utm_*, ...).
    params = QueryDict(mutable=True)
    for nome in ('culto', 'pagina'):
        valor = request.GET.get(nome, '')
        if valor.isdigit():
            params[nome] = valor
    params['lang'] = lingua_destino
    return f'{request.path}?{params.urlencode()}'


def _escolher_culto(boletins, culto):
    if culto and culto.isdigit():
        for b in boletins:
            if b.id == int(culto):
                return b
    return boletins[0]


def render_boletim(request, boletim, lingua, outros=(), pre_visualizacao=False):
    """HTML completo da página do boletim (usado também na pré-visualização)."""
    t = TEXTOS[lingua]
    cfg = services.configuracao_publica(lingua)
    b = services.contexto_boletim(boletim, lingua)
    url_data = reverse('boletim:data', args=[b['data_iso']])
    sufixo_culto = f'?culto={boletim.id}' if outros else ''
    descricao = cfg['nome_igreja']
    if b['tema']:
        descricao = f"{t['tema']}: {b['tema']} · {descricao}"
    contexto = {
        't': t,
        'lingua': lingua,
        'cfg': cfg,
        'b': b,
        'pre_visualizacao': pre_visualizacao,
        'outros': [
            {'url': f"{url_data}?culto={o.id}",
             'rotulo': f"{o.actividade.inicio:%Hh%M} — {tr(lingua, o.titulo_pt, o.titulo_en)}"}
            for o in outros
        ],
        'og_titulo': f"{b['titulo']} — {b['data_extenso']}",
        'og_descricao': descricao,
        'og_url': request.build_absolute_uri(url_data + sufixo_culto),
        'url_pdf': reverse('boletim:pdf', args=[b['data_iso']]) + sufixo_culto,
        'url_lingua': _url_lingua(request, t['outra_lingua']),
    }
    return render_to_string('boletim/boletim.html', contexto)


def _pagina_cacheada(request, partes, gerar):
    lingua, mudou = lingua_do_pedido(request)
    partes = tuple(partes) + (lingua, request.get_host())
    html = boletim_cache.obter(*partes)
    if html is None:
        html = gerar(lingua)
        boletim_cache.guardar(html, *partes)
    return _finalizar(HttpResponse(html), lingua, mudou)


# ── Boletim ──────────────────────────────────────────────────

@require_GET
def boletim_actual(request):
    hoje = date.today()

    def gerar(lingua):
        boletim = services.boletim_actual(hoje)
        if boletim is None:
            t = TEXTOS[lingua]
            return render_to_string('boletim/vazio.html', {
                't': t, 'lingua': lingua, 'cfg': services.configuracao_publica(lingua),
                'url_lingua': _url_lingua(request, t['outra_lingua']),
            })
        do_dia = services.boletins_da_data(boletim.actividade.data)
        outros = [o for o in do_dia if o.id != boletim.id]
        return render_boletim(request, boletim, lingua, outros)

    return _pagina_cacheada(request, ('actual', hoje.isoformat()), gerar)


@require_GET
def boletim_por_data(request, data):
    boletins = services.boletins_da_data(data)
    if not boletins:
        raise Http404('Boletim não encontrado.')
    escolhido = _escolher_culto(boletins, request.GET.get('culto'))
    outros = [o for o in boletins if o.id != escolhido.id]
    return _pagina_cacheada(
        request, ('data', escolhido.id),
        lambda lingua: render_boletim(request, escolhido, lingua, outros),
    )


@require_GET
def boletim_pdf(request, data):
    boletins = services.boletins_da_data(data)
    if not boletins:
        raise Http404('Boletim não encontrado.')
    escolhido = _escolher_culto(boletins, request.GET.get('culto'))
    lingua, mudou = lingua_do_pedido(request)
    conteudo = boletim_cache.obter('pdf', escolhido.id, lingua)
    if conteudo is None:
        conteudo = gerar_pdf(
            services.contexto_boletim(escolhido, lingua),
            services.configuracao_publica(lingua),
            lingua,
        )
        boletim_cache.guardar(conteudo, 'pdf', escolhido.id, lingua)
    resp = HttpResponse(conteudo, content_type='application/pdf')
    resp['Content-Disposition'] = f'inline; filename="boletim-{data.isoformat()}.pdf"'
    return _finalizar(resp, lingua, mudou)


@require_GET
def anuncio_ics(request, pk):
    anuncio = get_object_or_404(
        Anuncio.objects.select_related('actividade', 'actividade__designacao', 'actividade__localactividade'),
        pk=pk, publico=True, actividade__isnull=False,
    )
    lingua, mudou = lingua_do_pedido(request)
    conteudo = gerar_ics(
        anuncio,
        tr(lingua, anuncio.titulo, anuncio.titulo_en),
        tr(lingua, anuncio.texto, anuncio.texto_en),
        request.get_host().split(':')[0] or 'tibl.ao',
    )
    resp = HttpResponse(conteudo, content_type='text/calendar; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="anuncio-{anuncio.pk}.ics"'
    return _finalizar(resp, lingua, mudou)


@require_GET
def arquivo(request):
    pagina = request.GET.get('pagina') or '1'
    pagina = pagina if pagina.isdigit() else '1'

    def gerar(lingua):
        t = TEXTOS[lingua]
        qs = services.boletins_publicados().order_by('-actividade__data', '-actividade__inicio', '-id')
        pag = Paginator(qs, 20).get_page(pagina)
        itens = [{
            'url': reverse('boletim:data', args=[b.actividade.data.isoformat()]) + f'?culto={b.id}',
            'data_extenso': data_extenso(b.actividade.data, lingua),
            'titulo': tr(lingua, b.titulo_pt, b.titulo_en),
            'tema': b.actividade.tema,
            'gravacao': b.link_gravacao,
        } for b in pag.object_list]
        return render_to_string('boletim/arquivo.html', {
            't': t, 'lingua': lingua, 'cfg': services.configuracao_publica(lingua),
            'itens': itens, 'pag': pag,
            'url_lingua': _url_lingua(request, t['outra_lingua']),
        })

    return _pagina_cacheada(request, ('arquivo', pagina), gerar)


# ── Formulários ──────────────────────────────────────────────

def _formulario_publico(request, *, nome, form_class, template, ao_gravar, chave_obrigado):
    lingua, mudou = lingua_do_pedido(request)
    t = TEXTOS[lingua]
    contexto = {
        't': t, 'lingua': lingua, 'cfg': services.configuracao_publica(lingua),
        'url_lingua': _url_lingua(request, t['outra_lingua']),
    }

    if request.method == 'GET' and request.GET.get('enviado') == '1':
        contexto['mensagem'] = t[chave_obrigado]
        return _finalizar(render(request, 'boletim/obrigado.html', contexto), lingua, mudou, publico=False)

    if request.method == 'POST':
        ip_h = services.hash_ip(services.ip_cliente(request))
        if services.limite_excedido(nome, ip_h):
            contexto['erro'] = t['erro_neutro']
            form = form_class(lingua=lingua)
        else:
            form = form_class(request.POST, lingua=lingua)
            if form.is_robot():
                # Resposta igual à de sucesso, sem gravar nada.
                services.contar_submissao(nome, ip_h)
                return redirect(request.path + '?enviado=1')
            if form.is_valid():
                ao_gravar(form.cleaned_data, ip_h)
                services.contar_submissao(nome, ip_h)
                return redirect(request.path + '?enviado=1')
    else:
        form = form_class(lingua=lingua)

    contexto['form'] = form
    return _finalizar(render(request, template, contexto), lingua, mudou, publico=False)


@never_cache
@require_http_methods(['GET', 'POST'])
def visitante(request):
    def gravar(dados, ip_h):
        v, criado = services.registar_visitante(dados)
        estado = 'primeira visita registada' if criado else f'visita n.º {v.numero_visitas}'
        services.notificar_grupos(
            ['Secretaria', 'Pastor'],
            'Novo cartão de visitante',
            f'{v.nome} preencheu o cartão de visitante no boletim digital ({estado}).',
            url=reverse('sitetibl:mostra_gestao', args=['visitantes', 1]),
        )

    return _formulario_publico(
        request, nome='visitante', form_class=CartaoVisitanteForm,
        template='boletim/visitante.html', ao_gravar=gravar, chave_obrigado='obrigado_visitante',
    )


@never_cache
@require_http_methods(['GET', 'POST'])
def oracao(request):
    def gravar(dados, ip_h):
        pedido = PedidoOracao.objects.create(
            nome=dados.get('nome', '').strip(),
            contacto=dados.get('contacto', '').strip(),
            pedido=dados['pedido'].strip(),
            confidencial=bool(dados.get('confidencial')),
            ip_hash=ip_h,
        )
        # O conteúdo do pedido nunca vai na notificação.
        services.notificar_grupos(
            ['Pastor'],
            'Novo pedido de oração',
            'Foi recebido um novo pedido de oração através do boletim digital.',
            url=reverse('boletim:gestao_oracao_detalhe', args=[pedido.pk]),
        )

    return _formulario_publico(
        request, nome='oracao', form_class=PedidoOracaoForm,
        template='boletim/oracao.html', ao_gravar=gravar, chave_obrigado='obrigado_oracao',
    )
