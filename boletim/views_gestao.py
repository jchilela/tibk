"""Gestão interna do boletim (com login), integrada no base_modern.html."""
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from boletim import services
from boletim.forms import AnuncioForm, BoletimForm, ConverterPedidoForm, ItensFormSet, NovoBoletimForm
from boletim.models import Boletim, ItemOrdemCulto, PedidoOracao
from boletim.textos import lingua_do_pedido
from boletim.views_publicas import render_boletim
from sitetibl.models import Anuncio, CasoPastoral, Irmao


def _exigir(request, *perms):
    if not all(request.user.has_perm(p) for p in perms):
        raise PermissionDenied


def _data(valor):
    try:
        return datetime.strptime(valor, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


# ── Boletins ─────────────────────────────────────────────────

@login_required
def lista(request):
    _exigir(request, 'boletim.view_boletim')
    qs = Boletim.objects.select_related('actividade', 'actividade__designacao')
    estado = request.GET.get('estado', '')
    if estado in dict(Boletim.ESTADO_CHOICES):
        qs = qs.filter(estado=estado)
    de, ate = _data(request.GET.get('de')), _data(request.GET.get('ate'))
    if de:
        qs = qs.filter(actividade__data__gte=de)
    if ate:
        qs = qs.filter(actividade__data__lte=ate)
    pagina = Paginator(qs.order_by('-actividade__data', '-actividade__inicio'), 20).get_page(request.GET.get('pagina'))
    return render(request, 'boletim/gestao/lista.html', {
        'pagina': pagina,
        'estados': Boletim.ESTADO_CHOICES,
        'filtro_estado': estado,
        'filtro_de': request.GET.get('de', ''),
        'filtro_ate': request.GET.get('ate', ''),
    })


@login_required
def novo(request):
    _exigir(request, 'boletim.add_boletim')
    form = NovoBoletimForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        act = form.cleaned_data['actividade']
        modelo = form.cleaned_data['modelo']
        with transaction.atomic():
            boletim = Boletim.objects.create(
                actividade=act,
                leitura_referencia=act.versosbiblicos,
                hino_referencia=act.hinos,
                criado_por=request.user,
            )
            if modelo:
                ItemOrdemCulto.objects.bulk_create([
                    ItemOrdemCulto(boletim=boletim, ordem=i.ordem, titulo_pt=i.titulo_pt,
                                   titulo_en=i.titulo_en, detalhe=i.detalhe)
                    for i in modelo.itens.all()
                ])
        messages.success(request, 'Boletim criado em rascunho. Reveja os dados e publique quando estiver pronto.')
        return redirect('boletim:gestao_editar', pk=boletim.pk)
    return render(request, 'boletim/gestao/novo.html', {'form': form})


@login_required
def editar(request, pk):
    _exigir(request, 'boletim.change_boletim')
    boletim = get_object_or_404(Boletim.objects.select_related('actividade', 'actividade__designacao'), pk=pk)
    form = BoletimForm(request.POST or None, instance=boletim)
    formset = ItensFormSet(request.POST or None, instance=boletim, prefix='itens')
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Boletim gravado.')
            return redirect('boletim:gestao_editar', pk=boletim.pk)
        messages.error(request, 'Há erros no formulário. Verifique os campos assinalados.')

    data = boletim.actividade.data
    # Todos os anúncios do período (públicos ou não), para rever e editar.
    anuncios = Anuncio.objects.filter(
        Q(data_inicio__lte=data, data_fim__gte=data) | Q(data_fim__isnull=True, data_inicio=data))
    url_publico = request.build_absolute_uri(reverse('boletim:data', args=[data.isoformat()]))
    if Boletim.objects.filter(actividade__data=data).exclude(pk=boletim.pk).exists():
        url_publico += f'?culto={boletim.pk}'
    return render(request, 'boletim/gestao/editar.html', {
        'boletim': boletim,
        'form': form,
        'formset': formset,
        'anuncios': anuncios.order_by('ordem', 'id'),
        'url_publico': url_publico,
        'mensagem_whatsapp': services.mensagem_whatsapp(boletim, url_publico),
        'escalas': services.escalas_do_boletim(boletim.actividade, 'pt'),
    })


@login_required
def pre_visualizar(request, pk):
    _exigir(request, 'boletim.view_boletim')
    boletim = get_object_or_404(Boletim.objects.select_related('actividade', 'actividade__designacao'), pk=pk)
    lingua, _ = lingua_do_pedido(request)
    html = render_boletim(request, boletim, lingua, pre_visualizacao=True)
    resp = HttpResponse(html)
    resp['Cache-Control'] = 'no-store'
    resp['X-Robots-Tag'] = 'noindex'
    return resp


@login_required
@require_POST
def publicar(request, pk):
    _exigir(request, 'boletim.change_boletim')
    boletim = get_object_or_404(Boletim, pk=pk)
    if request.POST.get('accao') == 'despublicar':
        boletim.estado = Boletim.ESTADO_RASCUNHO
        messages.success(request, 'Boletim despublicado: deixou de estar visível na página pública.')
    else:
        boletim.estado = Boletim.ESTADO_PUBLICADO
        boletim.publicado_em = timezone.now()
        messages.success(request, 'Boletim publicado.')
    boletim.save(update_fields=['estado', 'publicado_em', 'actualizado_em'])
    return redirect('boletim:gestao_editar', pk=boletim.pk)


# ── Anúncios ─────────────────────────────────────────────────

def _form_anuncio(request, anuncio):
    form = AnuncioForm(request.POST or None, instance=anuncio)
    voltar = request.GET.get('voltar', '')
    voltar = voltar if voltar.isdigit() else ''
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Anúncio gravado.')
        if voltar:
            return redirect('boletim:gestao_editar', pk=int(voltar))
        return redirect('boletim:gestao_lista')
    return render(request, 'boletim/gestao/anuncio.html', {
        'form': form, 'anuncio': anuncio, 'voltar': voltar,
    })


@login_required
def anuncio_novo(request):
    _exigir(request, 'sitetibl.add_anuncio')
    anuncio = Anuncio(publico=True)
    inicio = _data(request.GET.get('data'))
    if inicio:
        anuncio.data_inicio = inicio
    irmao = Irmao.objects.filter(user=request.user).first()
    if irmao:
        anuncio.quemanuncia = irmao
    return _form_anuncio(request, anuncio)


@login_required
def anuncio_editar(request, pk):
    _exigir(request, 'sitetibl.change_anuncio')
    return _form_anuncio(request, get_object_or_404(Anuncio, pk=pk))


# ── Pedidos de oração ────────────────────────────────────────

@login_required
def oracao_lista(request):
    _exigir(request, 'boletim.view_pedidooracao')
    qs = PedidoOracao.objects.all()
    estado = request.GET.get('estado', '')
    if estado in dict(PedidoOracao.ESTADO_CHOICES):
        qs = qs.filter(estado=estado)
    pagina = Paginator(qs, 25).get_page(request.GET.get('pagina'))
    return render(request, 'boletim/gestao/oracao_lista.html', {
        'pagina': pagina, 'estados': PedidoOracao.ESTADO_CHOICES, 'filtro_estado': estado,
    })


@login_required
def oracao_detalhe(request, pk):
    _exigir(request, 'boletim.view_pedidooracao')
    pedido = get_object_or_404(PedidoOracao.objects.select_related('caso_pastoral'), pk=pk)
    pode_alterar = request.user.has_perm('boletim.change_pedidooracao')
    pode_converter = pode_alterar and request.user.has_perm('sitetibl.add_casopastoral') and not pedido.caso_pastoral_id

    if pedido.estado == 'novo' and pode_alterar and request.method == 'GET':
        pedido.estado = 'lido'
        pedido.save(update_fields=['estado'])

    form = ConverterPedidoForm(request.POST or None) if pode_converter else None

    if request.method == 'POST':
        accao = request.POST.get('accao')
        if accao == 'converter':
            if not pode_converter:
                raise PermissionDenied
            if form.is_valid():
                with transaction.atomic():
                    caso = CasoPastoral.objects.create(
                        membro=form.cleaned_data['membro'],
                        tipo=form.cleaned_data['tipo'],
                        prioridade=form.cleaned_data['prioridade'],
                        titulo=form.cleaned_data['titulo'],
                        descricao=pedido.pedido,
                        confidencial=True,
                        criado_por=Irmao.objects.filter(user=request.user).first(),
                    )
                    pedido.caso_pastoral = caso
                    pedido.estado = 'convertido'
                    pedido.save(update_fields=['caso_pastoral', 'estado'])
                messages.success(request, 'Caso pastoral criado (confidencial).')
                return redirect('boletim:gestao_oracao_detalhe', pk=pedido.pk)
        elif accao in ('arquivar', 'reabrir'):
            if not pode_alterar:
                raise PermissionDenied
            pedido.estado = 'arquivado' if accao == 'arquivar' else 'lido'
            pedido.save(update_fields=['estado'])
            messages.success(request, 'Pedido actualizado.')
            return redirect('boletim:gestao_oracao_detalhe', pk=pedido.pk)
        else:
            raise PermissionDenied

    return render(request, 'boletim/gestao/oracao_detalhe.html', {
        'pedido': pedido, 'form': form,
        'pode_alterar': pode_alterar, 'pode_converter': pode_converter,
    })
