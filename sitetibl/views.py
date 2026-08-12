# Create your views here.
from django.contrib import admin, messages
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaulttags import register
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from datetime import date
from django import forms
from django.urls import reverse
from django.template import loader
from django.db.models import Sum, Count, F, Q, Case, When, Value, IntegerField
from django.db import IntegrityError, connection, transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import permission_required
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from django.conf import settings
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, LongTable
from reportlab.lib import colors
import os
from django.contrib.auth.decorators import login_required

from django.db.models.functions import TruncMonth, ExtractDay
import json
from django.http import JsonResponse
from django.utils.timezone import now
from .signals import notificar_mudanca_estado_pedido, _atribuir_grupos_irmao, enviar_credenciais
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from collections import OrderedDict
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging
logger = logging.getLogger(__name__)
from sitetibl.sms import enviar_sms
from django.db.models.functions import ExtractWeekDay
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import mimetypes
from pathlib import Path
from django.http import FileResponse, Http404

#from django.db.models import Count

# Register your models here.
#from gestaoinfra.models import Contacto
from sitetibl.models import Irmao
from sitetibl.models import Municipio
from sitetibl.models import TipoOferta
from sitetibl.models import Ajuda
from sitetibl.models import Cestabasica
from sitetibl.models import Banco
from sitetibl.models import Contabancaria
from sitetibl.models import Actividade
from sitetibl.models import Departamento
from sitetibl.models import ComposicaoCesta
from sitetibl.models import Funcao
from sitetibl.models import Listaactividades
from sitetibl.models import Mandato
from sitetibl.models import Escala
from sitetibl.models import Rubricaentrada
from sitetibl.models import Rubricasaida
from sitetibl.models import Entrada
from sitetibl.models import Saida
from sitetibl.models import Dizimooferta
from sitetibl.models import Pagamentoservico
from sitetibl.models import Gruporubrica
from sitetibl.models import Servico
from sitetibl.models import Tipoajuda
from sitetibl.models import RelatorioSemanalCelula
from sitetibl.models import PedidoSaida
from sitetibl.models import Status_Aprovacao
from sitetibl.models import Anuncio
from sitetibl.models import SolicitacaoInterdepartamental
from sitetibl.models import HistoricoSolicitacao
from sitetibl.models import ComentarioSolicitacao
from sitetibl.models import NotificacaoSistema
from sitetibl.models import CasoPastoral
from sitetibl.models import RegistoAcompanhamento
from sitetibl.models import AlertaPastoral
from sitetibl.models import VisitanteRecorrente
from sitetibl.models import Celula
from sitetibl.forms import OrcamentoDepartamento
from sitetibl.forms import InventarioPatrimonio
from sitetibl.forms import ConteudoEnsino
from sitetibl.forms import EnvioMensagem

from sitetibl.serializers import EscalaSerializer

from sitetibl.forms import IrmaoForm
from sitetibl.forms import AjudaForm
from sitetibl.forms import CestabasicaForm
from sitetibl.forms import BancoForm
from sitetibl.forms import ContabancariaForm
from sitetibl.forms import ActividadeForm
from sitetibl.forms import DepartamentoForm
from sitetibl.forms import MandatoForm
from sitetibl.forms import EscalaForm
from sitetibl.forms import EntradaForm
from sitetibl.forms import SaidaForm
from sitetibl.forms import DizimoofertaForm
from sitetibl.forms import PagamentoservicoForm
from sitetibl.forms import GruporubricaForm
from sitetibl.forms import ServicoForm
from sitetibl.forms import RelatorioSemanalCelulaForm
from sitetibl.forms import CelulaForm
from sitetibl.forms import PedidoSaidaForm
from sitetibl.forms import PedidoSaidaUpdateForm
from sitetibl.forms import OrcamentoDepartamentoForm
from sitetibl.forms import InventarioPatrimonioForm
from sitetibl.forms import ConteudoEnsinoForm
from sitetibl.forms import EnvioMensagemForm
from sitetibl.forms import MeuPerfilForm, MeuPerfilPasswordForm
from sitetibl.forms import ActividadesRecorrentesForm
from sitetibl.forms import SolicitacaoForm, SolicitacaoUpdateForm
from sitetibl.forms import CasoPastoralForm, CasoPastoralUpdateForm
from sitetibl.forms import RegistoAcompanhamentoForm
from sitetibl.forms import VisitanteRecorrenteForm
from django.contrib.auth import update_session_auth_hash
from datetime import timedelta

PROVINCIAS = {'BNG':'Bengo','BGL':'Benguela','BIE':'Bié','CAB':'Cabinda','CNE':'Cunene','HMB':'Huambo','HLA':'Huila','KKG':'Kuando kubango','KZN':'Kwanza Norte','KZS':'Kwanza Sul','LDA':'Luanda','LDN':'Lunda Norte','LDS':'Lunda Sul','MLG':'Malange','MXC':'Moxico','NMB':'Namibe','UGE':'Uige','ZAR':'Zaire'}

MOEDA = {'AKZ':'Kwanza','USD':'USA Dólar','EU':'Euro','R':'Reais','RAN':'ZA Rands','NAMD':'Dólar Namibiano', 'LB':'Libra Inglesa'}


def _sincronizar_status_legado_pedidosaida(pedido):
    """Mantém o FK legado status_de_aprovacao coerente com o novo campo estado."""
    mapa = {
        'pendente': 'Em analise',
        'em_analise': 'Em analise',
        'aprovado': 'Aprovado',
        'rejeitado': 'Rejeitado',
    }
    designacao = mapa.get(pedido.estado)
    if not designacao:
        return

    status = Status_Aprovacao.objects.filter(designacao__iexact=designacao).first()
    if status and pedido.status_de_aprovacao_id != status.id:
        pedido.status_de_aprovacao = status
MESES = {'1':'Janeiro','2':'Fevereiro','3':'Março','4':'Abril','5':'Maio','6':'Junho','7':'Julho','8':'Agosto','9':'Setembro','10':'Outubro','11':'Novembro','12':'Dezembro'}
TIPO = {'1':'Saude','2':'Falecimento','3':'Propina','4':'Cesta básica','5':'Casamento','6':'Outra'}


def _irmaos_envolvidos_solicitacao(solicitacao, excluir=None):
    """Recolhe irmãos envolvidos numa solicitação (solicitante + líderes dos deptos)."""
    irmaos = []
    vistos = set()

    def _add(irmao):
        if not irmao or irmao.pk in vistos:
            return
        if excluir and irmao.pk == excluir.pk:
            return
        vistos.add(irmao.pk)
        irmaos.append(irmao)

    _add(solicitacao.solicitante)
    for dept in (solicitacao.departamento_destinatario, solicitacao.departamento_solicitante):
        if dept:
            _add(dept.lider_departamento)
            _add(dept.vice_lider_departamento)
    return irmaos


def _contactos_de_irmaos(irmaos):
    """Resolve emails (Irmao.email com fallback User.email) e telefones."""
    emails = []
    telefones = []
    for irmao in irmaos:
        email = (irmao.email or '').strip()
        if not email and irmao.user_id:
            email = (irmao.user.email or '').strip()
        if email and email not in emails:
            emails.append(email)
        tel = (irmao.telefone or '').strip()
        if tel and tel not in telefones:
            telefones.append(tel)
    return emails, telefones


def _enviar_sms(telefones, mensagem):
    """Envia SMS (via StrongX) para uma lista de telefones. Retorna True se bem-sucedido."""
    return enviar_sms(telefones, mensagem)


def _notificar_solicitacao(solicitacao, estado_anterior, estado_novo, responsavel, apenas_externo=False):
    """Cria NotificacaoSistema e envia email/SMS para os envolvidos na mudança de estado."""
    ESTADO_LABELS = dict(SolicitacaoInterdepartamental.ESTADO_CHOICES)
    label_novo = ESTADO_LABELS.get(estado_novo, estado_novo)
    label_anterior = ESTADO_LABELS.get(estado_anterior, estado_anterior) if estado_anterior else ''
    url = reverse('sitetibl:mostra_detalhe', args=['solicitacoes', solicitacao.id])
    titulo = f'Solicitação #{solicitacao.id} — {label_novo}'
    if estado_anterior:
        mensagem = f'A solicitação "{solicitacao.assunto}" mudou de estado de {label_anterior} para {label_novo}.'
    else:
        mensagem = f'Foi criada uma nova solicitação "{solicitacao.assunto}" — {label_novo}.'

    irmaos = _irmaos_envolvidos_solicitacao(solicitacao, excluir=responsavel)
    destinatarios = {irmao.user_id for irmao in irmaos if irmao.user_id}

    if not apenas_externo:
        notifs = [
            NotificacaoSistema(destinatario_id=uid, titulo=titulo, mensagem=mensagem, url=url)
            for uid in destinatarios
        ]
        if notifs:
            NotificacaoSistema.objects.bulk_create(notifs)

    _enviar_mensagens_solicitacao(
        solicitacao, estado_anterior, estado_novo, label_anterior, label_novo,
        responsavel, irmaos, titulo_override=titulo, mensagem_override=mensagem,
    )


def _enviar_mensagens_solicitacao(
    solicitacao, estado_anterior, estado_novo, label_anterior, label_novo,
    responsavel, irmaos, titulo_override=None, mensagem_override=None,
):
    """Envia email HTML e SMS aos envolvidos numa solicitação."""
    if not irmaos:
        return

    emails_to, telefones = _contactos_de_irmaos(irmaos)
    if not emails_to and not telefones:
        logger.warning(
            'Solicitação #%s: nenhum email ou telefone encontrado para os destinatários.',
            solicitacao.id,
        )
        return

    resp_nome = f'{responsavel.nome} {responsavel.apelido}' if responsavel else ''
    if mensagem_override:
        msg_texto = mensagem_override
    elif label_anterior:
        msg_texto = f'A solicitação "{solicitacao.assunto}" mudou de estado de {label_anterior} para {label_novo}.'
    else:
        msg_texto = f'Foi criada uma nova solicitação "{solicitacao.assunto}" — {label_novo}.'

    titulo = titulo_override or f'Solicitação #{solicitacao.id} — {label_novo}'
    context = {
        'titulo': titulo,
        'mensagem': msg_texto,
        'novo_estado': estado_novo,
        'estado_display': label_novo,
        'assunto': solicitacao.assunto,
        'categoria': solicitacao.get_categoria_display(),
        'dept_solicitante': str(solicitacao.departamento_solicitante),
        'dept_destinatario': str(solicitacao.departamento_destinatario),
        'prioridade': solicitacao.get_prioridade_display(),
        'data_necessidade': solicitacao.data_necessidade.strftime('%d/%m/%Y') if solicitacao.data_necessidade else '',
        'observacao': solicitacao.justificacao_resposta or '',
        'responsavel': resp_nome,
    }

    if emails_to:
        try:
            html_content = render_to_string('emails/email_solicitacao_estado.html', context)
            from_email = settings.EMAIL_HOST_USER or None
            for email_addr in emails_to:
                msg = EmailMultiAlternatives(
                    subject=titulo,
                    body=msg_texto,
                    from_email=from_email,
                    to=[email_addr],
                )
                msg.attach_alternative(html_content, 'text/html')
                msg.send()
            logger.info('Emails de solicitação #%s enviados para %s', solicitacao.id, emails_to)
        except Exception as e:
            logger.error('Falha ao enviar emails de solicitação #%s: %s', solicitacao.id, e)

    if telefones:
        sms_texto = f'TIBL — {titulo}. {msg_texto}'
        _enviar_sms(telefones, sms_texto)
        logger.info('SMS de solicitação #%s enviados para %s', solicitacao.id, telefones)


def _enviar_email_solicitacao(solicitacao, estado_anterior, estado_novo, label_anterior, label_novo, responsavel, user_ids):
    """Compatibilidade: delega para _enviar_mensagens_solicitacao."""
    irmaos = [
        irmao for irmao in Irmao.objects.filter(user_id__in=user_ids).select_related('user')
    ]
    _enviar_mensagens_solicitacao(
        solicitacao, estado_anterior, estado_novo, label_anterior, label_novo,
        responsavel, irmaos,
    )


def _notificar_comentario_solicitacao(solicitacao, autor, texto):
    """Cria notificação in-app e envia email/SMS quando alguém comenta numa solicitação."""
    url = reverse('sitetibl:mostra_detalhe', args=['solicitacoes', solicitacao.id])
    titulo = f'Novo comentário — Solicitação #{solicitacao.id}'
    mensagem = f'{autor.nome} {autor.apelido} comentou na solicitação "{solicitacao.assunto}": {texto[:100]}'

    irmaos = _irmaos_envolvidos_solicitacao(solicitacao, excluir=autor)
    destinatarios = {irmao.user_id for irmao in irmaos if irmao.user_id}

    notifs = [
        NotificacaoSistema(destinatario_id=uid, titulo=titulo, mensagem=mensagem, url=url)
        for uid in destinatarios
    ]
    if notifs:
        NotificacaoSistema.objects.bulk_create(notifs)

    ESTADO_LABELS = dict(SolicitacaoInterdepartamental.ESTADO_CHOICES)
    emails_to, telefones = _contactos_de_irmaos(irmaos)
    if not emails_to and not telefones:
        return

    context = {
        'titulo': titulo,
        'mensagem': mensagem,
        'novo_estado': solicitacao.estado,
        'estado_display': ESTADO_LABELS.get(solicitacao.estado, solicitacao.estado),
        'assunto': solicitacao.assunto,
        'categoria': solicitacao.get_categoria_display(),
        'dept_solicitante': str(solicitacao.departamento_solicitante),
        'dept_destinatario': str(solicitacao.departamento_destinatario),
        'prioridade': solicitacao.get_prioridade_display(),
        'data_necessidade': solicitacao.data_necessidade.strftime('%d/%m/%Y') if solicitacao.data_necessidade else '',
        'observacao': texto,
        'responsavel': f'{autor.nome} {autor.apelido}',
    }
    if emails_to:
        try:
            html_content = render_to_string('emails/email_solicitacao_estado.html', context)
            from_email = settings.EMAIL_HOST_USER or None
            for email_addr in emails_to:
                msg = EmailMultiAlternatives(
                    subject=titulo,
                    body=mensagem,
                    from_email=from_email,
                    to=[email_addr],
                )
                msg.attach_alternative(html_content, 'text/html')
                msg.send()
            logger.info('Emails de comentário solicitação #%s enviados para %s', solicitacao.id, emails_to)
        except Exception as e:
            logger.error('Falha ao enviar emails de comentário solicitação #%s: %s', solicitacao.id, e)

    if telefones:
        _enviar_sms(telefones, f'TIBL — {titulo}. {mensagem}')


def _notificar_caso_pastoral(caso, actor, mensagem_texto):
    """Cria notificação in-app e envia email para os envolvidos num caso pastoral."""
    url = reverse('sitetibl:mostra_detalhe', args=['casospastorais', caso.id])
    titulo = f'Caso Pastoral — {caso.titulo}'

    destinatarios = set()
    if caso.responsavel and caso.responsavel.user_id:
        destinatarios.add(caso.responsavel.user_id)
    if caso.criado_por and caso.criado_por.user_id:
        destinatarios.add(caso.criado_por.user_id)
    # Excluir o actor
    if actor and actor.user_id:
        destinatarios.discard(actor.user_id)

    notifs = [
        NotificacaoSistema(destinatario_id=uid, titulo=titulo, mensagem=mensagem_texto, url=url)
        for uid in destinatarios
    ]
    if notifs:
        NotificacaoSistema.objects.bulk_create(notifs)

    users = User.objects.filter(id__in=destinatarios, email__gt='').select_related()
    emails_to = [u.email for u in users if u.email]
    if not emails_to:
        return

    TIPO_LABELS = dict(CasoPastoral.TIPO_CHOICES)
    ESTADO_LABELS = dict(CasoPastoral.ESTADO_CHOICES)
    context = {
        'titulo': titulo,
        'mensagem': mensagem_texto,
        'caso_titulo': caso.titulo,
        'caso_tipo': TIPO_LABELS.get(caso.tipo, caso.tipo),
        'caso_estado': ESTADO_LABELS.get(caso.estado, caso.estado),
        'caso_prioridade': caso.get_prioridade_display(),
        'membro': str(caso.membro),
        'responsavel': str(caso.responsavel) if caso.responsavel else 'Não atribuído',
    }
    try:
        html_content = render_to_string('emails/email_alerta_pastoral.html', context)
        for email_addr in emails_to:
            msg = EmailMultiAlternatives(
                subject=titulo, body=mensagem_texto,
                from_email=None, to=[email_addr],
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
        logger.info('Emails caso pastoral #%s enviados para %s', caso.id, emails_to)
    except Exception as e:
        logger.error('Falha ao enviar emails caso pastoral #%s: %s', caso.id, e)


def comeco(request):
    return render(request, 'index.html')


@login_required
def api_municipios(request, provincia_id):
    """Retorna municípios de uma província em JSON (para cascading dropdown)."""
    municipios = Municipio.objects.filter(
        provincia_id=provincia_id
    ).order_by('nome').values('id', 'nome')
    return JsonResponse(list(municipios), safe=False)


@login_required
def api_funcoes_por_actividade(request, actividade_id):
    """Retorna funções relevantes para o departamento da actividade + genéricas."""
    actividade = get_object_or_404(Actividade, id=actividade_id)
    if actividade.departamento_id:
        funcoes = Funcao.objects.filter(
            Q(departamento_id=actividade.departamento_id) | Q(departamento__isnull=True)
        ).order_by('designacao')
    else:
        funcoes = Funcao.objects.all().order_by('designacao')
    data = [{'id': f.id, 'designacao': f.designacao} for f in funcoes]
    return JsonResponse(data, safe=False)


def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

@login_required
def mostraGestao(request,gestaoescolhida,pagina):
    LEGACY_GESTAO_MAP = {
        'entradabancos': 'entradas',
        'saidabancos': 'saidas',
        'entradascaixa': 'entradas',
        'saidascaixa': 'saidas',
    }
    if gestaoescolhida in LEGACY_GESTAO_MAP:
        return redirect('sitetibl:mostra_gestao', gestaoescolhida=LEGACY_GESTAO_MAP[gestaoescolhida], pagina=pagina)

    if gestaoescolhida == 'irmaos' and not request.user.has_perm('sitetibl.change_irmao'):
        messages.error(request, 'Acesso negado! Não tem permissão para consultar a gestão de irmãos.')
        return redirect('index')

    lista = {'escalas' : Escala.objects.select_related('irmao', 'actividade', 'actividade__departamento', 'funcao', 'funcao__departamento'), 
             'mandatos': Mandato.objects.select_related('irmao', 'departamento'), 
             'irmaos': Irmao.objects.select_related('celula', 'localcongregacao', 'provincia', 'municipio'), 
             'ajudas': Ajuda.objects.select_related('beneficiario', 'patrocinador', 'cesta'), 
             'cestas': Cestabasica.objects.select_related('saida'), 
             'bancos': Banco.objects, 
             'contasbancarias' : Contabancaria.objects.select_related('banco', 'proprietario', 'instituicao'), 
             'actividades' : Actividade.objects.select_related('designacao', 'localactividade').filter(parent_event__isnull=True), 
             'departamentos' : Departamento.objects.select_related('lider_departamento', 'vice_lider_departamento'),
             'entradas' : Entrada.objects.select_related('rubrica', 'responsavel', 'contaaacreditar'), 
             'saidas' : Saida.objects.select_related('rubrica', 'responsavel', 'conta'), 
             'dizimosofertas' : Dizimooferta.objects.select_related('irmao', 'tipooferta', 'actividade'),
             'relatoriosemanalcelula' : RelatorioSemanalCelula.objects.select_related('nome_celula', 'lider_responsavel'), 
             'pedidosaida' : PedidoSaida.objects.select_related('departamento', 'requerente', 'status_de_aprovacao', 'aprovador'),
             'orcamentodepartamento': OrcamentoDepartamento.objects.select_related('departamento', 'moeda'),
             'inventariopatrimonio': InventarioPatrimonio.objects.select_related('categoria_patrimonio', 'responsavel', 'estado'),
             'conteudoensino': ConteudoEnsino.objects.select_related('autor'),
             'enviomensagem': EnvioMensagem.objects.select_related('quemenviou'),
             'solicitacoes': SolicitacaoInterdepartamental.objects.select_related('departamento_solicitante', 'departamento_destinatario', 'solicitante', 'responsavel_resposta'),
             'casospastorais': CasoPastoral.objects.select_related('membro', 'responsavel', 'criado_por'),
             'visitantes': VisitanteRecorrente.objects.select_related('celula', 'responsavel_integracao', 'irmao_convertido'),
             'celulas': Celula.objects.select_related('lider', 'vice_lider'),
             }
    if gestaoescolhida == 'departamentos':
        resultado = (
            lista[gestaoescolhida]
            .all()
            .annotate(total_integrantes=Count('integrantes', distinct=True))
            .order_by('designacao')
        )
    elif gestaoescolhida == 'celulas':
        resultado = (
            lista[gestaoescolhida]
            .all()
            .annotate(total_relatorios=Count('relatorios', distinct=True))
            .order_by('designacao')
        )
    elif gestaoescolhida == 'contasbancarias':
        nomev = request.GET.get('nomev', '').strip()
        apelidov = request.GET.get('apelidov', '').strip()
        instituicaov = request.GET.get('instituicaov', '').strip()
        bancov = request.GET.get('bancov', '').strip()
        numerocontav = request.GET.get('numerocontav', '').strip()
        moedav = request.GET.get('moedav', '').strip()

        kwargs = {
            'is_active': True,
            'banco__designacao__icontains': bancov,
            'numeroconta__icontains': numerocontav,
        }
        if nomev:
            kwargs['proprietario__nome__icontains'] = nomev
        if apelidov:
            kwargs['proprietario__apelido__icontains'] = apelidov
        if instituicaov:
            kwargs['instituicao__designacao__icontains'] = instituicaov
        if moedav:
            kwargs['moeda'] = moedav

        resultado = lista[gestaoescolhida].filter(**kwargs).order_by('id')
    elif gestaoescolhida == 'mandatos':
        resultado = lista[gestaoescolhida].exclude(funcao='membro').order_by('departamento__designacao', 'funcao', 'irmao__nome', 'irmao__apelido')
    elif (gestaoescolhida == 'irmaos'):
        resultado = lista[gestaoescolhida].prefetch_related('mandato_set__departamento').all().order_by('nome','outrosnomes')
    elif gestaoescolhida == 'pedidosaida':
        qs = lista[gestaoescolhida].all()
        estado_filtro = request.GET.get('estado', '').strip()
        if estado_filtro:
            qs = qs.filter(estado=estado_filtro)
        resultado = qs.order_by('-data_criacao')
    elif gestaoescolhida == 'solicitacoes':
        qs = lista[gestaoescolhida].all()
        estado_filtro = request.GET.get('estado', '').strip()
        if estado_filtro:
            qs = qs.filter(estado=estado_filtro)
        resultado = qs.order_by('-data_criacao')
    elif gestaoescolhida == 'casospastorais':
        qs = lista[gestaoescolhida].all()
        # Filtro de confidencialidade
        irmao_logado = Irmao.objects.filter(user=request.user).first()
        if not request.user.is_superuser and not request.user.groups.filter(name='Pastor').exists():
            qs = qs.filter(Q(confidencial=False) | Q(responsavel=irmao_logado) | Q(criado_por=irmao_logado))
        estado_filtro = request.GET.get('estado', '').strip()
        tipo_filtro = request.GET.get('tipo', '').strip()
        if estado_filtro:
            qs = qs.filter(estado=estado_filtro)
        if tipo_filtro:
            qs = qs.filter(tipo=tipo_filtro)
        resultado = qs.order_by('-data_abertura')
    elif gestaoescolhida == 'visitantes':
        qs = lista[gestaoescolhida].all()
        estado_filtro = request.GET.get('estado', '').strip()
        if estado_filtro:
            qs = qs.filter(estado=estado_filtro)
        resultado = qs.order_by('-ultima_visita')
    elif gestaoescolhida == 'escalas':
        resultado = lista[gestaoescolhida].all().annotate(
            is_passado=Case(
                When(actividade__data__lt=date.today(), then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by(
            'actividade__departamento__designacao',
            'is_passado',
            'actividade__data',
            'actividade__id',
            'funcao__designacao',
        )
    elif gestaoescolhida == 'actividades':
        mostrar_historico = request.GET.get('historico') == '1'
        if mostrar_historico:
            resultado = lista[gestaoescolhida].filter(data__lt=date.today()).order_by('-data')
        else:
            resultado = lista[gestaoescolhida].filter(data__gte=date.today()).order_by('data')
    elif gestaoescolhida == 'dizimosofertas':
        _do_nomev = request.GET.get('nomev', '').strip()
        _do_apelidov = request.GET.get('apelidov', '').strip()
        _do_mesv = request.GET.get('mesv', '0')
        _do_anov = request.GET.get('anov', '0')
        _do_tipov = request.GET.get('tipov', '0')
        _do_qs = lista[gestaoescolhida].all()
        if _do_nomev:
            _do_qs = _do_qs.filter(irmao__nome__icontains=_do_nomev)
        if _do_apelidov:
            _do_qs = _do_qs.filter(irmao__apelido__icontains=_do_apelidov)
        if _do_mesv != '0':
            _do_qs = _do_qs.filter(datacorrespondente__month=_do_mesv)
        if _do_anov != '0':
            _do_qs = _do_qs.filter(datacorrespondente__year=_do_anov)
        if _do_tipov != '0':
            _do_qs = _do_qs.filter(tipooferta_id=_do_tipov)
        resultado = _do_qs.order_by('-datacorrespondente', 'id')
    elif gestaoescolhida in ('entradas', 'saidas'):
        resultado = lista[gestaoescolhida].all().order_by('-data', '-id')
    else:
        resultado = lista[gestaoescolhida].all().order_by('id')
    paginador = Paginator(resultado, 20)
    pagina_final = request.GET.get('pagina', pagina)
    paginaresultado = paginador.get_page(pagina_final)
    if (gestaoescolhida == 'ajudas') or (gestaoescolhida == 'cestas') or (gestaoescolhida == 'actividades'):
        context = { 'bb':paginaresultado, 'listameses' : MESES, 'tipoajuda' : Tipoajuda.objects.values('id','designacao'), 'listafuncoes' : Funcao.objects.values('id','designacao'), 'listaactividades' : Listaactividades.objects.values('id','designacao'), 'hoje': date.today(), 'mostrar_historico': request.GET.get('historico') == '1' }
    elif gestaoescolhida == 'departamentos':
        context = { 'bb':paginaresultado, 'listadepartamentos' : Departamento.objects.values('id','designacao'), 'funcao_choices': Mandato.FUNCAO_CHOICES}
    elif gestaoescolhida == 'contasbancarias':
        context = {
            'bb': paginaresultado,
            'listamoedas': MOEDA.items(),
            'filtro_instituicaov': request.GET.get('instituicaov', ''),
            'filtro_bancov': request.GET.get('bancov', ''),
            'filtro_numerocontav': request.GET.get('numerocontav', ''),
            'filtro_moedav': request.GET.get('moedav', ''),
        }
    elif (gestaoescolhida == 'entradas') or (gestaoescolhida == 'saidas'):
        context = { 'bb':paginaresultado, 'listarubricasentrada' : Rubricaentrada.objects.values('id', 'designacao'), 'listarubricassaida' : Rubricasaida.objects.values('id', 'designacao'), 'listameses' : MESES, 'listacontasigreja' : Contabancaria.objects.values('id','numeroconta','instituicao_id').filter(instituicao_id=1) }
    elif gestaoescolhida == 'irmaos':
        context = {
            'bb': paginaresultado,
            'listamunicipios': Municipio.objects.select_related('provincia').order_by('provincia__nome', 'nome'),
            'categorias_membro': Irmao.CATEGORIA_CHOICES,
        }
    elif gestaoescolhida == 'pedidosaida':
        contagens = dict(
            PedidoSaida.objects.values_list('estado')
            .annotate(c=Count('id'))
            .values_list('estado', 'c')
        )
        estado_choices_com_contagem = [
            (val, label, contagens.get(val, 0))
            for val, label in PedidoSaida.ESTADO_CHOICES
        ]
        context = {
            'bb': paginaresultado,
            'estado_filtro': request.GET.get('estado', ''),
            'estado_choices_com_contagem': estado_choices_com_contagem,
            'total_pedidos': sum(contagens.values()),
        }
    elif gestaoescolhida == 'solicitacoes':
        contagens = dict(
            SolicitacaoInterdepartamental.objects.values_list('estado')
            .annotate(c=Count('id'))
            .values_list('estado', 'c')
        )
        estado_choices_com_contagem = [
            (val, label, contagens.get(val, 0))
            for val, label in SolicitacaoInterdepartamental.ESTADO_CHOICES
        ]
        context = {
            'bb': paginaresultado,
            'estado_filtro': request.GET.get('estado', ''),
            'estado_choices_com_contagem': estado_choices_com_contagem,
            'total_solicitacoes': sum(contagens.values()),
        }
    elif gestaoescolhida == 'escalas':
        context = {
            'bb': paginaresultado,
            'departamentos': Departamento.objects.order_by('designacao'),
            'departamentov_sel': request.GET.get('departamentov', ''),
            'hoje': date.today(),
        }
    elif gestaoescolhida == 'dizimosofertas':
        pagina_get = request.GET.get('pagina', pagina)
        paginador_do = Paginator(resultado, 20)
        paginaresultado = paginador_do.get_page(pagina_get)
        _do_agg = resultado.aggregate(total=Sum('valor'), contribuintes=Count('irmao', distinct=True))
        _do_total_periodo = _do_agg['total'] or 0
        _do_contribuintes = _do_agg['contribuintes'] or 0
        _do_ano_atual = date.today().year
        _do_total_ano = (
            lista['dizimosofertas']
            .filter(datacorrespondente__year=_do_ano_atual)
            .aggregate(total=Sum('valor'))['total'] or 0
        )
        _do_moedas = list(resultado.values_list('moeda', flat=True).distinct())
        _do_moeda_kpi = _do_moedas[0] if len(_do_moedas) == 1 else ('MULTI' if _do_moedas else '---')
        context = {
            'bb': paginaresultado,
            'listameses': MESES,
            'lista_tipos': TipoOferta.objects.order_by('designacao'),
            'filtro_nomev': _do_nomev,
            'filtro_apelidov': _do_apelidov,
            'filtro_mesv': _do_mesv,
            'filtro_anov': _do_anov,
            'filtro_tipov': _do_tipov,
            'kpi_total_periodo': _do_total_periodo,
            'kpi_contribuintes': _do_contribuintes,
            'kpi_total_ano': _do_total_ano,
            'kpi_moeda': _do_moeda_kpi,
            'kpi_ano_atual': _do_ano_atual,
        }
    else:
        context = { 'bb':paginaresultado, 'listameses' : MESES }

    paginador = Paginator(resultado, 20)
    pagina_final = request.GET.get('pagina', pagina)
    paginaresultado = paginador.get_page(pagina_final)
    return render(request, gestaoescolhida + '.html', context)


@login_required
def mostraActualizacao(request, gestaoescolhida, id):
    LEGACY_GESTAO_MAP = {
        'entradabancos': 'entradas',
        'saidabancos': 'saidas',
        'entradascaixa': 'entradas',
        'saidascaixa': 'saidas',
    }
    if gestaoescolhida in LEGACY_GESTAO_MAP:
        return redirect('sitetibl:mostra_actualizacao', gestaoescolhida=LEGACY_GESTAO_MAP[gestaoescolhida], id=id)

    lista = {'escalas' : Escala, 
             'mandatos': Mandato, 
             'irmaos':Irmao, 
             'ajudas':Ajuda, 
             'cestas': Cestabasica, 
             'bancos': Banco, 
             'contasbancarias' : Contabancaria, 
             'actividades' : Actividade, 
             'departamentos' : Departamento, 
             'entradas' : Entrada, 
             'saidas' : Saida, 
             'dizimosofertas' : Dizimooferta,
             'relatoriosemanalcelula' : RelatorioSemanalCelula, 
             'pedidosaida' : PedidoSaida,
             'orcamentodepartamento': OrcamentoDepartamento,
             'inventariopatrimonio': InventarioPatrimonio,
             'conteudoensino':ConteudoEnsino,
             'enviomensagem':EnvioMensagem,
             'solicitacoes':SolicitacaoInterdepartamental,
             'casospastorais':CasoPastoral,
             'visitantes':VisitanteRecorrente,
             'celulas':Celula,
              }
    listaformularios = {'escalas' : EscalaForm, 
                        'mandatos': MandatoForm, 
                        'irmaos':IrmaoForm, 
                        'ajudas':AjudaForm, 
                        'cestas': CestabasicaForm, 
                        'bancos': BancoForm, 
                        'contasbancarias' : ContabancariaForm, 
                        'actividades' : ActividadeForm, 
                        'departamentos' : DepartamentoForm, 
                        'entradas' : EntradaForm, 
                        'saidas' : SaidaForm, 
                        'dizimosofertas' : DizimoofertaForm, 
                        'relatoriosemanalcelula' : RelatorioSemanalCelulaForm,
                        'pedidosaida' : PedidoSaidaUpdateForm,
                        'orcamentodepartamento' : OrcamentoDepartamentoForm,
                        'inventariopatrimonio': InventarioPatrimonioForm,
                        'conteudoensino':ConteudoEnsinoForm,
                        'enviomensagem':EnvioMensagemForm,
                        'solicitacoes':SolicitacaoUpdateForm,
                        'casospastorais':CasoPastoralUpdateForm,
                        'visitantes':VisitanteRecorrenteForm,
                        'celulas':CelulaForm,
                        }
    
    model = lista[gestaoescolhida]
  
    # ðŸ” verificação dinâmica
    perm = f'{model._meta.app_label}.change_{model._meta.model_name}'
    if not request.user.has_perm(perm):
        messages.error(request, 'Acesso negado! Você não tem permissão para actualizar registros.')
        return redirect('index')

    registo = get_object_or_404(model, id=id)

    # ðŸ” Verificação de propriedade para actividades
    if gestaoescolhida == 'actividades':
        papel_elevado = request.user.has_perm('sitetibl.change_mandato')
        if not papel_elevado:
            pode_editar = (registo.criado_por is not None and registo.criado_por == request.user)
            if not pode_editar and registo.departamento_id:
                irmao_logado = Irmao.objects.filter(user=request.user).first()
                if irmao_logado:
                    pode_editar = Departamento.objects.filter(
                        Q(lider_departamento=irmao_logado) | Q(vice_lider_departamento=irmao_logado),
                        id=registo.departamento_id,
                    ).exists()
            if not pode_editar:
                messages.error(request, 'Só pode editar actividades que criou ou do seu departamento.')
                return redirect('index')

    if request.method == 'GET':
        form = listaformularios[gestaoescolhida](instance=registo)
        tmpl = 'actividades_form.html' if gestaoescolhida == 'actividades' else 'formulario_actualizacao.html'
        return render(request, tmpl, {
            'formulario': form,
            'id': id,
            'is_update': True,
        })

    elif request.method == 'POST':
        formulario = listaformularios[gestaoescolhida](
            request.POST,
            request.FILES,
            instance=registo
        )

        if formulario.is_valid():
            obj = formulario.save(commit=False)

            # âš ï¸ Verificação de conflito de horário para actividades
            if gestaoescolhida == 'actividades':
                data = formulario.cleaned_data['data']
                inicio = formulario.cleaned_data['inicio']
                fim = formulario.cleaned_data['fim']
                conflitos = Actividade.objects.filter(
                    data=data, inicio__lt=fim, fim__gt=inicio
                ).exclude(id=registo.id)
                mesma_data_diferente = Actividade.objects.filter(
                    data=data
                ).exclude(id=registo.id).exclude(inicio__lt=fim, fim__gt=inicio)
                if conflitos.exists():
                    primeiro = conflitos.first()
                    messages.error(
                        request,
                        f'Conflito de horário: já existe uma actividade "{primeiro.designacao}" '
                        f'das {primeiro.inicio} Ã s {primeiro.fim} neste dia com horário sobrepóvel.'
                    )
                    return render(request, 'actividades_form.html', {'formulario': formulario, 'id': id, 'is_update': True})
                elif mesma_data_diferente.exists():
                    messages.warning(
                        request,
                        'Já existe outra actividade neste dia com horário diferente. '
                        'Se for num local diferente, pode prosseguir normalmente.'
                    )

            obj.save()
            messages.success(request, 'Actualização foi bem sucedida')
            if gestaoescolhida == 'solicitacoes':
                return HttpResponseRedirect(reverse('sitetibl:mostra_detalhe', args=['solicitacoes', id]))
            return HttpResponseRedirect(reverse('index'))

        else:
            messages.error(request, 'Foram encontrados erros ao preencher o formulário.')
            tmpl = 'actividades_form.html' if gestaoescolhida == 'actividades' else 'formulario_actualizacao.html'
            return render(request, tmpl, {
                'formulario': formulario,
                'id': id,
                'is_update': True,
            })

@login_required
def mostraDetalhe(request, gestaoescolhida, identificador):
    LEGACY_GESTAO_MAP = {
        'entradabancos': 'entradas',
        'saidabancos': 'saidas',
        'entradascaixa': 'entradas',
        'saidascaixa': 'saidas',
    }
    if gestaoescolhida in LEGACY_GESTAO_MAP:
        return redirect('sitetibl:mostra_detalhe', gestaoescolhida=LEGACY_GESTAO_MAP[gestaoescolhida], identificador=identificador)

    if gestaoescolhida == 'irmaos' and not request.user.has_perm('sitetibl.change_irmao'):
        messages.error(request, 'Acesso negado! Não tem permissão para consultar detalhes de irmãos.')
        return redirect('index')

    lista_qs = {
        'irmaos': Irmao.objects.select_related('celula', 'localcongregacao', 'provincia', 'municipio'),
        'ajudas': Ajuda.objects.select_related('beneficiario', 'patrocinador', 'cesta'),
        'cestas': Cestabasica.objects.select_related('saida'),
        'bancos': Banco.objects,
        'contasbancarias': Contabancaria.objects.select_related('banco', 'proprietario', 'instituicao'),
        'actividades': Actividade.objects.select_related('designacao', 'localactividade'),
        'departamentos': Departamento.objects.select_related('lider_departamento', 'vice_lider_departamento'),
        'entradas': Entrada.objects.select_related('rubrica', 'responsavel', 'contaaacreditar'),
        'saidas': Saida.objects.select_related('rubrica', 'responsavel', 'conta'),
        'dizimosofertas': Dizimooferta.objects.select_related('irmao', 'tipooferta', 'actividade'),
        'relatoriosemanalcelula': RelatorioSemanalCelula.objects.select_related('nome_celula', 'lider_responsavel'),
        'pedidosaida': PedidoSaida.objects.select_related('departamento', 'requerente', 'status_de_aprovacao', 'aprovador'),
        'orcamentodepartamento': OrcamentoDepartamento.objects.select_related('departamento', 'moeda'),
        'inventariopatrimonio': InventarioPatrimonio.objects.select_related('categoria_patrimonio', 'responsavel', 'estado'),
        'conteudoensino': ConteudoEnsino.objects.select_related('autor'),
        'enviomensagem': EnvioMensagem.objects.select_related('quemenviou'),
        'escalas': Escala.objects.select_related('irmao', 'actividade', 'funcao'),
        'solicitacoes': SolicitacaoInterdepartamental.objects.select_related('departamento_solicitante', 'departamento_destinatario', 'solicitante', 'responsavel_resposta'),
        'casospastorais': CasoPastoral.objects.select_related('membro', 'responsavel', 'criado_por'),
        'visitantes': VisitanteRecorrente.objects.select_related('celula', 'responsavel_integracao', 'irmao_convertido'),
    }
    queryset = lista_qs.get(gestaoescolhida)
    if queryset is None:
        return redirect('index')

    # Avoid rendering blank detail pages when an invalid id is requested.
    registo = get_object_or_404(queryset, id=identificador)
    registoachado = [registo]
    ficheirodetalhado = gestaoescolhida + 'detalhado.html'
    if gestaoescolhida == 'cestas':
        detalhecestas = ComposicaoCesta.objects.filter(cesta = identificador)
        context = {}
        while detalhecestas.exists():
            totalcestasajuda = Ajuda.objects.filter(cesta = identificador).count()
            montantedisponibilizado = Cestabasica.objects.values('valordisponibilizado').filter( id = identificador)
            for valor in montantedisponibilizado:
                a = valor['valordisponibilizado']
            subtotal = detalhecestas.all().annotate(subsoma = F('quantidade') * F('precounitario'))
            total = subtotal.aggregate(soma = Sum('subsoma')).get('soma')
            valorgasto = total * totalcestasajuda
            cestasremanescentes = int((a - valorgasto)/total)
            context = {'registoachado' : registoachado, 'gestaoescolhida' : gestaoescolhida, 'detalhecestas' : subtotal, 'total' : total, 'totalcestasajuda' : totalcestasajuda, 'montantedisponibilizado' : a, 'valorgasto' : valorgasto, 'cestasremanescentes' : cestasremanescentes}
    elif gestaoescolhida == 'actividades':
        escalas_da_actividade = (
            Escala.objects
            .filter(actividade_id=identificador)
            .select_related('irmao', 'irmao__celula', 'funcao', 'funcao__departamento')
            .prefetch_related('irmao_protocolo', 'irmao_protocolo__celula')
            .order_by('funcao__departamento__designacao', 'funcao__designacao', 'irmao__nome')
        )
        todas_funcoes = Funcao.objects.select_related('departamento').order_by('departamento__designacao', 'designacao')
        todos_irmaos = Irmao.objects.select_related('celula', 'localcongregacao').order_by('nome', 'apelido')
        departamentos = Departamento.objects.order_by('designacao')
        # mapa irmao_id â†’ [departamento_id, …] para filtro JS no modal
        from collections import defaultdict
        _irmao_depts = defaultdict(list)
        for m in Mandato.objects.values('irmao_id', 'departamento_id'):
            _irmao_depts[m['irmao_id']].append(m['departamento_id'])
        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'escalas_da_actividade': escalas_da_actividade,
            'todas_funcoes': todas_funcoes,
            'todos_irmaos': todos_irmaos,
            'departamentos': departamentos,
            'irmao_depts_json': json.dumps({str(k): v for k, v in _irmao_depts.items()}),
            'tem_protocolo': escalas_da_actividade.filter(eh_protocolo=True).exists(),
            'tem_escalas': escalas_da_actividade.exists(),
        }
    elif gestaoescolhida == 'departamentos':
        mandatos_departamento = (
            Mandato.objects
            .select_related('irmao')
            .filter(departamento_id=identificador)
            .order_by('funcao', 'irmao__nome', 'irmao__apelido')
        )
        irmao_logado = Irmao.objects.filter(user=request.user).first()
        lidera_departamento = (
            irmao_logado is not None
            and (registo.lider_departamento_id == irmao_logado.id
                 or registo.vice_lider_departamento_id == irmao_logado.id)
        )
        # Papéis elevados (Pastor/Secretaria/Admin) gerem qualquer dept;
        # LD/VLD só gere o departamento onde é líder ou vice-líder.
        papel_elevado_dept = request.user.has_perm('sitetibl.change_mandato')
        pode_gerir_membros = lidera_departamento or papel_elevado_dept

        if request.method == 'POST':
            if not pode_gerir_membros:
                messages.error(request, 'Apenas o lider do departamento ou um administrador pode gerir membros.')
                return HttpResponseRedirect(reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador]))

            action = request.POST.get('action', '').strip()
            if action == 'add_member':
                irmao_ids = [i for i in request.POST.getlist('irmao_ids') if i.strip()]
                funcao = request.POST.get('funcao', 'membro').strip()
                funcoes_validas = [c[0] for c in Mandato.FUNCAO_CHOICES]
                if funcao not in funcoes_validas:
                    funcao = 'membro'

                if not irmao_ids:
                    messages.error(request, 'Seleccione pelo menos um irmão para adicionar ao departamento.')
                else:
                    FUNCOES_EXCLUSIVAS = Mandato.FUNCOES_EXCLUSIVAS
                    # Cargo exclusivo com vários irmãos selecionados → forçar 'membro'

                    if funcao in FUNCOES_EXCLUSIVAS and len(irmao_ids) > 1:
                        funcao = 'membro'
                        messages.warning(request, 'Cargo exclusivo não pode ser atribuído a vários irmãos de uma vez. Cargo alterado para Membro.')
                    elif funcao in FUNCOES_EXCLUSIVAS:
                        # Remover cargo exclusivo do ocupante anterior
                        ocupante = Mandato.objects.filter(
                            departamento_id=identificador,
                            funcao=funcao,
                        ).select_related('irmao').first()
                        if ocupante and str(ocupante.irmao_id) != irmao_ids[0]:
                            nome_anterior = f'{ocupante.irmao.nome} {ocupante.irmao.apelido}'
                            ocupante.funcao = 'membro'
                            ocupante.save(update_fields=['funcao'])
                            funcao_display = dict(Mandato.FUNCAO_CHOICES).get(funcao, funcao)
                            messages.warning(
                                request,
                                f'{nome_anterior} deixou de ser {funcao_display} e voltou a ser Membro.',
                            )

                    adicionados = 0
                    atualizados = 0
                    for irmao_id in irmao_ids:
                        mandato_existente = Mandato.objects.filter(
                            departamento_id=identificador,
                            irmao_id=irmao_id,
                        ).first()
                        if mandato_existente:
                            if mandato_existente.funcao != funcao:
                                mandato_existente.funcao = funcao
                                mandato_existente.save(update_fields=['funcao'])
                                atualizados += 1
                        else:
                            try:
                                Mandato.objects.create(
                                    departamento_id=identificador,
                                    irmao_id=irmao_id,
                                    funcao=funcao,
                                )
                                adicionados += 1
                            except IntegrityError:
                                pass

                    partes = []
                    if adicionados:
                        partes.append(f'{adicionados} membro(s) adicionado(s)')
                    if atualizados:
                        partes.append(f'{atualizados} cargo(s) actualizado(s)')
                    if partes:
                        messages.success(request, ' e '.join(partes) + ' com sucesso.')
                    else:
                        messages.info(request, 'Nenhuma alteração efectuada — os irmãos já pertencem ao departamento com esse cargo.')

            elif action == 'remove_member':
                mandato_id = request.POST.get('mandato_id', '').strip()
                mandato = Mandato.objects.filter(id=mandato_id, departamento_id=identificador).first()
                if mandato is None:
                    messages.error(request, 'Registo de mandato nao encontrado para este departamento.')
                else:
                    # Limpar FK do Departamento se removendo lider/vice_lider
                    if mandato.funcao == 'lider':
                        Departamento.objects.filter(pk=identificador, lider_departamento=mandato.irmao).update(lider_departamento=None)
                    elif mandato.funcao == 'vice_lider':
                        Departamento.objects.filter(pk=identificador, vice_lider_departamento=mandato.irmao).update(vice_lider_departamento=None)
                    mandato.delete()
                    messages.success(request, 'Membro removido do departamento com sucesso.')

            elif action == 'add_funcao':
                if not (lidera_departamento or request.user.has_perm('sitetibl.add_funcao')):
                    messages.error(request, 'Sem permissão para adicionar funções.')
                else:
                    nome_funcao = request.POST.get('nome_funcao', '').strip()
                    if not nome_funcao:
                        messages.error(request, 'O nome da função não pode estar vazio.')
                    elif Funcao.objects.filter(designacao=nome_funcao, departamento_id=identificador).exists():
                        messages.warning(request, 'Esta função já existe neste departamento.')
                    else:
                        Funcao.objects.create(designacao=nome_funcao, departamento_id=identificador)
                        messages.success(request, f'Função "{nome_funcao}" adicionada ao departamento.')

            elif action == 'remove_funcao':
                if not (lidera_departamento or request.user.has_perm('sitetibl.delete_funcao')):
                    messages.error(request, 'Sem permissão para remover funções.')
                else:
                    funcao_id = request.POST.get('funcao_id', '').strip()
                    func = Funcao.objects.filter(id=funcao_id, departamento_id=identificador).first()
                    if func is None:
                        messages.error(request, 'Função não encontrada neste departamento.')
                    elif Escala.objects.filter(funcao=func).exists():
                        messages.warning(request, f'Não é possível remover "{func.designacao}" porque já está em uso em escalas.')
                    else:
                        func.delete()
                        messages.success(request, 'Função removida do departamento.')

            return HttpResponseRedirect(reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador]))

        funcoes_departamento = Funcao.objects.filter(departamento_id=identificador).order_by('designacao')
        pode_gerir_funcoes = (
            lidera_departamento
            or request.user.has_perm('sitetibl.add_funcao')
        )

        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'mandatos_departamento': mandatos_departamento,
            'todos_irmaos': Irmao.objects.order_by('nome', 'apelido'),
            'funcao_choices': Mandato.FUNCAO_CHOICES,
            'pode_gerir_membros': pode_gerir_membros,
            'funcoes_departamento': funcoes_departamento,
            'pode_gerir_funcoes': pode_gerir_funcoes,
        }
    elif gestaoescolhida == 'contasbancarias':
        entradas_conta = (
            Entrada.objects
            .select_related('rubrica', 'responsavel', 'contaorigem')
            .filter(tipo='banco', contaaacreditar_id=identificador)
            .order_by('-data', '-hora')
        )
        saidas_conta = (
            Saida.objects
            .select_related('rubrica', 'responsavel', 'contaaacreditar')
            .filter(tipo='banco', conta_id=identificador)
            .order_by('-data', '-hora')
        )
        total_entradas = entradas_conta.aggregate(total=Sum('valor')).get('total') or 0
        total_saidas = saidas_conta.aggregate(total=Sum('valor')).get('total') or 0

        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'entradas_conta': entradas_conta[:8],
            'saidas_conta': saidas_conta[:8],
            'total_entradas_conta': total_entradas,
            'total_saidas_conta': total_saidas,
            'saldo_movimento': total_entradas - total_saidas,
        }
    elif gestaoescolhida == 'bancos':
        contas_banco = (
            Contabancaria.objects
            .select_related('proprietario', 'instituicao')
            .filter(banco_id=identificador)
            .order_by('numeroconta')
        )
        entradas_banco = (
            Entrada.objects
            .select_related('contaaacreditar', 'rubrica')
            .filter(tipo='banco', contaaacreditar__banco_id=identificador)
            .order_by('-data', '-hora')[:6]
        )
        saidas_banco = (
            Saida.objects
            .select_related('conta', 'rubrica')
            .filter(tipo='banco', conta__banco_id=identificador)
            .order_by('-data', '-hora')[:6]
        )
        total_contas = contas_banco.count()
        total_saldo_banco = sum(conta.saldo_actual() for conta in contas_banco)

        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'contas_banco': contas_banco,
            'entradas_banco': entradas_banco,
            'saidas_banco': saidas_banco,
            'total_contas_banco': total_contas,
            'total_saldo_banco': total_saldo_banco,
        }
    elif gestaoescolhida == 'entradas':
        if registo.tipo == 'banco' and registo.contaaacreditar_id:
            conta_destino_id = registo.contaaacreditar_id
            entradas_relacionadas = (
                Entrada.objects
                .select_related('rubrica')
                .filter(tipo='banco', contaaacreditar_id=conta_destino_id)
                .exclude(id=identificador)
                .order_by('-data', '-hora')[:6]
            )
            saidas_relacionadas = (
                Saida.objects
                .select_related('rubrica')
                .filter(tipo='banco', conta_id=conta_destino_id)
                .order_by('-data', '-hora')[:6]
            )
        else:
            entradas_relacionadas = (
                Entrada.objects
                .select_related('rubrica', 'responsavel')
                .filter(tipo='caixa', rubrica_id=registo.rubrica_id)
                .exclude(id=identificador)
                .order_by('-data', '-hora')[:6]
            )
            saidas_relacionadas = (
                Saida.objects
                .select_related('rubrica', 'responsavel')
                .filter(tipo='caixa', responsavel_id=registo.responsavel_id)
                .order_by('-data', '-hora')[:6]
            )
        total_entradas_rubrica = (
            Entrada.objects
            .filter(rubrica_id=registo.rubrica_id)
            .aggregate(total=Sum('valor'))
            .get('total') or 0
        )
        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'entradas_relacionadas': entradas_relacionadas,
            'saidas_relacionadas': saidas_relacionadas,
            'total_entradas_rubrica': total_entradas_rubrica,
        }
    elif gestaoescolhida == 'saidas':
        if registo.tipo == 'banco' and registo.conta_id:
            conta_origem_id = registo.conta_id
            entradas_relacionadas = (
                Entrada.objects
                .select_related('rubrica')
                .filter(tipo='banco', contaaacreditar_id=conta_origem_id)
                .order_by('-data', '-hora')[:6]
            )
            saidas_relacionadas = (
                Saida.objects
                .select_related('rubrica')
                .filter(tipo='banco', conta_id=conta_origem_id)
                .exclude(id=identificador)
                .order_by('-data', '-hora')[:6]
            )
        else:
            saidas_relacionadas = (
                Saida.objects
                .select_related('rubrica', 'responsavel')
                .filter(tipo='caixa', rubrica_id=registo.rubrica_id)
                .exclude(id=identificador)
                .order_by('-data', '-hora')[:6]
            )
            entradas_relacionadas = (
                Entrada.objects
                .select_related('rubrica', 'responsavel')
                .filter(tipo='caixa', responsavel_id=registo.responsavel_id)
                .order_by('-data', '-hora')[:6]
            )
        total_saidas_rubrica = (
            Saida.objects
            .filter(rubrica_id=registo.rubrica_id)
            .aggregate(total=Sum('valor'))
            .get('total') or 0
        )
        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'entradas_relacionadas': entradas_relacionadas,
            'saidas_relacionadas': saidas_relacionadas,
            'total_saidas_rubrica': total_saidas_rubrica,
        }
    elif gestaoescolhida == 'irmaos':
        pode_gerir_user = request.user.has_perm('sitetibl.change_irmao')

        if request.method == 'POST' and pode_gerir_user:
            action = request.POST.get('action', '').strip()

            if action == 'criar_user' and registo.user is None:
                # Build a unique username
                if registo.email:
                    base_username = registo.email.split('@')[0].lower().replace(' ', '')
                else:
                    base_username = f'{registo.nome}.{registo.apelido}'.lower().replace(' ', '')
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f'{base_username}{counter}'
                    counter += 1

                temp_password = get_random_string(length=12)
                user = User.objects.create_user(
                    username=username,
                    email=registo.email or '',
                    password=temp_password,
                    first_name=registo.nome or '',
                    last_name=registo.apelido or '',
                )
                Irmao.objects.filter(pk=registo.pk).update(user=user)
                _atribuir_grupos_irmao(user, registo.categoria)

                ok, canais = enviar_credenciais(registo, username, temp_password)
                if ok:
                    via = []
                    if canais.get('email'):
                        via.append('email')
                    if canais.get('sms'):
                        via.append('SMS')
                    messages.success(
                        request,
                        f'Utilizador "{username}" criado. Credenciais enviadas por {", ".join(via)}.',
                    )
                else:
                    messages.warning(
                        request,
                        f'Utilizador "{username}" criado, mas não foi possível enviar credenciais '
                        f'(verifique email/telefone ou contacte o administrador).',
                    )

            elif action == 'reenviar_credenciais' and registo.user is not None:
                temp_password = get_random_string(length=12)
                registo.user.set_password(temp_password)
                registo.user.save(update_fields=['password'])
                username = registo.user.username

                ok, canais = enviar_credenciais(registo, username, temp_password)
                if ok:
                    via = []
                    if canais.get('email'):
                        via.append('email')
                    if canais.get('sms'):
                        via.append('SMS')
                    messages.success(
                        request,
                        f'Credenciais reenviadas por {", ".join(via)} para "{username}".',
                    )
                elif canais.get('email') or canais.get('sms'):
                    messages.warning(
                        request,
                        f'Palavra-passe renovada para "{username}", mas nem todos os canais '
                        f'responderam (email={"sim" if canais.get("email") else "não"}, '
                        f'SMS={"sim" if canais.get("sms") else "não"}).',
                    )
                else:
                    messages.error(
                        request,
                        f'Palavra-passe renovada para "{username}", mas o envio falhou — '
                        f'verifique se o irmão tem email ou telefone registado.',
                    )

            return HttpResponseRedirect(
                reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador])
            )

        mandatos_irmao = (
            Mandato.objects
            .select_related('departamento')
            .filter(irmao_id=identificador)
            .order_by('departamento__designacao')
        )
        _contrib_qs = Dizimooferta.objects.filter(irmao_id=identificador)
        _contrib_agg = _contrib_qs.aggregate(
            total_historico=Sum('valor'),
            total_registos=Count('id'),
        )
        _contrib_ano_atual = date.today().year
        _contrib_total_ano = (
            _contrib_qs.filter(datacorrespondente__year=_contrib_ano_atual)
            .aggregate(total=Sum('valor'))['total'] or 0
        )
        _contrib_ultimo = _contrib_qs.order_by('-datacorrespondente').first()
        _contrib_moedas = list(_contrib_qs.values_list('moeda', flat=True).distinct())
        _contrib_moeda = _contrib_moedas[0] if len(_contrib_moedas) == 1 else ('MULTI' if _contrib_moedas else None)
        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'mandatos_irmao': mandatos_irmao,
            'pode_gerir_user': pode_gerir_user,
            'contrib_total_historico': _contrib_agg['total_historico'] or 0,
            'contrib_total_registos': _contrib_agg['total_registos'] or 0,
            'contrib_total_ano': _contrib_total_ano,
            'contrib_ultimo': _contrib_ultimo,
            'contrib_moeda': _contrib_moeda,
            'contrib_ano_atual': _contrib_ano_atual,
        }
    elif gestaoescolhida == 'pedidosaida':
        pode_aprovar = request.user.has_perm('sitetibl.change_pedidosaida')

        if request.method == 'POST' and pode_aprovar:
            action = request.POST.get('action', '').strip()
            irmao_logado = Irmao.objects.filter(user=request.user).first()

            if action == 'aprovar':
                registo.estado = 'aprovado'
                registo.estado_pagamento = 'aguardando'
                registo.aprovador = irmao_logado
                registo.observacao_aprovador = request.POST.get('observacao', '').strip()
                registo.data_aprovacao = now()
                _sincronizar_status_legado_pedidosaida(registo)
                registo.save()
                notificar_mudanca_estado_pedido(registo, 'aprovado', irmao_logado)
                messages.success(request, 'Pedido aprovado com sucesso.')

            elif action == 'rejeitar':
                obs = request.POST.get('observacao', '').strip()
                if not obs:
                    messages.error(request, 'É obrigatório indicar o motivo da rejeição.')
                else:
                    registo.estado = 'rejeitado'
                    registo.estado_pagamento = 'nao_aplicavel'
                    registo.aprovador = irmao_logado
                    registo.observacao_aprovador = obs
                    registo.data_aprovacao = now()
                    _sincronizar_status_legado_pedidosaida(registo)
                    registo.save()
                    notificar_mudanca_estado_pedido(registo, 'rejeitado', irmao_logado)
                    messages.success(request, 'Pedido rejeitado.')

            elif action == 'em_analise':
                registo.estado = 'em_analise'
                _sincronizar_status_legado_pedidosaida(registo)
                registo.save(update_fields=['estado', 'status_de_aprovacao', 'data_atualizacao'])
                notificar_mudanca_estado_pedido(registo, 'em_analise', irmao_logado)
                messages.info(request, 'Pedido marcado como "Em Análise".')

            elif action == 'marcar_pago':
                comprovativo = request.FILES.get('comprovativo')
                if not comprovativo:
                    messages.error(request, 'Anexe o comprovativo de pagamento.')
                else:
                    registo.estado_pagamento = 'pago'
                    registo.comprovativo_pagamento = comprovativo
                    registo.data_pagamento = now()
                    registo.save()
                    notificar_mudanca_estado_pedido(registo, 'pago', irmao_logado)
                    messages.success(request, 'Pagamento registado com sucesso.')

            return HttpResponseRedirect(
                reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador])
            )

        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'pode_aprovar': pode_aprovar,
        }
    elif gestaoescolhida == 'solicitacoes':
        irmao_logado = Irmao.objects.filter(user=request.user).first()
        pode_responder = request.user.has_perm('sitetibl.change_solicitacaointerdepartamental')
        historico = HistoricoSolicitacao.objects.filter(solicitacao=registo).select_related('responsavel').order_by('data')
        comentarios = ComentarioSolicitacao.objects.filter(solicitacao=registo).select_related('autor').order_by('data')

        if request.method == 'POST':
            action = request.POST.get('action', '').strip()

            # Comentário — qualquer utilizador com view permission pode comentar
            if action == 'comentar' and irmao_logado:
                texto = request.POST.get('comentario_texto', '').strip()
                if texto:
                    anexo_coment = request.FILES.get('comentario_anexo')
                    ComentarioSolicitacao.objects.create(
                        solicitacao=registo, autor=irmao_logado,
                        texto=texto, anexo=anexo_coment or '',
                    )
                    _notificar_comentario_solicitacao(registo, irmao_logado, texto)
                    messages.success(request, 'Comentário adicionado.')
                else:
                    messages.error(request, 'O comentário não pode estar vazio.')
                return HttpResponseRedirect(
                    reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador])
                )

            # Transições de estado — requer permissão change
            if pode_responder:
                estado_anterior = registo.estado
                anexo = request.FILES.get('documento_anexo')

                if action == 'em_analise' and registo.pode_transitar_para('em_analise'):
                    registo.estado = 'em_analise'
                    registo.save(update_fields=['estado', 'data_atualizacao'])
                    HistoricoSolicitacao.objects.create(
                        solicitacao=registo, estado_anterior=estado_anterior,
                        estado_novo='em_analise', responsavel=irmao_logado,
                        documento_anexo=anexo or '',
                    )
                    _notificar_solicitacao(registo, estado_anterior, 'em_analise', irmao_logado)
                    messages.info(request, 'Solicitação marcada como "Em Análise".')

                elif action == 'aprovar' and registo.pode_transitar_para('aprovado'):
                    obs = request.POST.get('justificacao', '').strip()
                    registo.estado = 'aprovado'
                    registo.responsavel_resposta = irmao_logado
                    registo.justificacao_resposta = obs
                    registo.data_resposta = now()
                    if registo.categoria == 'verba':
                        registo.estado_pagamento = 'aguardando'
                    registo.save()
                    HistoricoSolicitacao.objects.create(
                        solicitacao=registo, estado_anterior=estado_anterior,
                        estado_novo='aprovado', responsavel=irmao_logado, observacao=obs,
                        documento_anexo=anexo or '',
                    )
                    _notificar_solicitacao(registo, estado_anterior, 'aprovado', irmao_logado)
                    messages.success(request, 'Solicitação aprovada com sucesso.')

                elif action == 'rejeitar' and registo.pode_transitar_para('rejeitado'):
                    obs = request.POST.get('justificacao', '').strip()
                    if not obs:
                        messages.error(request, 'É obrigatório indicar o motivo da rejeição.')
                    else:
                        registo.estado = 'rejeitado'
                        registo.responsavel_resposta = irmao_logado
                        registo.justificacao_resposta = obs
                        registo.data_resposta = now()
                        registo.save()
                        HistoricoSolicitacao.objects.create(
                            solicitacao=registo, estado_anterior=estado_anterior,
                            estado_novo='rejeitado', responsavel=irmao_logado, observacao=obs,
                            documento_anexo=anexo or '',
                        )
                        _notificar_solicitacao(registo, estado_anterior, 'rejeitado', irmao_logado)
                        messages.success(request, 'Solicitação rejeitada.')

                elif action == 'concluir' and registo.pode_transitar_para('concluido'):
                    obs = request.POST.get('justificacao', '').strip()
                    registo.estado = 'concluido'
                    registo.data_conclusao = now()
                    registo.save()
                    HistoricoSolicitacao.objects.create(
                        solicitacao=registo, estado_anterior=estado_anterior,
                        estado_novo='concluido', responsavel=irmao_logado, observacao=obs,
                        documento_anexo=anexo or '',
                    )
                    _notificar_solicitacao(registo, estado_anterior, 'concluido', irmao_logado)
                    messages.success(request, 'Solicitação concluída.')

                elif action == 'registar_pagamento' and registo.estado == 'aprovado' and registo.categoria == 'verba':
                    obs = request.POST.get('justificacao', '').strip()
                    comprovativo = request.FILES.get('comprovativo_pagamento')
                    registo.estado_pagamento = 'pago'
                    registo.data_pagamento = now()
                    if comprovativo:
                        registo.comprovativo_pagamento = comprovativo
                    registo.save()
                    HistoricoSolicitacao.objects.create(
                        solicitacao=registo, estado_anterior=estado_anterior,
                        estado_novo='aprovado', responsavel=irmao_logado,
                        observacao=f'Pagamento registado. {obs}'.strip(),
                        documento_anexo=comprovativo or '',
                    )
                    _notificar_solicitacao(registo, estado_anterior, 'aprovado', irmao_logado)
                    messages.success(request, 'Pagamento registado com sucesso.')
                else:
                    messages.error(request, 'Transição de estado inválida.')

                return HttpResponseRedirect(
                    reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador])
                )

        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'pode_responder': pode_responder,
            'historico': historico,
            'comentarios': comentarios,
        }
    elif gestaoescolhida == 'casospastorais':
        irmao_logado = Irmao.objects.filter(user=request.user).first()
        # Confidencialidade: verificar acesso
        if registo.confidencial:
            is_pastor = request.user.is_superuser or request.user.groups.filter(name='Pastor').exists()
            is_envolvido = irmao_logado and (registo.responsavel == irmao_logado or registo.criado_por == irmao_logado)
            if not is_pastor and not is_envolvido:
                messages.error(request, 'Acesso negado. Este caso é confidencial.')
                return redirect('index')

        registos_acompanhamento = RegistoAcompanhamento.objects.filter(caso=registo).select_related('realizado_por').order_by('-data')
        form_registo = RegistoAcompanhamentoForm()

        if request.method == 'POST' and irmao_logado:
            action = request.POST.get('action', '').strip()

            if action == 'adicionar_registo':
                form_registo = RegistoAcompanhamentoForm(request.POST, request.FILES)
                if form_registo.is_valid():
                    novo_registo = form_registo.save(commit=False)
                    novo_registo.caso = registo
                    novo_registo.realizado_por = irmao_logado
                    novo_registo.save()
                    # Actualizar estado do caso se estiver aberto
                    if registo.estado == 'aberto':
                        registo.estado = 'em_acompanhamento'
                        registo.save(update_fields=['estado', 'data_atualizacao'])
                    _notificar_caso_pastoral(registo, irmao_logado, f'Novo registo: {novo_registo.get_tipo_contacto_display()}')
                    messages.success(request, 'Registo de acompanhamento adicionado.')
                    return HttpResponseRedirect(
                        reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador])
                    )

            elif action == 'resolver':
                registo.estado = 'resolvido'
                registo.save(update_fields=['estado', 'data_atualizacao'])
                _notificar_caso_pastoral(registo, irmao_logado, 'Caso marcado como resolvido')
                messages.success(request, 'Caso marcado como resolvido.')
                return HttpResponseRedirect(
                    reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador])
                )

            elif action == 'iniciar_acompanhamento':
                if registo.estado == 'aberto':
                    registo.estado = 'em_acompanhamento'
                    registo.save(update_fields=['estado', 'data_atualizacao'])
                    _notificar_caso_pastoral(registo, irmao_logado, 'Acompanhamento iniciado')
                    messages.success(request, 'Acompanhamento iniciado.')
                return HttpResponseRedirect(
                    reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador])
                )

            elif action == 'encerrar':
                registo.estado = 'encerrado'
                registo.data_encerramento = now()
                registo.save(update_fields=['estado', 'data_encerramento', 'data_atualizacao'])
                _notificar_caso_pastoral(registo, irmao_logado, 'Caso encerrado')
                messages.success(request, 'Caso encerrado.')
                return HttpResponseRedirect(
                    reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador])
                )

            elif action == 'reabrir':
                registo.estado = 'em_acompanhamento'
                registo.data_encerramento = None
                registo.save(update_fields=['estado', 'data_encerramento', 'data_atualizacao'])
                _notificar_caso_pastoral(registo, irmao_logado, 'Caso reaberto')
                messages.success(request, 'Caso reaberto.')
                return HttpResponseRedirect(
                    reverse('sitetibl:mostra_detalhe', args=[gestaoescolhida, identificador])
                )

        pode_gerir = request.user.has_perm('sitetibl.change_casopastoral')
        context = {
            'registoachado': registoachado,
            'gestaoescolhida': gestaoescolhida,
            'registos_acompanhamento': registos_acompanhamento,
            'form_registo': form_registo,
            'pode_gerir': pode_gerir,
        }
    else:
        context = {'registoachado' : registoachado, 'gestaoescolhida' : gestaoescolhida}
    return render(request, ficheirodetalhado, context)

def _eliminar_actividade_com_dependencias(actividade):
    """
    Elimina actividade (e ocorrências-filho) após limpar a tabela legacy
    sitetibl_escala_irmao_protocolo, que bloqueia CASCADE das escalas em MySQL.
    """
    actividade_ids = [actividade.id]
    actividade_ids.extend(
        Actividade.objects.filter(parent_event_id=actividade.id).values_list('id', flat=True)
    )
    escala_ids = list(
        Escala.objects.filter(actividade_id__in=actividade_ids).values_list('id', flat=True)
    )

    with transaction.atomic():
        if escala_ids:
            table = 'sitetibl_escala_irmao_protocolo'
            if table in connection.introspection.table_names():
                placeholders = ','.join(['%s'] * len(escala_ids))
                with connection.cursor() as cursor:
                    cursor.execute(
                        f'DELETE FROM {table} WHERE escala_id IN ({placeholders})',
                        escala_ids,
                    )
        actividade.delete()


@login_required
def mostraEliminacao(request, gestaoescolhida, id):
    LEGACY_GESTAO_MAP = {
        'entradabancos': 'entradas',
        'saidabancos': 'saidas',
        'entradascaixa': 'entradas',
        'saidascaixa': 'saidas',
    }
    if gestaoescolhida in LEGACY_GESTAO_MAP:
        return redirect('sitetibl:mostra_eliminacao', gestaoescolhida=LEGACY_GESTAO_MAP[gestaoescolhida], id=id)

    lista = {'irmaos':Irmao, 
             'ajudas':Ajuda, 
             'cestas': Cestabasica, 
             'bancos': Banco, 
             'contasbancarias' : Contabancaria, 
             'actividades' : Actividade, 
             'departamentos' : Departamento, 
             'entradas' : Entrada, 
             'saidas' : Saida, 
             'dizimosofertas' : Dizimooferta,
             'relatoriosemanalcelula' : RelatorioSemanalCelula, 
             'pedidosaida' : PedidoSaida,
             'orcamentodepartamento': OrcamentoDepartamento,
             'inventariopatrimonio': InventarioPatrimonio,
             'conteudoensino':ConteudoEnsino,
             'enviomensagem':EnvioMensagem,
             'escalas':Escala,
             'mandatos':Mandato,
             'solicitacoes':SolicitacaoInterdepartamental,
             'casospastorais':CasoPastoral,
             'visitantes':VisitanteRecorrente,
             'celulas':Celula,
             }
    model = lista.get(gestaoescolhida)
    if model is None:
        messages.error(request, f'Tipo de registo desconhecido: {gestaoescolhida}')
        return redirect('index')

    # ðŸ” verificação dinâmica
    perm = f'{model._meta.app_label}.delete_{model._meta.model_name}'
    if not request.user.has_perm(perm):
        messages.error(request, 'Acesso negado! Você não tem permissão para eliminar registros.')
        return redirect('index')

    registo = get_object_or_404(model, id=id)

    # ðŸ” Verificação de propriedade para actividades
    if gestaoescolhida == 'actividades':
        papel_elevado = request.user.has_perm('sitetibl.change_mandato')
        if not papel_elevado:
            pode_eliminar = (registo.criado_por is not None and registo.criado_por == request.user)
            if not pode_eliminar and registo.departamento_id:
                irmao_logado = Irmao.objects.filter(user=request.user).first()
                if irmao_logado:
                    pode_eliminar = Departamento.objects.filter(
                        Q(lider_departamento=irmao_logado) | Q(vice_lider_departamento=irmao_logado),
                        id=registo.departamento_id,
                    ).exists()
            if not pode_eliminar:
                messages.error(request, 'Só pode eliminar actividades que criou ou do seu departamento.')
                return redirect('index')

    if request.method == 'POST':
        try:
            if gestaoescolhida == 'actividades':
                _eliminar_actividade_com_dependencias(registo)
            else:
                registo.delete()
        except IntegrityError:
            logger.exception('Falha ao eliminar %s id=%s', gestaoescolhida, id)
            messages.error(
                request,
                'Não foi possível eliminar: existem registos associados que impedem a operação.',
            )
            next_url = request.POST.get('next', '')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('index')

        messages.success(request, 'Eliminação foi bem sucedida')
        next_url = request.POST.get('next', '')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect('index')

    # GET â†’ mostra confirmação
    next_url = request.GET.get('next', '')
    if next_url and not next_url.startswith('/'):
        next_url = ''
    return render(request, 'confirmar_eliminacao.html', {
        'registo': registo,
        'gestao': gestaoescolhida,
        'next': next_url,
    })

@login_required
def mostraCriacao(request, gestaoescolhida):
    LEGACY_GESTAO_MAP = {
        'entradabancos': 'entradas',
        'saidabancos': 'saidas',
        'entradascaixa': 'entradas',
        'saidascaixa': 'saidas',
    }
    if gestaoescolhida in LEGACY_GESTAO_MAP:
        return redirect('sitetibl:mostra_criacao', gestaoescolhida=LEGACY_GESTAO_MAP[gestaoescolhida])

    listaformularios = {'escalas' : EscalaForm, 
                        'mandatos': MandatoForm, 
                        'irmaos':IrmaoForm, 
                        'ajudas':AjudaForm, 
                        'cestas': CestabasicaForm, 
                        'bancos': BancoForm, 
                        'contasbancarias' : ContabancariaForm, 
                        'actividades' : ActividadeForm, 
                        'departamentos' : DepartamentoForm, 
                        'entradas' : EntradaForm, 
                        'saidas' : SaidaForm, 
                        'dizimosofertas' : DizimoofertaForm,
                        'relatoriosemanalcelula' : RelatorioSemanalCelulaForm, 
                        'pedidosaida':PedidoSaidaForm,
                        'orcamentodepartamento':OrcamentoDepartamentoForm,
                        'inventariopatrimonio': InventarioPatrimonioForm,
                        'conteudoensino':ConteudoEnsinoForm,
                        'enviomensagem':EnvioMensagemForm,
                        'solicitacoes':SolicitacaoForm,
                        'casospastorais':CasoPastoralForm,
                        'visitantes':VisitanteRecorrenteForm,
                        'celulas':CelulaForm,
                        }
    form_class = listaformularios.get(gestaoescolhida)
    if not form_class:
        messages.error(request, 'Tipo de formulário inválido.')
        return redirect('index')

    # ðŸ” MODEL CORRETO
    model = form_class._meta.model
    perm = f'{model._meta.app_label}.add_{model._meta.model_name}'

    if not request.user.has_perm(perm):
        messages.error(request, 'Acesso negado! Você não tem permissão criar novos registros.')
        return redirect('index')

    if request.method == 'POST':
        formulario = form_class(request.POST, request.FILES)
        if formulario.is_valid():

            # Escalas: selecção múltipla de irmãos — criar uma escala por irmão
            if gestaoescolhida == 'escalas':
                irmaos_ids = request.POST.getlist('irmaos_selecionados')
                if not irmaos_ids:
                    messages.error(request, 'Seleccione pelo menos um irmão.')
                else:
                    actividade = formulario.cleaned_data['actividade']
                    funcao = formulario.cleaned_data.get('funcao')
                    criados = 0
                    duplicados = 0
                    for iid in irmaos_ids:
                        irmao = Irmao.objects.filter(id=iid).first()
                        if not irmao:
                            continue
                        _, created = Escala.objects.get_or_create(
                            irmao=irmao, actividade=actividade, funcao=funcao,
                        )
                        if created:
                            criados += 1
                        else:
                            duplicados += 1
                    if criados > 0:
                        msg = f'{criados} escala(s) criada(s) com sucesso!'
                        if duplicados > 0:
                            msg += f' ({duplicados} já existia(m) e foram ignoradas)'
                        messages.success(request, msg)
                    else:
                        messages.warning(request, 'Todos os irmãos seleccionados já estavam escalados para esta actividade com esta função.')
                    return redirect(f'/tibl/actividades/detalhe/{actividade.id}/')

            obj = formulario.save(commit=False)

            # âš ï¸ Verificação de conflito de horário para actividades
            if gestaoescolhida == 'actividades':
                data = formulario.cleaned_data['data']
                inicio = formulario.cleaned_data['inicio']
                fim = formulario.cleaned_data['fim']
                conflitos = Actividade.objects.filter(
                    data=data, inicio__lt=fim, fim__gt=inicio
                )
                mesma_data_diferente = Actividade.objects.filter(
                    data=data
                ).exclude(inicio__lt=fim, fim__gt=inicio)
                if conflitos.exists():
                    primeiro = conflitos.first()
                    messages.error(
                        request,
                        f'Conflito de horário: já existe uma actividade "{primeiro.designacao}" '
                        f'das {primeiro.inicio} Ã s {primeiro.fim} neste dia com horário sobrepóvel.'
                    )
                    return render(request, 'actividades_form.html', {'formulario': formulario, 'is_update': False})
                elif mesma_data_diferente.exists():
                    messages.warning(
                        request,
                        'Já existe outra actividade neste dia com horário diferente. '
                        'Se for num local diferente, pode prosseguir normalmente.'
                    )

            # ðŸ“‹ Pedido de Saída: definir requerente e estado inicial antes do primeiro save
            if gestaoescolhida == 'pedidosaida':
                irmao_req = Irmao.objects.filter(user=request.user).first()
                if irmao_req:
                    obj.requerente = irmao_req
                obj.estado = 'pendente'
                obj.estado_pagamento = 'nao_aplicavel'

            # ðŸ“‹ Solicitação Interdepartamental: auto-preencher solicitante e dept
            if gestaoescolhida == 'solicitacoes':
                irmao_sol = Irmao.objects.filter(user=request.user).first()
                if not irmao_sol:
                    messages.error(request, 'O seu utilizador não está associado a nenhum registo de Irmão. Contacte o administrador.')
                    return render(request, gestaoescolhida + '.html', {'formulario': formulario, 'is_update': False})
                obj.solicitante = irmao_sol
                if not obj.departamento_solicitante_id:
                    depts = Departamento.objects.filter(
                        Q(lider_departamento=irmao_sol) | Q(vice_lider_departamento=irmao_sol)
                    )
                    if depts.count() == 1:
                        obj.departamento_solicitante = depts.first()
                obj.estado = 'pendente'

            # ðŸ“‹ Caso Pastoral: auto-preencher criado_por
            if gestaoescolhida == 'casospastorais':
                irmao_logado = Irmao.objects.filter(user=request.user).first()
                if irmao_logado:
                    obj.criado_por = irmao_logado
                if not obj.responsavel_id and irmao_logado:
                    obj.responsavel = irmao_logado

            obj.save()
            formulario.save_m2m()

            # ðŸ“‹ Solicitação: notificar líderes do departamento destinatário
            if gestaoescolhida == 'solicitacoes':
                HistoricoSolicitacao.objects.create(
                    solicitacao=obj, estado_anterior='',
                    estado_novo='pendente', responsavel=irmao_sol,
                )
                _notificar_solicitacao(obj, '', 'pendente', irmao_sol)

            # ðŸ‘¤ Regista o criador nas actividades
            if gestaoescolhida == 'actividades':
                obj.criado_por = request.user
                obj.save(update_fields=['criado_por'])

            # ðŸ“‹ Pedido de Saída: já definido antes do save, nada a fazer aqui
            if gestaoescolhida == 'pedidosaida':
                pass

            # Se for Irmão e o utilizador escolheu departamentos, criar Mandatos
            if gestaoescolhida == 'irmaos':
                departamentos = formulario.cleaned_data.get('departamentos')
                if departamentos:
                    for dep in departamentos:
                        Mandato.objects.get_or_create(
                            irmao=obj, departamento=dep,
                            defaults={'funcao': 'membro'},
                        )
            messages.success(request, 'Dados salvos com sucesso!')
            # Após criar uma escala, redirecionar para o detalhe da actividade
            if gestaoescolhida == 'escalas' and hasattr(obj, 'actividade_id') and obj.actividade_id:
                return redirect(f'/tibl/actividades/detalhe/{obj.actividade_id}/')
            if gestaoescolhida == 'solicitacoes':
                return redirect(reverse('sitetibl:mostra_detalhe', args=['solicitacoes', obj.id]))
            if gestaoescolhida == 'casospastorais':
                _notificar_caso_pastoral(obj, obj.criado_por, 'Novo caso pastoral criado')
                return redirect(reverse('sitetibl:mostra_detalhe', args=['casospastorais', obj.id]))
            if gestaoescolhida == 'visitantes':
                return redirect(reverse('sitetibl:mostra_gestao', args=['visitantes', 1]))
            return redirect('index')
        else:
            messages.error(request, 'Foram encontrados erros ao preencher o formulário')
    else:
        formulario = form_class()

    tmpl = 'actividades_form.html' if gestaoescolhida == 'actividades' else 'formulario_criacao.html'
    if gestaoescolhida == 'escalas':
        from collections import defaultdict
        todos_irmaos_esc = Irmao.objects.select_related('celula').order_by('nome', 'apelido')
        todas_funcoes_esc = Funcao.objects.select_related('departamento').order_by('departamento__designacao', 'designacao')
        departamentos_esc = Departamento.objects.order_by('designacao')
        _irmao_depts = defaultdict(list)
        for m in Mandato.objects.values('irmao_id', 'departamento_id'):
            _irmao_depts[m['irmao_id']].append(m['departamento_id'])
        return render(request, 'escalas_form.html', {
            'formulario': formulario,
            'todos_irmaos': todos_irmaos_esc,
            'todas_funcoes': todas_funcoes_esc,
            'departamentos': departamentos_esc,
            'irmao_depts_json': json.dumps({str(k): v for k, v in _irmao_depts.items()}),
        })
    return render(request, tmpl, {'formulario': formulario, 'is_update': False})

@login_required
def encontraIrmao(request):
    nomev = request.GET.get('nomev', '').strip()
    apelidov = request.GET.get('apelidov', '').strip()
    municipiov = request.GET.get('municipiov', '').strip()
    bairrov = request.GET.get('bairrov', '').strip()
    categoriav = request.GET.get('categoriav', '').strip()
    profissaov = request.GET.get('profissaov', '').strip()
    pagina = request.GET.get('pagina', '1')
    kwargs= {'nome__icontains':nomev, 'apelido__icontains' : apelidov, 'bairro__icontains' : bairrov}
    if profissaov:
        kwargs['profissao__icontains'] = profissaov
    if municipiov and municipiov != '0':
        kwargs['municipio_id'] = municipiov
    if categoriav:
        kwargs['categoria'] = categoriav
    resultado = Irmao.objects.select_related('celula', 'localcongregacao', 'provincia', 'municipio').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']

    return render(request,'irmaosfiltrados.html', {'bb': paginaresultado, 'dd': cc[:-1] })

@login_required
def encontraRelatorioSemanalCelula(request):
    nomev = request.GET['nomev']
    liderv = request.GET['liderv']
    localv = request.GET['localv']
    temav = request.GET['temav']
    kwargs= {'nome_celula__icontains':nomev, 
             'lider_responsavel__icontains' : liderv, 
             'local_reuniao__icontains' : localv, 
             'tema_palavra__icontains' : temav }
    pagina= request.GET['pagina']
    resultado = RelatorioSemanalCelula.objects.select_related('nome_celula', 'lider_responsavel').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']

    return render(request,'relatoriosemanalcelulafiltrados.html', {'bb': paginaresultado, 'dd': cc[:-1] })

@login_required
def encontraPedidoSaida(request):
    nomev = request.GET['projectov']
    liderv = request.GET['montantev']
    localv = request.GET['ibanv']
    kwargs= {'projecto__icontains':nomev, 
             'montante__icontains' : liderv, 
             'iban__icontains' : localv, 
              }
    pagina= request.GET['pagina']
    resultado = PedidoSaida.objects.select_related('departamento', 'requerente', 'status_de_aprovacao', 'aprovador').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']

    return render(request,'pedidosaidafiltrados.html', {'bb': paginaresultado, 'dd': cc[:-1] })

@login_required
def encontraContasbancarias(request):
    nomev = request.GET.get('nomev', '').strip()
    apelidov = request.GET.get('apelidov', '').strip()
    bancov = request.GET.get('bancov', '').strip()
    kwargs = {
        'proprietario__nome__icontains': nomev,
        'proprietario__apelido__icontains': apelidov,
        'banco__designacao__icontains': bancov,
        'is_active': True,
    }
    resultado = Contabancaria.objects.filter(**kwargs)
    return render(request,'contasbancariasfiltradas.html', {'bb': resultado })


@login_required
def inativaContabancaria(request, id):
    if not request.user.has_perm('sitetibl.change_contabancaria'):
        messages.error(request, 'Acesso negado para inativar conta bancária.')
        return redirect('index')

    conta = get_object_or_404(Contabancaria, id=id)
    conta.is_active = False
    conta.save(update_fields=['is_active'])
    messages.success(request, f'Conta {conta.numeroconta} inativada com sucesso.')
    return redirect(f'/tibl/contasbancarias/detalhe/{id}/')


@login_required
def reativaContabancaria(request, id):
    if not request.user.has_perm('sitetibl.change_contabancaria'):
        messages.error(request, 'Acesso negado para reativar conta bancária.')
        return redirect('index')

    conta = get_object_or_404(Contabancaria, id=id)
    conta.is_active = True
    conta.save(update_fields=['is_active'])
    messages.success(request, f'Conta {conta.numeroconta} reativada com sucesso.')
    return redirect(f'/tibl/contasbancarias/detalhe/{id}/')


@login_required
def contasbancariasinativas(request):
    pagina = request.GET.get('pagina', 1)
    resultado = Contabancaria.objects.select_related('banco', 'proprietario', 'instituicao').filter(is_active=False).order_by('id')
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    return render(request, 'contasbancariasinativas.html', {
        'bb': paginaresultado,
        'total_inativas': resultado.count(),
    })




def _desenhar_rodape_pdf(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 9)
    canvas_obj.setFillColor(colors.HexColor('#666666'))
    canvas_obj.drawRightString(doc.pagesize[0] - 40, 20, f'Pagina {canvas_obj.getPageNumber()}')
    canvas_obj.restoreState()


def _get_relatorio_ofertas_por_tipo_context(params):
    q = params.get('q', '').strip()
    mes = params.get('mes', '').strip()
    ano = params.get('ano', '').strip()
    datainicio = params.get('datainicio', '').strip()
    datafim = params.get('datafim', '').strip()

    filtros = {}
    if mes:
        filtros['datacorrespondente__month'] = mes
    if ano:
        filtros['datacorrespondente__year'] = ano
    if datainicio:
        filtros['datacorrespondente__gte'] = datainicio
    if datafim:
        filtros['datacorrespondente__lte'] = datafim

    queryset = Dizimooferta.objects.select_related('tipooferta', 'irmao').filter(**filtros)
    if q:
        queryset = queryset.filter(
            Q(tipooferta__designacao__icontains=q)
            | Q(irmao__nome__icontains=q)
            | Q(irmao__apelido__icontains=q)
            | Q(irmao__email__icontains=q)
        )

    reporte = list(
        queryset.values('tipooferta__designacao', 'moeda')
        .annotate(total=Sum('valor'), count=Count('id'))
        .order_by('-total', 'tipooferta__designacao')
    )

    total_geral = queryset.aggregate(total=Sum('valor'))['total'] or 0
    moedas_distintas = list(queryset.values_list('moeda', flat=True).distinct())
    moeda_resumo = moedas_distintas[0] if len(moedas_distintas) == 1 else 'MULTI'

    return {
        'reporte': reporte,
        'q': q,
        'mes': mes,
        'ano': ano,
        'datainicio': datainicio,
        'datafim': datafim,
        'total_geral': total_geral,
        'moeda_resumo': moeda_resumo,
        'query_string': params.urlencode(),
    }


@login_required
def insightsdizimosofertas(request):
    from django.core.exceptions import PermissionDenied
    if not request.user.has_perm('sitetibl.view_dizimooferta'):
        raise PermissionDenied

    ano_sel = int(request.GET.get('anov', date.today().year))
    qs_ano = Dizimooferta.objects.filter(datacorrespondente__year=ano_sel)

    # Top 15 contributors
    top_contribuintes = list(
        qs_ano.values('irmao_id', 'irmao__nome', 'irmao__apelido')
        .annotate(total=Sum('valor'), registos=Count('id'))
        .order_by('-total')[:15]
    )

    # Monthly trend
    tendencia_raw = list(
        qs_ano
        .annotate(mes=TruncMonth('datacorrespondente'))
        .values('mes')
        .annotate(total=Sum('valor'), contribuintes=Count('irmao_id', distinct=True))
        .order_by('mes')
    )
    MESES_PT = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    tendencia = [
        {
            'mes_label': MESES_PT[t['mes'].month - 1],
            'total': float(t['total'] or 0),
            'contribuintes': t['contribuintes'],
        }
        for t in tendencia_raw
    ]

    # By tipo
    por_tipo = list(
        qs_ano.values('tipooferta__designacao')
        .annotate(total=Sum('valor'), registos=Count('id'))
        .order_by('-total')
    )

    # Non-contributors (baptized members with no record this year)
    contribuintes_ids = set(qs_ano.values_list('irmao_id', flat=True).distinct())
    nao_contribuintes = (
        Irmao.objects
        .filter(batizado=True)
        .exclude(id__in=contribuintes_ids)
        .order_by('nome', 'apelido')
    )

    # Summary KPIs
    total_baptizados = Irmao.objects.filter(batizado=True).count()
    total_contribuintes_ano = len(contribuintes_ids)
    taxa_participacao = round(total_contribuintes_ano / total_baptizados * 100) if total_baptizados else 0
    total_arrecadado = float(qs_ano.aggregate(t=Sum('valor'))['t'] or 0)

    anos_disponiveis = (
        Dizimooferta.objects
        .dates('datacorrespondente', 'year', order='DESC')
    )

    context = {
        'ano_sel': ano_sel,
        'anos_disponiveis': anos_disponiveis,
        'top_contribuintes': top_contribuintes,
        'tendencia': tendencia,
        'tendencia_json': json.dumps(tendencia),
        'por_tipo': por_tipo,
        'nao_contribuintes': nao_contribuintes,
        'total_baptizados': total_baptizados,
        'total_contribuintes_ano': total_contribuintes_ano,
        'taxa_participacao': taxa_participacao,
        'total_arrecadado': total_arrecadado,
    }
    return render(request, 'insightsdizimosofertas.html', context)


@login_required
def relatorioofertasportipo(request):
    return render(request, 'relatorioofertasportipo.html', _get_relatorio_ofertas_por_tipo_context(request.GET))


@login_required
def relatorioofertasportipo_pdf(request):
    context = _get_relatorio_ofertas_por_tipo_context(request.GET)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_ofertas_por_tipo.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatorio de Ofertas por Tipo",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'RelatorioHeader',
        parent=styles['Heading2'],
        alignment=1,
        textColor=colors.HexColor('#1f3d1f'),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'RelatorioSubtitle',
        parent=styles['Normal'],
        alignment=1,
        textColor=colors.HexColor('#4f4f4f'),
        fontSize=9,
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        'RelatorioMeta',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#555555'),
        leading=12,
        spaceAfter=4,
    )
    elements = []

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'fotos', '2022', 'cba.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Paragraph("<br/>", styles['Normal']))
    elements.append(Paragraph("<b>Terceira Igreja Baptista de Luanda</b>", header_style))
    elements.append(Paragraph("Sistema TIBL | Relatorio Financeiro", subtitle_style))
    elements.append(Paragraph("<b>Relatorio de Ofertas por Tipo</b>", styles['Title']))

    filtros_aplicados = []
    if context['q']:
        filtros_aplicados.append(f"Pesquisa: {context['q']}")
    if context['mes']:
        filtros_aplicados.append(f"Mes: {MESES.get(context['mes'], context['mes'])}")
    if context['ano']:
        filtros_aplicados.append(f"Ano: {context['ano']}")
    if context['datainicio']:
        filtros_aplicados.append(f"De: {context['datainicio']}")
    if context['datafim']:
        filtros_aplicados.append(f"Ate: {context['datafim']}")
    periodo = 'Todos os periodos'
    if context['datainicio'] and context['datafim']:
        periodo = f"{context['datainicio']} ate {context['datafim']}"
    elif context['datainicio']:
        periodo = f"A partir de {context['datainicio']}"
    elif context['datafim']:
        periodo = f"Ate {context['datafim']}"
    elif context['mes'] and context['ano']:
        periodo = f"{MESES.get(context['mes'], context['mes'])} de {context['ano']}"
    elif context['mes']:
        periodo = MESES.get(context['mes'], context['mes'])
    elif context['ano']:
        periodo = f"Ano de {context['ano']}"

    total_registos = sum(row['count'] for row in context['reporte'])
    moeda_label = 'Multimoeda' if context['moeda_resumo'] == 'MULTI' else context['moeda_resumo']

    elements.append(Paragraph(f"<b>Periodo:</b> {periodo}", meta_style))
    elements.append(Paragraph(f"<b>Emitido em:</b> {date.today().strftime('%d/%m/%Y')}", meta_style))
    if filtros_aplicados:
        elements.append(Paragraph(f"<b>Filtros:</b> {' | '.join(filtros_aplicados)}", meta_style))
    else:
        elements.append(Paragraph("<b>Filtros:</b> Nenhum filtro adicional aplicado", meta_style))

    resumo = Table([
        ['Tipos de oferta', 'Total arrecadado', 'Moeda', 'Registos'],
        [str(len(context['reporte'])), f"{context['total_geral']:,.2f}", moeda_label, str(total_registos)],
    ], colWidths=[110, 140, 90, 90])
    resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9ead3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f3d1f')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f4fbf1')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a8c79d')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(Paragraph("<br/>", styles['Normal']))
    elements.append(resumo)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    data = [['Tipo de Oferta', 'Moeda', 'Total Arrecadado', 'N. Registos']]
    for row in context['reporte']:
        data.append([
            row['tipooferta__designacao'] or 'Geral',
            row['moeda'],
            f"{row['total']:,.2f}",
            str(row['count'])
        ])

    if len(data) == 1:
        data.append(['Nenhum registo encontrado', '-', '-', '-'])

    data.append([
        'Total Geral',
        'Multimoeda' if context['moeda_resumo'] == 'MULTI' else context['moeda_resumo'],
        f"{context['total_geral']:,.2f}",
        ''
    ])

    table = LongTable(data, colWidths=[180, 70, 120, 80], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
        ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f3e0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    doc.build(elements, onFirstPage=_desenhar_rodape_pdf, onLaterPages=_desenhar_rodape_pdf)
    return response


@login_required
def balanco_financeiro(request):
    from django.core.exceptions import PermissionDenied
    from .financeiro_utils import build_balanco_financeiro

    if not (
        request.user.has_perm('sitetibl.view_dizimooferta')
        or request.user.has_perm('sitetibl.view_entrada')
        or request.user.has_perm('sitetibl.view_saida')
    ):
        raise PermissionDenied

    context = build_balanco_financeiro(request.GET)
    return render(request, 'balancofinanceiro.html', context)


@login_required
def balanco_financeiro_excel(request):
    from django.core.exceptions import PermissionDenied
    from .financeiro_utils import build_balanco_financeiro, gerar_excel_balanco_financeiro

    if not (
        request.user.has_perm('sitetibl.view_dizimooferta')
        or request.user.has_perm('sitetibl.view_entrada')
        or request.user.has_perm('sitetibl.view_saida')
    ):
        raise PermissionDenied

    context = build_balanco_financeiro(request.GET)
    buffer = gerar_excel_balanco_financeiro(context)

    response = HttpResponse(
        buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    from datetime import datetime
    ts = datetime.now().strftime('%Y%m%d_%H%M')
    ano_str = context.get('ano', 'todos') or 'todos'
    nome_ficheiro = f"balanco_financeiro_{context['periodo']}_{ano_str}_{ts}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{nome_ficheiro}"'
    return response


@login_required
def cartao_protocolo_pdf(request, actividade_id):
    """Gera PDF com credenciais individuais — 2 por folha A4."""
    actividade = get_object_or_404(Actividade, id=actividade_id)
    todas_escalas = (
        Escala.objects.filter(actividade=actividade)
        .select_related('irmao', 'irmao__celula', 'funcao')
        .prefetch_related('irmao_protocolo', 'irmao_protocolo__celula')
    )

    if not todas_escalas.exists():
        messages.error(request, 'Esta actividade não possui escalas associadas.')
        return redirect(reverse('sitetibl:mostra_detalhe', args=['actividades', actividade_id]))

    membros_funcoes = []
    seen = set()
    for esc in todas_escalas:
        funcao_str = str(esc.funcao) if esc.funcao else 'Participante'
        if esc.eh_protocolo:
            for membro in esc.irmao_protocolo.all():
                if membro.id not in seen:
                    seen.add(membro.id)
                    membros_funcoes.append((membro, funcao_str))
        else:
            membro = esc.irmao
            if membro.id not in seen:
                seen.add(membro.id)
                membros_funcoes.append((membro, funcao_str))

    if not membros_funcoes:
        messages.error(request, 'Nenhum membro encontrado nas escalas desta actividade.')
        return redirect(reverse('sitetibl:mostra_detalhe', args=['actividades', actividade_id]))

    membros_funcoes.sort(key=lambda x: x[0].nome)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="cartoes_protocolo_{actividade_id}_{actividade.data}.pdf"'
    )

    page_w, page_h = A4
    margin  = 28
    gap     = 20
    card_w  = page_w - 2 * margin
    card_h  = (page_h - 2 * margin - gap) / 2

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'fotos', '2022', 'cba.png')

    primary      = colors.HexColor('#1e3a5f')
    primary_dark = colors.HexColor('#0f2044')
    gold         = colors.HexColor('#d97706')
    gold_light   = colors.HexColor('#fef3c7')
    gold_border  = colors.HexColor('#fde68a')
    light_blue   = colors.HexColor('#93c5fd')
    pale_blue    = colors.HexColor('#bfdbfe')
    muted        = colors.HexColor('#6b7280')
    ink          = colors.HexColor('#1f2937')
    divider_col  = colors.HexColor('#e2e8f0')

    HEADER_H = 80
    FOOTER_H = 46
    ACCENT_W = 6
    BODY_PAD = ACCENT_W + 15
    # max text width available in card body
    MAX_TXT  = card_w - BODY_PAD - 16

    def _fit_str(canvas_obj, text, font, size, max_w):
        """Truncate text with ellipsis until it fits within max_w."""
        t = text
        while canvas_obj.stringWidth(t, font, size) > max_w and len(t) > 1:
            t = t[:-1]
        if t != text:
            t = t[:-1] + '…'
        return t

    def _label_value(c, lx, ly, label, value, label_w=68):
        lbl_font, val_font, sz = 'Helvetica-Bold', 'Helvetica', 9
        c.setFont(lbl_font, sz)
        c.setFillColor(primary)
        c.drawString(lx, ly, label)
        c.setFont(val_font, sz)
        c.setFillColor(ink)
        val_str = _fit_str(c, str(value), val_font, sz, MAX_TXT - label_w)
        c.drawString(lx + label_w, ly, val_str)

    def _draw_card(c, x, card_y, membro, funcao_str, idx):

        # ── Card background ───────────────────────────────────────────────
        c.setFillColor(colors.white)
        c.setStrokeColor(primary)
        c.setLineWidth(1.5)
        c.roundRect(x, card_y, card_w, card_h, 10, fill=1, stroke=1)

        # ── Header band ───────────────────────────────────────────────────
        header_top = card_y + card_h
        c.setFillColor(primary_dark)
        c.roundRect(x, header_top - HEADER_H, card_w, HEADER_H, 10, fill=1, stroke=0)
        c.rect(x, header_top - HEADER_H, card_w, HEADER_H // 2, fill=1, stroke=0)

        # Gold accent under header
        c.setFillColor(gold)
        c.rect(x, header_top - HEADER_H - 3, card_w, 3, fill=1, stroke=0)

        # Logo
        if os.path.exists(logo_path):
            try:
                logo_sz = 58
                c.drawImage(
                    logo_path,
                    x + 12,
                    header_top - HEADER_H + (HEADER_H - logo_sz) / 2,
                    width=logo_sz, height=logo_sz,
                    preserveAspectRatio=True, mask='auto',
                )
            except Exception:
                pass

        # Title & church name
        title_x = x + 82
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 17)
        c.drawString(title_x, header_top - 22, 'CREDENCIAL')

        c.setFont('Helvetica', 9)
        c.setFillColor(light_blue)
        c.drawString(title_x, header_top - 35, 'Terceira Igreja Batista de Luanda')

        # Thin separator inside header
        c.setStrokeColor(colors.HexColor('#334e7a'))
        c.setLineWidth(0.6)
        c.line(title_x, header_top - 44, x + card_w - 14, header_top - 44)

        # Activity name inside header
        act_str = str(actividade.designacao)
        act_fitted = _fit_str(c, act_str, 'Helvetica', 8, card_w - 82 - 100 - 14)
        c.setFont('Helvetica', 8)
        c.setFillColor(pale_blue)
        c.drawString(title_x, header_top - 56, act_fitted)

        # Date / time / local — top right
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(colors.white)
        c.drawRightString(x + card_w - 12, header_top - 17, actividade.data.strftime('%d/%m/%Y'))
        c.setFont('Helvetica', 8.5)
        c.setFillColor(pale_blue)
        c.drawRightString(
            x + card_w - 12, header_top - 29,
            f'{actividade.inicio.strftime("%H:%M")} — {actividade.fim.strftime("%H:%M")}',
        )
        local_str = _fit_str(c, str(actividade.localactividade or 'Sede'), 'Helvetica', 8, 110)
        c.setFont('Helvetica', 8)
        c.setFillColor(light_blue)
        c.drawRightString(x + card_w - 12, header_top - 40, local_str)

        # ── Left gold accent stripe (body only) ───────────────────────────
        body_bot = card_y + FOOTER_H
        body_h   = card_h - HEADER_H - 3 - FOOTER_H
        c.setFillColor(gold)
        c.rect(x, body_bot, ACCENT_W, body_h, fill=1, stroke=0)

        # ── Member name ───────────────────────────────────────────────────
        body_start_y = card_y + card_h - HEADER_H - 3
        nome_completo = f'{membro.nome} {membro.apelido}'
        name_y   = body_start_y - 32
        font_sz  = 22
        while c.stringWidth(nome_completo, 'Helvetica-Bold', font_sz) > MAX_TXT and font_sz > 13:
            font_sz -= 1
        c.setFillColor(primary)
        c.setFont('Helvetica-Bold', font_sz)
        c.drawString(x + BODY_PAD, name_y, nome_completo)

        # Gold underline
        name_w = c.stringWidth(nome_completo, 'Helvetica-Bold', font_sz)
        c.setStrokeColor(gold)
        c.setLineWidth(2)
        c.line(x + BODY_PAD, name_y - 5, x + BODY_PAD + name_w, name_y - 5)

        # ── Function badge ────────────────────────────────────────────────
        badge_y = name_y - 30
        func_fitted = _fit_str(c, funcao_str, 'Helvetica-Bold', 10, MAX_TXT - 20)
        badge_w = c.stringWidth(func_fitted, 'Helvetica-Bold', 10) + 20
        c.setFillColor(gold_light)
        c.setStrokeColor(gold_border)
        c.setLineWidth(0.8)
        c.roundRect(x + BODY_PAD, badge_y - 5, badge_w, 20, 4, fill=1, stroke=1)
        c.setFillColor(gold)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(x + BODY_PAD + 10, badge_y + 3, func_fitted)

        # ── Divider ───────────────────────────────────────────────────────
        div_y = badge_y - 16
        c.setStrokeColor(divider_col)
        c.setLineWidth(0.6)
        c.line(x + ACCENT_W + 10, div_y, x + card_w - 14, div_y)

        # ── Detail fields ─────────────────────────────────────────────────
        det_y = div_y - 14
        LINE  = 15

        _label_value(c, x + BODY_PAD, det_y, 'Actividade:', act_str)
        det_y -= LINE

        if membro.celula:
            _label_value(c, x + BODY_PAD, det_y, 'Célula:', str(membro.celula))
            det_y -= LINE

        if membro.telefone:
            _label_value(c, x + BODY_PAD, det_y, 'Telefone:', membro.telefone)
            det_y -= LINE

        if hasattr(membro, 'email') and membro.email:
            _label_value(c, x + BODY_PAD, det_y, 'Email:', membro.email)

        # ── Footer zone ───────────────────────────────────────────────────
        footer_top = card_y + FOOTER_H
        c.setStrokeColor(divider_col)
        c.setLineWidth(0.6)
        c.line(x + 10, footer_top, x + card_w - 10, footer_top)

        sig1_cx   = x + card_w * 0.27
        sig2_cx   = x + card_w * 0.73
        sig_line_y = card_y + FOOTER_H - 16

        c.setStrokeColor(ink)
        c.setLineWidth(0.7)
        c.line(sig1_cx - 65, sig_line_y + 14, sig1_cx + 65, sig_line_y + 14)
        c.line(sig2_cx - 65, sig_line_y + 14, sig2_cx + 65, sig_line_y + 14)

        c.setFont('Helvetica', 8)
        c.setFillColor(ink)
        c.drawCentredString(sig1_cx, sig_line_y + 3, 'Líder Responsável')
        c.drawCentredString(sig2_cx, sig_line_y + 3, 'Responsável da Actividade')

        # Card number
        c.setFont('Helvetica', 7)
        c.setFillColor(muted)
        c.drawString(x + 12, card_y + 8, f'N.º {idx + 1:02d}  ·  TIBL  ·  {actividade.data.strftime("%d/%m/%Y")}')

        # Bottom gold bar
        c.setFillColor(gold)
        c.roundRect(x, card_y, card_w, 5, 3, fill=1, stroke=0)

    c = canvas.Canvas(response, pagesize=A4)

    for idx, (membro, funcao_str) in enumerate(membros_funcoes):
        if idx > 0 and idx % 2 == 0:
            c.showPage()
        slot   = idx % 2
        card_y = (page_h - margin - card_h) if slot == 0 else margin
        _draw_card(c, margin, card_y, membro, funcao_str, idx)

    c.save()
    return response


_TELCOSMS_URL = 'https://telcosms.co.ao/send_message'


def _enviar_sms_telco(telefone, texto):
    """Envia um SMS individual via TelcoSMS. Regista falhas no logger sem lançar excepção."""
    sms_data = {
        'message': {
            'api_key_app': _telcosms_api_key(),
            'phone_number': telefone,
            'message_body': texto,
        }
    }
    try:
        resp = requests.post(_TELCOSMS_URL, json=sms_data, timeout=10)
        if resp.status_code == 200:
            logger.info('SMS enviado para %s', telefone)
        else:
            logger.error('Falha SMS para %s — status %s: %s', telefone, resp.status_code, resp.text)
    except Exception as e:
        logger.error('Erro SMS para %s: %s', telefone, e)


def _notificar_protocolo_escalado(irmao, escala, actividade):
    """Envia email e SMS ao membro escalado para o protocolo."""
    funcao_str = str(escala.funcao) if escala.funcao else 'Protocolo'
    local_str  = str(actividade.localactividade or 'Sede')
    data_str   = actividade.data.strftime('%d/%m/%Y')
    hora_str   = f'{actividade.inicio.strftime("%H:%M")} — {actividade.fim.strftime("%H:%M")}'
    act_str    = str(actividade.designacao)
    dept_str   = str(escala.funcao.departamento) if escala.funcao and escala.funcao.departamento else ''

    if irmao.email:
        try:
            context = {
                'nome': irmao.nome,
                'apelido': irmao.apelido,
                'actividade': act_str,
                'data': data_str,
                'hora': hora_str,
                'local': local_str,
                'funcao': funcao_str,
                'departamento': dept_str,
            }
            html_content = render_to_string('emails/email_protocolo_escalado.html', context)
            msg = EmailMultiAlternatives(
                subject=f'Escala de Protocolo — {act_str} ({data_str})',
                body=(
                    f'Olá {irmao.nome}, foi escalado(a) para o Protocolo da actividade '
                    f'"{act_str}" em {data_str} às {hora_str}. Local: {local_str}.'
                ),
                from_email=None,
                to=[irmao.email],
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            logger.info('Email de protocolo enviado para %s', irmao.email)
        except Exception as e:
            logger.error('Falha ao enviar email de protocolo para %s: %s', irmao.email, e)

    if irmao.telefone:
        sms_texto = (
            f'TIBL — Foi escalado(a) para o Protocolo da actividade "{act_str}" '
            f'em {data_str} as {hora_str}. Local: {local_str}. Deus abencoe!'
        )
        _enviar_sms_telco(irmao.telefone, sms_texto)


@login_required
def substituir_membro_protocolo(request, escala_id, irmao_id):
    """Substitui um membro numa escala (protocolo M2M ou normal FK) e notifica o novo membro."""
    from django.core.exceptions import PermissionDenied
    if not request.user.has_perm('sitetibl.change_escala'):
        raise PermissionDenied

    escala          = get_object_or_404(Escala, id=escala_id)
    membro_original = get_object_or_404(Irmao, id=irmao_id)
    actividade      = escala.actividade

    if escala.eh_protocolo:
        if not escala.irmao_protocolo.filter(id=irmao_id).exists():
            messages.error(request, 'Este membro não faz parte desta escala.')
            return redirect(reverse('sitetibl:mostra_detalhe', args=['actividades', actividade.id]))
        ja_escalados_ids = set(escala.irmao_protocolo.values_list('id', flat=True))
    else:
        if escala.irmao_id != int(irmao_id):
            messages.error(request, 'Este membro não faz parte desta escala.')
            return redirect(reverse('sitetibl:mostra_detalhe', args=['actividades', actividade.id]))
        ja_escalados_ids = set(
            Escala.objects.filter(actividade=actividade).values_list('irmao_id', flat=True)
        )

    irmaos_disponiveis = (
        Irmao.objects.select_related('celula')
        .exclude(id__in=ja_escalados_ids)
        .order_by('nome', 'apelido')
    )

    if request.method == 'GET':
        return render(request, 'substituir_protocolo.html', {
            'escala': escala,
            'membro_original': membro_original,
            'irmaos_disponiveis': irmaos_disponiveis,
        })

    novo_irmao_id = request.POST.get('novo_irmao_id', '').strip()
    if not novo_irmao_id:
        return render(request, 'substituir_protocolo.html', {
            'escala': escala,
            'membro_original': membro_original,
            'irmaos_disponiveis': irmaos_disponiveis,
            'form_error': 'Seleccione um irmão para efectuar a substituição.',
        })

    try:
        novo_irmao = Irmao.objects.get(id=int(novo_irmao_id))
    except (Irmao.DoesNotExist, ValueError):
        return render(request, 'substituir_protocolo.html', {
            'escala': escala,
            'membro_original': membro_original,
            'irmaos_disponiveis': irmaos_disponiveis,
            'form_error': 'Irmão seleccionado não encontrado.',
        })

    if escala.eh_protocolo:
        escala.irmao_protocolo.remove(membro_original)
        escala.irmao_protocolo.add(novo_irmao)
        if escala.irmao_id == membro_original.id:
            escala.irmao = novo_irmao
            escala.save(update_fields=['irmao'])
    else:
        escala.irmao = novo_irmao
        escala.save(update_fields=['irmao'])

    _notificar_protocolo_escalado(novo_irmao, escala, actividade)

    messages.success(
        request,
        f'{membro_original.nome} {membro_original.apelido} substituído(a) por '
        f'{novo_irmao.nome} {novo_irmao.apelido}. Notificação enviada.',
    )
    return redirect(reverse('sitetibl:mostra_detalhe', args=['actividades', actividade.id]))


@login_required
def visualizar_recibo_dizimo(request, dizimo_id):
    messages.warning(request, f'Recibo de dízimo #{dizimo_id} não está disponível nesta branch.')
    return redirect('index')


@login_required
def gerar_recibo_dizimo(request, dizimo_id):
    messages.warning(request, f'Geração de recibo de dízimo #{dizimo_id} não está disponível nesta branch.')
    return redirect('index')

@login_required
def encontraAjudas(request):
    nomev = request.GET['nomev']
    apelidov = request.GET['apelidov']
    tipoajudav = int(request.GET['tipoajudav'])
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'beneficiario__nome__icontains':nomev, 'beneficiario__apelido__icontains' : apelidov,'ajuda_id' : tipoajudav,'data__month':mesv, 'data__year' : anov}
    if (mesv == '0'):
        del kwargs['data__month']
    if (anov == '0'):
        del kwargs['data__year']
    if (tipoajudav == 0):
        del kwargs['ajuda_id']
    resultado = Ajuda.objects.select_related('beneficiario', 'patrocinador', 'cesta').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'ajudasfiltradas.html', {'bb':paginaresultado})

@login_required
def encontraCestas(request):
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'codigo__month':mesv, 'codigo__year' : anov}
    if (mesv == '0'):
        del kwargs['codigo__month']
    if (anov == '0'):
        del kwargs['codigo__year']
    resultado = Cestabasica.objects.select_related('saida').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'cestasfiltradas.html', {'bb':paginaresultado})

@login_required
def encontraCelulas(request):
    nomev = request.GET.get('nomev', '').strip()
    liderv = request.GET.get('liderv', '').strip()
    localv = request.GET.get('localv', '').strip()
    pagina = request.GET.get('pagina', 1)
    from django.db.models import Count
    resultado = Celula.objects.select_related('lider', 'vice_lider').annotate(
        total_relatorios=Count('relatorios')
    )
    if nomev:
        resultado = resultado.filter(designacao__icontains=nomev)
    if liderv:
        resultado = resultado.filter(
            models.Q(lider__nome__icontains=liderv) | models.Q(lider__apelido__icontains=liderv)
        )
    if localv:
        resultado = resultado.filter(local_reuniao__icontains=localv)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    return render(request, 'celulasfiltradas.html', {'bb': paginaresultado})

@login_required
def encontraActividades(request):
    nomev = request.GET.get('nomev', '').strip()
    apelidov = request.GET.get('apelidov', '').strip()
    actividadev = request.GET.get('actividadev', '0')
    funcaov = request.GET.get('funcaov', '0')
    mesv = request.GET.get('mesv', '0')
    anov = request.GET.get('anov', '0')
    pagina = request.GET.get('pagina', 1)
    kwargs= {'irmao__nome__icontains' : nomev, 'irmao__apelido__icontains' : apelidov, 'actividade__designacao' : actividadev, 'funcao_id' : funcaov, 'actividade__data__month':mesv, 'actividade__data__year' : anov}
    
    if (
        not nomev and
        not apelidov and
        actividadev == '0' and
        funcaov == '0' and
        mesv == '0' and
        anov == '0'
    ):
        messages.warning(request, "Preencha pelo menos um campo para efectuar a busca.")
        return redirect('/tibl/gestao/actividades/1/')
    
    if (actividadev == '0'):
        del kwargs['actividade__designacao']
    if (funcaov == '0'):
        del kwargs['funcao_id']
    if (mesv == '0'):
        del kwargs['actividade__data__month']
    if (anov == '0'):
        del kwargs['actividade__data__year']
    resultado = Escala.objects.values('actividade_id','actividade__designacao','actividade__designacao__designacao','actividade__data','funcao__designacao','irmao__nome','irmao__apelido','actividade__localactividade__designacao').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'actividadesfiltradas.html', {'bb':paginaresultado})

@login_required
def encontraDepartamentos(request):
    nomev = request.GET['nomev']
    apelidov = request.GET['apelidov']
    departamentov = int(request.GET['departamentov'])
    funcaov = request.GET.get('funcaov', '').strip()
    pagina= request.GET['pagina']
    kwargs= {'irmao__nome__icontains':nomev, 'irmao__apelido__icontains' : apelidov, 'departamento_id' : departamentov }
    if (departamentov == 0):
        del kwargs['departamento_id']
    if funcaov:
        kwargs['funcao'] = funcaov
    resultado = Mandato.objects.values('departamento_id', 'departamento__designacao', 'funcao', 'irmao__nome', 'irmao__apelido').filter(**kwargs).order_by('departamento__designacao')
    # Mapear valor bruto do cargo para etiqueta legível
    cargo_map = dict(Mandato.FUNCAO_CHOICES)
    resultado = list(resultado)
    for r in resultado:
        r['cargo_display'] = cargo_map.get(r['funcao'], r['funcao'])
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'departamentosfiltrados.html', {'bb':paginaresultado})


@login_required
def encontraDizimosofertas(request):
    nomev = request.GET['nomev']
    apelidov = request.GET['apelidov']
    mesv= request.GET['mesv']
    anov= request.GET['anov']
    pagina= request.GET['pagina']
    kwargs= {'irmao__nome__icontains' : nomev, 'irmao__apelido__icontains' : apelidov, 'datacorrespondente__month':mesv, 'datacorrespondente__year' : anov}
    if (mesv == '0'):
        del kwargs['datacorrespondente__month']
    if (anov == '0'):
        del kwargs['datacorrespondente__year']
    resultado = Dizimooferta.objects.select_related('irmao', 'tipooferta', 'actividade').filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'dizimosofertasfiltradas.html', {'bb':paginaresultado})

@login_required
def encontraEntradas(request):
    tipov = request.GET.get('tipov', '').strip()
    rubricav = int(request.GET.get('rubricav', 0))
    mesv = request.GET.get('mesv', '0')
    anov = request.GET.get('anov', '0')
    pagina = request.GET.get('pagina', 1)
    contabancariav = int(request.GET.get('contabancariav', 0))
    kwargs = {}
    if tipov:
        kwargs['tipo'] = tipov
    if rubricav:
        kwargs['rubrica'] = rubricav
    if mesv != '0':
        kwargs['data__month'] = mesv
    if anov != '0':
        kwargs['data__year'] = anov
    if contabancariav:
        kwargs['contaaacreditar'] = contabancariav
    resultado = Entrada.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    return render(request, 'entradasfiltradas.html', {'bb': paginaresultado})

@login_required
def encontraSaidas(request):
    tipov = request.GET.get('tipov', '').strip()
    rubricav = int(request.GET.get('rubricav', 0))
    mesv = request.GET.get('mesv', '0')
    anov = request.GET.get('anov', '0')
    pagina = request.GET.get('pagina', 1)
    contabancariav = int(request.GET.get('contabancariav', 0))
    kwargs = {}
    if tipov:
        kwargs['tipo'] = tipov
    if rubricav:
        kwargs['rubrica'] = rubricav
    if mesv != '0':
        kwargs['data__month'] = mesv
    if anov != '0':
        kwargs['data__year'] = anov
    if contabancariav:
        kwargs['conta'] = contabancariav
    resultado = Saida.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    return render(request, 'saidasfiltradas.html', {'bb': paginaresultado})


@login_required
def encontraOrcamentoDepartamento(request):
    departamentov = request.GET['departamentov']
    orcamentov = request.GET['orcamentov']
    anov = request.GET['anov']
    
    kwargs= {'departamento__designacao__icontains':departamentov, 
             'orcamento__icontains' : orcamentov, 
             'ano__icontains' : anov, 
            }
    pagina= request.GET['pagina']
    resultado = OrcamentoDepartamento.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'orcamentodepartamentofiltrados.html', {'bb':paginaresultado})


@login_required
def encontraInventarioPatrimonio(request):
    nomev = request.GET['nomev']
    descricaov = request.GET['descricaov']
    codigov = request.GET['codigov']
    
    kwargs= {'nome__icontains':nomev, 
             'descricao__icontains' : descricaov, 
             'codigo__icontains' : codigov, 
            }
    pagina= request.GET['pagina']
    resultado = InventarioPatrimonio.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'inventariopatrimoniofiltrados.html', {'bb':paginaresultado})

@login_required
def encontraConteudoEnsino(request):
    autorv = request.GET['autorv']
    titulov = request.GET['titulov']
    
    
    kwargs= {'autor__nome__icontains':autorv, 
             'titulo__icontains' : titulov, 
             
            }
    pagina= request.GET['pagina']
    resultado = ConteudoEnsino.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'conteudoensinofiltrados.html', {'bb':paginaresultado})


@login_required
def encontraEnvioMensagem(request):
    mensagemv = request.GET['mensagemv']
    quemenviou = request.GET['quemenviou']
    
    
    kwargs= {'mensagem__icontains':mensagemv,
             'quemenviou__designacao__icontains' : quemenviou,

            }
    pagina= request.GET['pagina']
    resultado = EnvioMensagem.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'enviomensagemfiltrados.html', {'bb':paginaresultado})

@login_required
def criarEnvioMensagem(request):
    if not request.user.has_perm('sitetibl.add_enviomensagem'):
        messages.error(request, 'Acesso negado! Você não tem permissão para enviar mensagens.')
        return redirect('index')

    irmaos = Irmao.objects.select_related('celula').prefetch_related('integrantes_departamento').order_by('nome', 'apelido')
    departamentos = Departamento.objects.order_by('designacao')

    irmao_logado = Irmao.objects.filter(user=request.user).first()
    todos_departamentos = Departamento.objects.order_by('designacao')

    if request.method == 'POST':
        formulario = EnvioMensagemForm(request.POST)
        formulario.fields['quemenviou'].queryset = todos_departamentos
        if formulario.is_valid():
            obj = formulario.save(commit=False)
            obj.save()
            formulario.save_m2m()  # guardar destinatários M2M

            destinatarios = obj.destinatarios.all()
            emails_to = [i.email for i in destinatarios if i.email and i.email.strip()]
            telefones = [str(i.telefone).strip() for i in destinatarios if i.telefone and str(i.telefone).strip()]
            autor_nome = str(obj.quemenviou) if obj.quemenviou else ''

            sms_ok = False
            email_ok = False

            # Enviar SMS
            if obj.sms and telefones:
                sms_ok = bool(_enviar_sms(telefones, obj.mensagem))
                if sms_ok:
                    logger.info('SMS massivo enviado para %d destinatários', len(telefones))
                else:
                    messages.error(request, 'Não foi possível enviar o SMS. Por favor contacte o administrador do sistema.')

            # Enviar Email
            if obj.email and emails_to:
                try:
                    html_content = render_to_string('emails/email_mensagem_massiva.html', {
                        'mensagem': obj.mensagem,
                        'autor': autor_nome,
                    })
                    from_email = settings.EMAIL_HOST_USER or None
                    for email_addr in emails_to:
                        msg = EmailMultiAlternatives(
                            subject='Mensagem da TIBL',
                            body=obj.mensagem,
                            from_email=from_email,
                            to=[email_addr],
                        )
                        msg.attach_alternative(html_content, 'text/html')
                        msg.send()
                    email_ok = True
                    logger.info('Emails massivos enviados para %d destinatários', len(emails_to))
                except Exception as e:
                    logger.error('Falha ao enviar emails massivos: %s', e)
                    messages.error(request, 'Não foi possível enviar o email. Por favor contacte o administrador do sistema.')

            # Guardar estado real de envio
            obj.sms_enviado = sms_ok
            obj.email_enviado = email_ok
            obj.save(update_fields=['sms_enviado', 'email_enviado'])

            if (not obj.sms or sms_ok) and (not obj.email or email_ok):
                messages.success(request, f'Mensagem enviada com sucesso para {destinatarios.count()} destinatário(s).')
            return redirect(reverse('sitetibl:mostra_gestao', args=['enviomensagem', 1]))
        else:
            messages.error(request, 'Foram encontrados erros ao preencher o formulário.')
    else:
        formulario = EnvioMensagemForm()
        formulario.fields['quemenviou'].queryset = todos_departamentos

    return render(request, 'enviomensagem_criar.html', {
        'formulario': formulario,
        'irmaos': irmaos,
        'departamentos': departamentos,
    })


@login_required
def reenviarEnvioMensagem(request, pk):
    if not request.user.has_perm('sitetibl.add_enviomensagem'):
        messages.error(request, 'Acesso negado.')
        return redirect('index')

    obj = get_object_or_404(EnvioMensagem, pk=pk)
    destinatarios = obj.destinatarios.all()
    emails_to = [i.email for i in destinatarios if i.email and i.email.strip()]
    telefones = [str(i.telefone).strip() for i in destinatarios if i.telefone and str(i.telefone).strip()]
    autor_nome = str(obj.quemenviou) if obj.quemenviou else ''

    sms_ok = obj.sms_enviado
    email_ok = obj.email_enviado

    if obj.sms and telefones:
        sms_ok = bool(_enviar_sms(telefones, obj.mensagem))
        if sms_ok:
            logger.info('Reenvio SMS para %d destinatários (EnvioMensagem #%s)', len(telefones), pk)
        else:
            messages.error(request, 'Não foi possível reenviar o SMS. Por favor contacte o administrador do sistema.')

    if obj.email and emails_to:
        try:
            html_content = render_to_string('emails/email_mensagem_massiva.html', {
                'mensagem': obj.mensagem,
                'autor': autor_nome,
            })
            from_email = settings.EMAIL_HOST_USER or None
            for email_addr in emails_to:
                msg = EmailMultiAlternatives(
                    subject='Mensagem da TIBL',
                    body=obj.mensagem,
                    from_email=from_email,
                    to=[email_addr],
                )
                msg.attach_alternative(html_content, 'text/html')
                msg.send()
            email_ok = True
            logger.info('Reenvio email para %d destinatários (EnvioMensagem #%s)', len(emails_to), pk)
        except Exception as e:
            logger.error('Falha no reenvio de email (EnvioMensagem #%s): %s', pk, e)
            messages.error(request, 'Não foi possível reenviar o email. Por favor contacte o administrador do sistema.')

    obj.sms_enviado = sms_ok
    obj.email_enviado = email_ok
    obj.save(update_fields=['sms_enviado', 'email_enviado'])

    if (not obj.sms or sms_ok) and (not obj.email or email_ok):
        messages.success(request, 'Mensagem reenviada com sucesso.')

    return redirect(reverse('sitetibl:mostra_detalhe', args=['enviomensagem', pk]))


@login_required
def encontraBancos(request):
    designacao = request.GET['designacao']
    abreviatura = request.GET['abreviatura']
    
    
    kwargs= {'designacao__icontains':designacao, 
             'abreviacao__icontains' : abreviatura, 
             
            }
    pagina= request.GET['pagina']
    resultado = Banco.objects.filter(**kwargs)
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = dict(request.GET.lists())
    del dd['pagina']
    cc = request.META['QUERY_STRING']
    return render(request,'bancosfiltrados.html', {'bb':paginaresultado})

@login_required
def encontraEscalas(request):
    actividade = request.GET.get('actividade', '')
    funcao = request.GET.get('funcao', '')
    departamentov = request.GET.get('departamentov', '0')

    kwargs = {
        'actividade__designacao__designacao__icontains': actividade,
        'funcao__designacao__icontains': funcao,
    }
    if departamentov and departamentov != '0':
        kwargs['actividade__departamento_id'] = departamentov

    pagina = request.GET.get('pagina', 1)
    resultado = Escala.objects.filter(**kwargs).select_related(
        'irmao', 'actividade', 'actividade__departamento', 'funcao'
    )
    paginador = Paginator(resultado, 20)
    paginaresultado = paginador.get_page(pagina)
    departamentos = Departamento.objects.all().order_by('designacao')
    return render(request, 'escalasfiltrados.html', {
        'bb': paginaresultado,
        'departamentos': departamentos,
        'departamentov_sel': departamentov,
    })


@login_required
def criar_actividades_recorrentes(request):
    """Cria múltiplas actividades para uma série semanal recorrente."""
    if not request.user.has_perm('sitetibl.add_actividade'):
        messages.error(request, 'Acesso negado! Não tem permissão para criar actividades.')
        return redirect('index')

    if request.method == 'POST':
        form = ActividadesRecorrentesForm(request.POST)
        if form.is_valid():
            tipo_nome = form.cleaned_data['nome_actividade'].strip()
            tipo, _ = Listaactividades.objects.get_or_create(designacao=tipo_nome)
            departamento = form.cleaned_data.get('departamento')
            localactividade = form.cleaned_data.get('localactividade')
            inicio = form.cleaned_data['inicio']
            fim = form.cleaned_data['fim']
            data_inicio = form.cleaned_data['data_inicio']
            data_fim = form.cleaned_data['data_fim']
            dias_semana = [int(d) for d in form.cleaned_data['dias_semana']]
            dias_semana_str = ','.join(str(d) for d in sorted(dias_semana))

            Actividade.objects.create(
                designacao=tipo,
                departamento=departamento,
                localactividade=localactividade,
                inicio=inicio,
                fim=fim,
                data=data_inicio,
                is_recorrente=True,
                recorrencia_fim=data_fim,
                dias_semana=dias_semana_str,
                criado_por=request.user,
            )

            messages.success(request, f'Série recorrente "{tipo_nome}" criada com sucesso.')
            return redirect('sitetibl:mostra_gestao', gestaoescolhida='actividades', pagina=1)
    else:
        form = ActividadesRecorrentesForm()

    return render(request, 'actividades_recorrentes.html', {'form': form})


class EscalasPorActividadeView(APIView):

    def get(self, request, actividade_id):

        try:
            actividade = Actividade.objects.get(id=actividade_id)
        except Actividade.DoesNotExist:
            return Response(
                {"erro": "Actividade não encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )

        escalas = Escala.objects.filter(actividade=actividade)

        serializer = EscalaSerializer(escalas, many=True)

        return Response({
            "actividade": str(actividade),
            "escalas": serializer.data
        })


#VIEWS PARA OS DASHBOARDS

@login_required
def dashboardIrmaos(request):
    ano = now().year

    queryset = (
        Irmao.objects
        .filter(data_criacao__year=ano)
        .annotate(mes=TruncMonth('data_criacao'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')   # ordem cronológica
    )

    # Cria todos os meses com valor zero
    meses = OrderedDict()
    for i in range(1, 13):
        meses[i] = 0

    # Preenche os meses que têm dados
    for item in queryset:
        meses[item['mes'].month] = item['total']

    # Labels dinâmicos: mês + ano
    labels = [f"{mes} {ano}" for mes in ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']]
    data = list(meses.values())

    return JsonResponse({
        "labels": labels,
        "data": data
    })

@login_required
def dashboardOrcamentoDepartamento(request):
    ano = now().year

    queryset = (
        OrcamentoDepartamento.objects
        .filter(ano=ano)
        .values('departamento__designacao')
        .annotate(total=Sum('orcamento'))
        .order_by('departamento__designacao')
    )

    labels = []
    data = []

    for item in queryset:
        labels.append(item['departamento__designacao'])
        data.append(float(item['total']))

    return JsonResponse({
        "labels": labels,
        "data": data
    })

@login_required
def dashboardPedidosSaidaSemana(request):
    ano = now().year

    queryset = (
        PedidoSaida.objects
        .filter(data_criacao__year=ano)
        .annotate(dia_semana=ExtractWeekDay('data_criacao'))
        .values('dia_semana')
        .annotate(total=Count('id'))
    )

    # Django: 1=Dom, 2=Seg, 3=Ter, ..., 7=Sáb
    dias = {
        1: 'Dom',
        2: 'Seg',
        3: 'Ter',
        4: 'Qua',
        5: 'Qui',
        6: 'Sex',
        7: 'Sáb',
    }

    # Inicializa todos os dias com zero
    dados = {dia: 0 for dia in dias.values()}

    for item in queryset:
        nome_dia = dias[item['dia_semana']]
        dados[nome_dia] = item['total']

    return JsonResponse({
        "ano":ano,
        "labels": list(dados.keys()),
        "data": list(dados.values())
    })


@login_required
def dashboardConteudoEnsinoMensal(request):
    ano = now().year

    queryset = (
        ConteudoEnsino.objects
        .filter(data_criacao__year=ano)
        .annotate(mes=TruncMonth('data_criacao'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    meses = {
        1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',
        7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'
    }

    labels = []
    data = []
    total_geral = 0

    for item in queryset:
        labels.append(meses[item['mes'].month])
        data.append(item['total'])
        total_geral += item['total']

    return JsonResponse({
        "ano": ano,
        "labels": labels,
        "data": data,
        "total": total_geral
    })

@login_required
def dashboardDizimoOferta(request):
    ano = now().year

    # Pega todos os tipos de oferta existentes
    tipos = TipoOferta.objects.all()

    meses = {i: 0 for i in range(1, 13)}
    labels = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

    datasets = []

    for tipo in tipos:
        queryset = (
            Dizimooferta.objects
            .filter(datacorrespondente__year=ano, tipooferta=tipo)
            .annotate(mes=TruncMonth('datacorrespondente'))
            .values('mes')
            .annotate(total=Sum('valor'))
            .order_by('mes')
        )

        # Preenche todos os meses
        data = meses.copy()
        for item in queryset:
            data[item['mes'].month] = float(item['total'] or 0)

        datasets.append({
            "label": tipo.designacao,   # Nome do tipo de oferta
            "data": list(data.values())
        })

    return JsonResponse({
        "ano": ano,
        "labels": labels,
        "datasets": datasets
    })



@login_required
def dashboardCrescimentoMembros(request):
    ano = now().year

    queryset = (
        RelatorioSemanalCelula.objects
        .filter(data_reuniao__year=ano)
        .annotate(mes=TruncMonth('data_reuniao'))
        .values('mes')
        .annotate(
            total_membros=Sum('numero_participantes_membros'),
            total_visitantes=Sum('numero_participantes_visitantes'),
            total_criancas=Sum('numero_participantes_criancas')
        )
        .order_by('mes')
    )

    # Meses padrão
    meses = {i: 0 for i in range(1, 13)}
    labels = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

    data_membros = meses.copy()
    data_visitantes = meses.copy()
    data_criancas = meses.copy()

    for item in queryset:
        m = item['mes'].month
        data_membros[m] = item['total_membros'] or 0
        data_visitantes[m] = item['total_visitantes'] or 0
        data_criancas[m] = item['total_criancas'] or 0

    return JsonResponse({
        "ano": ano,
        "labels": labels,
        "membros": list(data_membros.values()),
        "visitantes": list(data_visitantes.values()),
        "criancas": list(data_criancas.values())
    })


@login_required
def dashboardDepartamentosMembros(request):
    """Número de membros por departamento — gráfico de barras horizontais."""
    dados = (
        Mandato.objects
        .values('departamento__designacao')
        .annotate(total=Count('irmao', distinct=True))
        .order_by('-total')
    )
    labels = [d['departamento__designacao'] for d in dados]
    data = [d['total'] for d in dados]
    return JsonResponse({"labels": labels, "data": data})


#VIEWS QUE GERAM RELATÓRIOS
@login_required
def meu_perfil(request):
    """Página de perfil pessoal: actualiza contactos e senha."""
    try:
        irmao = request.user.irmao
    except Irmao.DoesNotExist:
        irmao = None

    perfil_form = MeuPerfilForm(instance=irmao) if irmao else None
    senha_form = MeuPerfilPasswordForm(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'perfil' and irmao:
            perfil_form = MeuPerfilForm(request.POST, request.FILES, instance=irmao)
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, 'Dados de contacto actualizados com sucesso.')
                return redirect('sitetibl:meu_perfil')

        elif action == 'senha':
            senha_form = MeuPerfilPasswordForm(user=request.user, data=request.POST)
            if senha_form.is_valid():
                senha_form.save()
                update_session_auth_hash(request, senha_form.user)
                messages.success(request, 'Senha alterada com sucesso.')
                return redirect('sitetibl:meu_perfil')

    return render(request, 'meu_perfil.html', {
        'perfil_form': perfil_form,
        'senha_form': senha_form,
        'irmao': irmao,
    })


@login_required
def pagina_relatorios(request):
    return render(request, 'relatorios/template_relatorio.html')


@login_required
@permission_required('sitetibl.change_irmao', raise_exception=True)
def relatorio_irmaos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_irmaos.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatório de Irmãos",
        author="Sistema TIBL"
    )

    elements = []
    styles = getSampleStyleSheet()

    # ðŸ”¹ LOGO
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'fotos', '2022', 'cba.png')

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Paragraph("<br/>", styles['Normal']))

    # ðŸ”¹ TÍTULO
    elements.append(
        Paragraph(
            "<b>Relatório Geral de Irmãos</b>",
            styles['Title']
        )
    )

    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ðŸ”¹ CABEÃ‡ALHO DA TABELA
    data = [
        ['Nome', 'Telefone', 'Categoria', 'Dizimista']
    ]

    # ðŸ”¹ DADOS
    for irmao in Irmao.objects.all():
        data.append([
            irmao.nome,
            irmao.telefone or '-',
            irmao.get_categoria_display(),
            'Sim' if irmao.dizimista == 'sim' else 'Não',
        ])

    # ðŸ”¹ TABELA
    table = Table(data, colWidths=[160, 110, 90, 90])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


@login_required
@permission_required('sitetibl.view_dizimooferta', raise_exception=True)
def relatorio_dizimos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_dizimos_ofertas.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatório de Dizimos",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    elements = []

    # ðŸ”¹ LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'fotos',
        '2022',
        'cba.png'
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Paragraph("<br/>", styles['Normal']))

    # ðŸ”¹ TÍTULO
    elements.append(
        Paragraph("<b>Relatório de Dízimos e Ofertas</b>", styles['Title'])
    )

    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ðŸ”¹ CABEÃ‡ALHO DA TABELA
    data = [
        ['Irmão', 'Telefone', 'Tipo de Oferta', 'Valor', 'Moeda', 'Data']
    ]

    # ðŸ”¹ DADOS
    queryset = Dizimooferta.objects.select_related(
        'irmao', 'tipooferta'
    ).order_by('-datacorrespondente')

    for d in queryset:
        data.append([
            d.irmao.nome,
            d.irmao.telefone or '-',
            d.tipooferta.designacao if d.tipooferta else '-',
            f"{d.valor:,.2f}",
            d.moeda,
            d.datacorrespondente.strftime('%d/%m/%Y')
        ])

    # ðŸ”¹ TABELA
    table = Table(
        data,
        colWidths=[110, 80, 100, 70, 50, 70]
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ('ALIGN', (5, 1), (5, -1), 'CENTER'),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


@login_required
@permission_required('sitetibl.view_departamento', raise_exception=True)
def relatorio_departamentos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_departamentos.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        title="Relatório de Departamentos",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    elements = []

    # ðŸ”¹ LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'fotos',
        '2022',
        'cba.png'
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    # ðŸ”¹ TÍTULO
    elements.append(
        Paragraph("<b>Relatório de Departamentos</b>", styles['Title'])
    )

   
    elements.append(Paragraph("<br/>", styles['Normal']))

    # ðŸ”¹ TABELA
    data = [['Departamento', 'Líder', 'Vice-Líder']]

    for d in Departamento.objects.all():
        data.append([
            d.designacao,
            str(d.lider_departamento) if d.lider_departamento else '-',
            str(d.vice_lider_departamento) if d.vice_lider_departamento else '-'
        ])

    table = Table(data, colWidths=[180, 160, 160])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ]))

    elements.append(table)

    doc.build(elements)

    return response


@login_required
@permission_required('sitetibl.view_escala', raise_exception=True)
def relatorio_escalas_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_escalas.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatório de Escalas",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    elements = []

    # ðŸ”¹ LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'fotos',
        '2022',
        'cba.png'
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Paragraph("<br/>", styles['Normal']))

    # ðŸ”¹ TÍTULO
    elements.append(
        Paragraph("<b>Relatório Geral de Escalas</b>", styles['Title'])
    )

    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ðŸ”¹ CABEÃ‡ALHO DA TABELA
    data = [[
        'Irmão',
        'Actividade',
        'Função',
        'Início',
        'Fim',
        'Data'
    ]]

    # ðŸ”¹ DADOS
    for escala in Escala.objects.select_related('irmao', 'actividade').all():
        data.append([
            escala.irmao.nome if escala.irmao else '-',
            escala.actividade.designacao.designacao if escala.actividade else '-',
            escala.funcao,
            escala.actividade.inicio.strftime('%H:%M') if escala.actividade and escala.actividade.inicio else '-',
            escala.actividade.fim.strftime('%H:%M') if escala.actividade and escala.actividade.fim else '-',
            escala.actividade.data.strftime('%d/%m/%Y') if escala.actividade and escala.actividade.data else '-',
        ])

    # ðŸ”¹ TABELA
    table = Table(data, colWidths=[90, 120, 70, 60, 60, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('ALIGN', (3, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


@login_required
@permission_required('sitetibl.view_actividade', raise_exception=True)
def relatorio_actividades_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_actividades.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Relatório de Actividades",
        author="Sistema TIBL"
    )

    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']

    cell_style = ParagraphStyle(
        'cell',
        fontSize=9,
        leading=11,
        wordWrap='CJK'
    )

    # ðŸ”¹ LOGO
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'fotos', '2022', 'cba.png')

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    # ðŸ”¹ TÍTULO
    elements.append(Paragraph("Relatório de Actividades", title_style))

    elements.append(Paragraph("<br/>", styles['Normal']))

    # ðŸ”¹ CABEÃ‡ALHO DA TABELA
    data = [
        [
            "Designação",
            "Início",
            "Fim",
            "Data",
            "Tema",
            "Local"
        ]
    ]

    # ðŸ”¹ DADOS
    for actividade in Actividade.objects.all():
        data.append([
            Paragraph(str(actividade.designacao or '-'), cell_style),
            Paragraph(actividade.inicio.strftime('%H:%M') if actividade.inicio else '-', cell_style),
            Paragraph(actividade.fim.strftime('%H:%M') if actividade.fim else '-', cell_style),
            Paragraph(actividade.data.strftime('%d/%m/%Y') if actividade.data else '-', cell_style),
            Paragraph(str(actividade.tema or '-'), cell_style),
            Paragraph(str(actividade.localactividade or '-'), cell_style),
        ])

    # ðŸ”¹ TABELA
    table = Table(
        data,
        colWidths=[
            4 * cm,
            2 * cm,
            2 * cm,
            2.5 * cm,
            4 * cm,
            3.5 * cm
        ],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-3, -1), 'CENTER'),

        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),

        # Fundo
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


@login_required
@permission_required('sitetibl.view_inventariopatrimonio', raise_exception=True)
def relatorio_inventario_patrimonio_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_inventario_patrimonio.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatório de Inventário de Património",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    elements = []

    # ðŸ”¹ ESTILO PARA CÉLULAS (QUEBRA DE LINHA)
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11
    )

    # ðŸ”¹ LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'fotos',
        '2022',
        'cba.png'
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Paragraph("<br/>", styles['Normal']))

    # ðŸ”¹ TÍTULO
    elements.append(
        Paragraph("<b>Relatório de Inventário de Património</b>", styles['Title'])
    )
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ðŸ”¹ CABEÃ‡ALHO DA TABELA
    data = [[
        'Nome',
        'Descrição',
        'Categoria',
        'Código',
        'Preço',
        'Moeda',
        'Quantidade'
    ]]

    # ðŸ”¹ DADOS
    for i in InventarioPatrimonio.objects.all():
        data.append([
            Paragraph(i.nome or '-', cell_style),
            Paragraph(i.descricao or '-', cell_style),
            Paragraph(i.categoria_patrimonio.designacao if i.categoria_patrimonio else '-', cell_style),
            Paragraph(i.codigo or '-', cell_style),
            Paragraph(f"{i.preco:.2f}" if i.preco else '0.00', cell_style),
            Paragraph(i.moeda.designacao or '-', cell_style),
            Paragraph(str(i.quantidade), cell_style),
        ])

    # ðŸ”¹ TABELA
    table = Table(
        data,
        colWidths=[70, 110, 80, 60, 50, 40, 50]
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('ALIGN', (4, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response



@login_required
@permission_required('sitetibl.view_saida', raise_exception=True)
def relatorio_saida_caixa_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_saida_caixa.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="Relatório de Saídas de Caixa",
        author="Sistema TIBL"
    )

    styles = getSampleStyleSheet()
    elements = []

    # ðŸ”¹ Estilo para quebra automática nas células
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11
    )

    # ðŸ”¹ LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'fotos',
        '2022',
        'cba.png'
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Paragraph("<br/>", styles['Normal']))

    # ðŸ”¹ TÍTULO
    elements.append(
        Paragraph("<b>Relatório de Saídas de Caixa</b>", styles['Title'])
    )
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ðŸ”¹ CABEÃ‡ALHO DA TABELA
    data = [[
        'Departamento',
        'Projecto',
        'Montante',
        'Moeda',
        'Requerente',
        'Status',
        'Aprovador',
        'Data'
    ]]

    # ðŸ”¹ DADOS
    for p in PedidoSaida.objects.all():
        data.append([
            Paragraph(str(p.departamento) if p.departamento else '-', cell_style),
            Paragraph(str(p.projecto) if p.projecto else '-', cell_style),
            Paragraph(f"{p.montante:.2f}" if p.montante else '0.00', cell_style),
            Paragraph(p.moeda.designacao or '-', cell_style),
            Paragraph(str(p.requerente) if p.requerente else '-', cell_style),
            Paragraph(str(p.status_de_aprovacao), cell_style),
            Paragraph(str(p.aprovador) if p.aprovador else '-', cell_style),
            Paragraph(
                p.data_criacao.strftime('%d/%m/%Y') if p.data_criacao else '-',
                cell_style
            ),
        ])

    # ðŸ”¹ TABELA
    table = Table(
        data,
        colWidths=[80, 70, 55, 40, 70, 55, 60, 50]
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


@login_required
def dashboard(request):
    from datetime import date as dt_date, timedelta
    import random
    hoje = dt_date.today()
    user = request.user

    # --- Versículo do dia (roda pela data para variar diariamente) ---
    VERSICULOS = [
        {'texto': 'Porque eu bem sei os pensamentos que penso de vós, diz o Senhor; pensamentos de paz e não de mal, para vos dar o fim que esperais.', 'ref': 'Jeremias 29:11'},
        {'texto': 'Tudo posso naquele que me fortalece.', 'ref': 'Filipenses 4:13'},
        {'texto': 'O Senhor é o meu pastor; nada me faltará.', 'ref': 'Salmos 23:1'},
        {'texto': 'Confia no Senhor de todo o teu coração e não te estribes no teu próprio entendimento.', 'ref': 'Provérbios 3:5'},
        {'texto': 'Mas os que esperam no Senhor renovarão as suas forças; subirão com asas como águias; correrão e não se cansarão; caminharão e não se fatigarão.', 'ref': 'Isaías 40:31'},
        {'texto': 'Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus; eu te fortaleço, e te ajudo, e te sustento com a destra da minha justiça.', 'ref': 'Isaías 41:10'},
        {'texto': 'Dá instrução ao sábio, e ele se fará mais sábio; ensina ao justo, e ele crescerá em entendimento.', 'ref': 'Provérbios 9:9'},
        {'texto': 'O amor é paciente, o amor é bondoso. Não inveja, não se vangloria, não se orgulha.', 'ref': '1 Coríntios 13:4'},
        {'texto': 'Alegrai-vos sempre no Senhor; outra vez digo: alegrai-vos.', 'ref': 'Filipenses 4:4'},
        {'texto': 'Vinde a mim, todos os que estais cansados e oprimidos, e eu vos aliviarei.', 'ref': 'Mateus 11:28'},
        {'texto': 'Porque Deus amou o mundo de tal maneira que deu o seu Filho unigénito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.', 'ref': 'João 3:16'},
        {'texto': 'E sabemos que todas as coisas contribuem juntamente para o bem daqueles que amam a Deus.', 'ref': 'Romanos 8:28'},
        {'texto': 'Sê forte e corajoso; não temas, nem te espantes, porque o Senhor, teu Deus, é contigo por onde quer que andares.', 'ref': 'Josué 1:9'},
        {'texto': 'O Senhor é a minha luz e a minha salvação; a quem temerei? O Senhor é a força da minha vida; de quem me recearei?', 'ref': 'Salmos 27:1'},
        {'texto': 'Lançando sobre ele toda a vossa ansiedade, porque ele tem cuidado de vós.', 'ref': '1 Pedro 5:7'},
        {'texto': 'Sede fortes e corajosos, não temais, nem vos assusteis por causa deles, pois o Senhor, vosso Deus, é quem vai convosco; não vos deixará, nem vos desamparará.', 'ref': 'Deuteronómio 31:6'},
        {'texto': 'Eu sou a videira, vós, as varas; quem está em mim, e eu nele, este dá muito fruto, porque sem mim nada podeis fazer.', 'ref': 'João 15:5'},
        {'texto': 'A tua palavra é lâmpada que ilumina os meus passos e luz que clareia o meu caminho.', 'ref': 'Salmos 119:105'},
        {'texto': 'Porque onde estiverem dois ou três reunidos em meu nome, aí estou eu no meio deles.', 'ref': 'Mateus 18:20'},
        {'texto': 'Entrega o teu caminho ao Senhor; confia nele, e ele tudo fará.', 'ref': 'Salmos 37:5'},
        {'texto': 'Irmãos, não julgo havê-lo alcançado; mas uma coisa faço: esquecendo-me das coisas que ficaram para trás e avançando para as que estão adiante, prossigo para o alvo.', 'ref': 'Filipenses 3:13-14'},
    ]
    idx_versiculo = hoje.toordinal() % len(VERSICULOS)
    versiculo_do_dia = VERSICULOS[idx_versiculo]

    # --- Dados visíveis para TODOS ---
    anuncios = Anuncio.objects.order_by('-data')[:5]

    proximas_actividades = (
        Actividade.objects
        .filter(data__gte=hoje, data__lte=hoje + timedelta(days=14))
        .exclude(is_recorrente=True, parent_event__isnull=True)
        .select_related('designacao', 'localactividade')
        .distinct()
        .order_by('data', 'inicio')[:5]
    )

    # Escalas do membro logado + verificação de célula
    minhas_escalas_list = []
    irmao_obj = Irmao.objects.filter(user=user).select_related('celula').first()
    tem_celula = False
    if irmao_obj:
        tem_celula = irmao_obj.celula is not None
        minhas_escalas_base = (
            Escala.objects
            .filter(irmao=irmao_obj)
            .select_related('actividade', 'actividade__designacao', 'actividade__localactividade', 'funcao')
            .order_by('-id')
        )
        minhas_escalas_futuras, _ = _normalizar_escalas_por_ocorrencia(minhas_escalas_base, hoje)
        minhas_escalas_list = minhas_escalas_futuras[:5]

    # Aniversariantes do mês
    aniversariantes = (
        Irmao.objects
        .filter(datanascimento__month=hoje.month)
        .annotate(
            aniversario_dia=ExtractDay('datanascimento'),
            aniversario_ja_passou=Case(
                When(datanascimento__day__lt=hoje.day, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        .order_by('aniversario_ja_passou', 'aniversario_dia', 'nome', 'apelido')[:10]
    )

    # Alertas de aniversário de hoje
    aniversarios_alerta = []
    aniversariantes_hoje = Irmao.objects.filter(
        datanascimento__month=hoje.month,
        datanascimento__day=hoje.day,
    )
    for a in aniversariantes_hoje:
        prefixo = 'da irmã' if a.sexo == 'F' else 'do irmão'
        aniversarios_alerta.append({
            'tipo': 'today',
            'mensagem': f'ðŸŽ‚ Hoje é aniversário {prefixo} {a.nome} {a.apelido}!',
            'data_iso': hoje.isoformat(),
        })

    # --- Dados financeiros (passados apenas se utilizador tem permissão) ---
    pedidos_pendentes = None
    saldos_bancarios = None
    total_membros = Irmao.objects.count()

    if user.has_perm('sitetibl.view_pedidosaida'):
        pedidos_pendentes = (
            PedidoSaida.objects
            .exclude(estado__in=['aprovado', 'rejeitado'])
            .select_related('requerente', 'departamento', 'status_de_aprovacao')
            .order_by('-data_criacao')[:5]
        )

    if user.has_perm('sitetibl.view_contabancaria'):
        contas = Contabancaria.objects.filter(is_active=True).select_related('banco')
        saldos_bancarios = []
        for c in contas:
            saldos_bancarios.append({
                'banco': str(c.banco),
                'numero': c.numeroconta[-4:] if len(c.numeroconta) >= 4 else c.numeroconta,
                'moeda': c.moeda,
                'saldo': c.saldo_actual(),
            })

    context = {
        'titulo': 'Dashboard',
        'versiculo': versiculo_do_dia,
        'tem_celula': tem_celula,
        'tem_perfil': irmao_obj is not None,
        'anuncios': anuncios,
        'proximas_actividades': proximas_actividades,
        'minhas_escalas': minhas_escalas_list,
        'aniversariantes': aniversariantes,
        'aniversarios_alerta': aniversarios_alerta,
        'pedidos_pendentes': pedidos_pendentes,
        'saldos_bancarios': saldos_bancarios,
        'total_membros': total_membros,
    }
    return render(request, 'dashboard.html', context)

def root_redirect(request):
    return redirect('dashboard')


def _normalizar_escalas_por_ocorrencia(escalas, hoje):
    """
    Para escalas ligadas a actividade-pai recorrente, usa a ocorrência-filho
    relevante para exibição (próxima futura ou mais recente passada).
    """
    import datetime as _dt

    escalas = list(escalas)
    if not escalas:
        return [], []

    parent_ids = {
        escala.actividade_id
        for escala in escalas
        if escala.actividade_id and escala.actividade and escala.actividade.is_recorrente and escala.actividade.parent_event_id is None
    }

    filhos_por_pai = {}
    if parent_ids:
        filhos = (
            Actividade.objects
            .select_related('designacao', 'localactividade')
            .filter(parent_event_id__in=parent_ids)
            .order_by('data', 'inicio', 'id')
        )
        for filho in filhos:
            filhos_por_pai.setdefault(filho.parent_event_id, []).append(filho)

    escalas_futuras = []
    escalas_passadas = []
    seen_keys = set()

    for escala in escalas:
        actividade = escala.actividade
        actividade_exibicao = actividade

        if actividade and actividade.id in filhos_por_pai:
            filhos = filhos_por_pai[actividade.id]
            proxima = next((f for f in filhos if f.data and f.data >= hoje), None)
            actividade_exibicao = proxima if proxima is not None else (filhos[-1] if filhos else actividade)

        escala.actividade = actividade_exibicao
        dedupe_key = (
            actividade_exibicao.id if actividade_exibicao else None,
            escala.funcao_id,
        )
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)

        data_ref = actividade_exibicao.data if actividade_exibicao and actividade_exibicao.data else hoje
        if data_ref >= hoje:
            escalas_futuras.append(escala)
        else:
            escalas_passadas.append(escala)

    escalas_futuras.sort(
        key=lambda e: (
            e.actividade.data if e.actividade and e.actividade.data else hoje,
            e.actividade.inicio if e.actividade and e.actividade.inicio else _dt.time(0, 0),
            e.id,
        )
    )
    escalas_passadas.sort(
        key=lambda e: (
            e.actividade.data if e.actividade and e.actividade.data else hoje,
            e.actividade.inicio if e.actividade and e.actividade.inicio else _dt.time(0, 0),
            e.id,
        ),
        reverse=True,
    )

    return escalas_futuras, escalas_passadas

@login_required
def minhas_escalas(request):
    from datetime import date as dt_date
    hoje = dt_date.today()

    irmao_obj = Irmao.objects.filter(user=request.user).first()
    if not irmao_obj:
        messages.warning(request, 'O seu utilizador não está associado a nenhum perfil de irmão.')
        return render(request, 'minhasescalas.html', {
            'escalas_futuras': [],
            'escalas_passadas': [],
            'titulo': 'As Minhas Escalas',
        })

    base_qs = Escala.objects.filter(irmao=irmao_obj).select_related(
        'actividade',
        'actividade__designacao',
        'actividade__localactividade',
        'funcao',
    )
    escalas_futuras, escalas_passadas = _normalizar_escalas_por_ocorrencia(base_qs, hoje)
    escalas_passadas = escalas_passadas[:20]

    context = {
        'escalas_futuras': escalas_futuras,
        'escalas_passadas': escalas_passadas,
        'titulo': 'As Minhas Escalas',
    }
    return render(request, 'minhasescalas.html', context)

@login_required
def escalar_em_massa(request, actividade_id):
    if request.method == 'POST':
        funcao_id = request.POST.get('funcao')
        irmaos_ids = request.POST.getlist('irmaos') # Multiple select returns list
        
        if funcao_id and irmaos_ids:
            actividade = get_object_or_404(Actividade, id=actividade_id)
            funcao = get_object_or_404(Funcao, id=funcao_id)
            
            novos = 0
            ids_processados = set()
            
            for irmao_id in irmaos_ids:
                if irmao_id in ids_processados:
                    continue
                ids_processados.add(irmao_id)
                
                # Evitar que o membro seja escalado duas vezes na mesma Actividade (mesmo que com funções diferentes)
                if not Escala.objects.filter(actividade=actividade, irmao_id=irmao_id).exists():
                    try:
                        Escala.objects.create(
                            actividade=actividade,
                            irmao_id=irmao_id,
                            funcao=funcao,
                        )
                        novos += 1
                    except IntegrityError:
                        continue

            if novos:
                messages.success(request, f'{novos} irmãos escalados para {funcao.designacao} com sucesso!')
            else:
                messages.info(request, 'As pessoas selecionadas já estavam escaladas para esta actividade.')
                
    # Redirect back to the details page regardless of success/failure
    return redirect(f'/tibl/actividades/detalhe/{actividade_id}/')


# ---------------------------------------------------------------------------
# FullCalendar JSON feed — actividades
# ---------------------------------------------------------------------------

@login_required
def actividades_feed(request):
    """
    Endpoint JSON para o FullCalendar.
    - Actividades simples: devolvidas directamente da BD para o intervalo pedido.
    - Actividades recorrentes: ocorrências calculadas dinamicamente via rrule.
      Suporta recorrências sem data de fim — expande até ao limite do intervalo.
    """
    if not request.user.has_perm('sitetibl.view_actividade'):
        return JsonResponse({'error': 'Acesso negado'}, status=403)

    import datetime as _dt
    from dateutil.rrule import rrule, WEEKLY, DAILY, MONTHLY, MO, TU, WE, TH, FR, SA, SU

    start_str = request.GET.get('start', '')
    end_str = request.GET.get('end', '')
    try:
        start = _dt.date.fromisoformat(start_str[:10])
        end = _dt.date.fromisoformat(end_str[:10])
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Parâmetros start/end inválidos'}, status=400)

    FREQ_MAP = {'WEEKLY': WEEKLY, 'DAILY': DAILY, 'MONTHLY': MONTHLY}
    WEEKDAY_MAP = {0: MO, 1: TU, 2: WE, 3: TH, 4: FR, 5: SA, 6: SU}

    events = []

    # --- 1. Actividades simples (não recorrentes, sem pai) ---
    simples = (
        Actividade.objects
        .select_related('designacao', 'departamento', 'localactividade')
        .filter(data__range=(start, end), is_recorrente=False, parent_event__isnull=True)
    )
    for act in simples:
        start_iso = f'{act.data}T{act.inicio}' if act.inicio else str(act.data)
        end_iso = f'{act.data}T{act.fim}' if act.fim else str(act.data)
        events.append({
            'id': act.pk,
            'title': str(act.designacao),
            'start': start_iso,
            'end': end_iso,
            'url': f'/tibl/actividades/detalhe/{act.pk}/',
            'backgroundColor': '#1b4d3e',
            'borderColor': '#163d31',
            'textColor': '#ffffff',
            'classNames': [],
            'extendedProps': {
                'departamento': str(act.departamento) if act.departamento else '',
                'local': str(act.localactividade) if act.localactividade else '',
                'recorrente': False,
            },
        })

    # --- 2. Actividades recorrentes — expansão dinâmica via rrule ---
    # Pais cujo período de recorrência intersecta o intervalo pedido:
    #   início â‰¤ fim do intervalo  E  (sem recorrencia_fim  OU  recorrencia_fim â‰¥ início)
    parents = (
        Actividade.objects
        .select_related('designacao', 'departamento', 'localactividade', 'event__rule')
        .filter(is_recorrente=True, parent_event__isnull=True)
        .filter(data__lte=end)
        .filter(
            Q(recorrencia_fim__isnull=True) | Q(recorrencia_fim__gte=start)
        )
    )
    parent_ids = [p.id for p in parents]
    child_map = {}
    if parent_ids:
        children = (
            Actividade.objects
            .filter(parent_event_id__in=parent_ids, data__range=(start, end))
            .only('id', 'parent_event_id', 'data')
        )
        for child in children:
            child_map[(child.parent_event_id, child.data)] = child.id

    for parent in parents:
        hora_inicio = parent.inicio or _dt.time(0, 0)
        hora_fim = parent.fim or _dt.time(23, 59)
        dtstart = _dt.datetime.combine(parent.data, hora_inicio)

        # Limite da expansão: respeitar recorrencia_fim ou usar o fim do intervalo pedido
        if parent.recorrencia_fim:
            until = _dt.datetime.combine(parent.recorrencia_fim, hora_fim)
        else:
            until = _dt.datetime.combine(end, hora_fim)

        # Frequência via Rule do django-scheduler (por omissão WEEKLY)
        freq_str = 'WEEKLY'
        try:
            if parent.event_id and parent.event and parent.event.rule_id:
                freq_str = parent.event.rule.frequency
        except Exception:
            pass
        freq = FREQ_MAP.get(freq_str, WEEKLY)

        rrule_kwargs = {'dtstart': dtstart, 'until': until}
        if freq == WEEKLY and parent.dias_semana:
            dias = [int(d.strip()) for d in parent.dias_semana.split(',') if d.strip().isdigit()]
            byweekday = [WEEKDAY_MAP[d] for d in dias if d in WEEKDAY_MAP]
            if byweekday:
                rrule_kwargs['byweekday'] = byweekday

        dur = (
            _dt.datetime.combine(_dt.date.today(), hora_fim)
            - _dt.datetime.combine(_dt.date.today(), hora_inicio)
        )
        if dur.total_seconds() < 0:
            dur = _dt.timedelta(hours=1)

        for occ_dt in rrule(freq, **rrule_kwargs):
            occ_date = occ_dt.date()
            if occ_date < start:
                continue
            if occ_date > end:
                break
            fim_dt = occ_dt + dur
            occurrence_id = child_map.get((parent.pk, occ_date), parent.pk)
            events.append({
                'id': f'r{parent.pk}_{occ_date.isoformat()}',
                'title': f'\u21bb {parent.designacao}',
                'start': occ_dt.strftime('%Y-%m-%dT%H:%M:%S'),
                'end': fim_dt.strftime('%Y-%m-%dT%H:%M:%S'),
                'url': f'/tibl/actividades/detalhe/{occurrence_id}/',
                'backgroundColor': '#0369a1',
                'borderColor': '#075985',
                'textColor': '#ffffff',
                'classNames': ['recorrente'],
                'extendedProps': {
                    'departamento': str(parent.departamento) if parent.departamento else '',
                    'local': str(parent.localactividade) if parent.localactividade else '',
                    'recorrente': True,
                },
            })

    return JsonResponse(events, safe=False)


# ---------------------------------------------------------------------------
# Vista de calendário — actividades
# ---------------------------------------------------------------------------

@login_required
def actividades_calendario(request):
    """Vista de calendário visual (FullCalendar v6)."""
    if not request.user.has_perm('sitetibl.view_actividade'):
        messages.error(request, 'Não tem permissão para ver o calendário de actividades.')
        return redirect('sitetibl:comeco')
    feed_url = '/tibl/api/actividades/feed/'
    return render(request, 'actividades_calendario.html', {'feed_url': feed_url})

# ---------------------------------------------------------------------------
# Documentação do utilizador — serve o site estático gerado pelo ProperDocs
# ---------------------------------------------------------------------------
def serve_documentacao(request, path=''):
    site_dir = Path(settings.BASE_DIR) / 'docs' / 'site'

    file_path = site_dir / path if path else site_dir / 'index.html'

    # Directórios â†’ tentar index.html dentro deles
    if file_path.is_dir():
        file_path = file_path / 'index.html'

    if not file_path.exists() or not file_path.is_file():
        raise Http404

    content_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(
        open(file_path, 'rb'),
        content_type=content_type or 'application/octet-stream',
    )


@login_required
def encontraSolicitacoes(request):
    assuntov = request.GET.get('assuntov', '').strip()
    categoriav = request.GET.get('categoriav', '').strip()
    estadov = request.GET.get('estadov', '').strip()
    pagina = request.GET.get('pagina', 1)
    qs = SolicitacaoInterdepartamental.objects.select_related(
        'departamento_solicitante', 'departamento_destinatario', 'solicitante'
    )
    if assuntov:
        qs = qs.filter(assunto__icontains=assuntov)
    if categoriav:
        qs = qs.filter(categoria=categoriav)
    if estadov:
        qs = qs.filter(estado=estadov)
    qs = qs.order_by('-data_criacao')
    paginador = Paginator(qs, 20)
    paginaresultado = paginador.get_page(pagina)
    dd = request.META['QUERY_STRING']
    return render(request, 'solicitacoesfiltradas.html', {'bb': paginaresultado, 'dd': dd})


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PAINEL DE ACOMPANHAMENTO PASTORAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_required
def pastoral_dashboard(request):
    """Painel principal pastoral com KPIs, insights, alertas, casos e aniversariantes."""
    if not request.user.has_perm('sitetibl.view_casopastoral'):
        messages.error(request, 'Não tem permissão para aceder ao painel pastoral.')
        return redirect('index')

    from datetime import timedelta as td
    from django.db.models import Max
    hoje = date.today()
    irmao_logado = Irmao.objects.filter(user=request.user).first()

    # â”€â”€ KPIs de atenção pastoral â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    alertas_novos = AlertaPastoral.objects.filter(estado='novo').count()
    casos_abertos = CasoPastoral.objects.filter(estado__in=['aberto', 'em_acompanhamento']).count()

    trinta_dias = now() - td(days=30)
    novos_ids_com_caso = CasoPastoral.objects.filter(
        tipo='integracao', membro__isnull=False
    ).values_list('membro_id', flat=True)
    novos_sem_acomp = Irmao.objects.filter(
        data_criacao__lt=trinta_dias, batizado=False,
    ).exclude(categoria='crianca').exclude(id__in=novos_ids_com_caso).count()

    visitantes_recorrentes = VisitanteRecorrente.objects.filter(
        estado='visitante', numero_visitas__gte=3
    ).count()

    # Inactivos: apenas membros que já participaram alguma vez mas não nos últimos 60 dias
    sessenta_dias = hoje - td(days=60)
    alguma_vez_ids = Escala.objects.values_list('irmao_id', flat=True).distinct()
    activos_ids = Escala.objects.filter(
        actividade__data__gte=sessenta_dias
    ).values_list('irmao_id', flat=True).distinct()
    membros_inactivos = Irmao.objects.filter(
        id__in=alguma_vez_ids
    ).exclude(id__in=activos_ids).count()

    # â”€â”€ Retrato da Congregação â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    total_membros = Irmao.objects.count()
    total_criancas = Irmao.objects.filter(categoria='crianca').count()
    total_batizados = Irmao.objects.filter(batizado=True).count()
# Não batizados conta apenas adultos (exclui crianças).
    total_nao_batizados = total_membros - total_batizados - total_criancas

    total_dizimistas = Irmao.objects.filter(dizimista='sim').count()
    total_masculino = Irmao.objects.filter(sexo='M').count()
    total_feminino = Irmao.objects.filter(sexo='F').count()
    total_em_departamento = Mandato.objects.values('irmao').distinct().count()
    total_sem_celula = Irmao.objects.filter(celula__isnull=True).count()
    total_com_celula = total_membros - total_sem_celula

    # Percentagens seguras
    def pct(part, total):
        return round(part * 100 / total) if total else 0

    retrato = {
        'total_membros': total_membros,
        'total_criancas': total_criancas,
        'total_batizados': total_batizados,
        'pct_batizados': pct(total_batizados, total_membros),
        'total_nao_batizados': total_nao_batizados,
        'total_dizimistas': total_dizimistas,
        'total_nao_dizimistas': total_membros - total_dizimistas,
        'pct_dizimistas': pct(total_dizimistas, total_membros),
        'total_masculino': total_masculino,
        'total_feminino': total_feminino,
        'total_em_departamento': total_em_departamento,
        'pct_em_departamento': pct(total_em_departamento, total_membros),
        'total_sem_celula': total_sem_celula,
        'total_com_celula': total_com_celula,
        'pct_com_celula': pct(total_com_celula, total_membros),
    }

    # â”€â”€ Alertas e Casos â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    alertas_urgentes = AlertaPastoral.objects.filter(
        estado__in=['novo', 'visto']
    ).select_related('membro', 'celula').order_by('-data_criacao')[:10]

    casos_recentes = CasoPastoral.objects.filter(
        estado__in=['aberto', 'em_acompanhamento']
    ).select_related('membro', 'responsavel').order_by('-data_atualizacao')[:10]

    if not request.user.is_superuser and not request.user.groups.filter(name='Pastor').exists():
        casos_recentes = casos_recentes.filter(
            Q(confidencial=False) | Q(responsavel=irmao_logado) | Q(criado_por=irmao_logado)
        )

    # â”€â”€ Aniversariantes (DB-level, com tratamento de virada de ano) â”€â”€â”€
    semana_fim = hoje + td(days=7)
    aniversariantes = []
    # Gera lista de (mês, dia) para os próximos 7 dias
    dias_para_verificar = [(hoje + td(days=i)) for i in range(8)]
    pares_mes_dia = [(d.month, d.day) for d in dias_para_verificar]
    # Filtra por mês/dia via Python (mais simples e compatível com SQLite e MySQL)
    candidatos = Irmao.objects.exclude(datanascimento__isnull=True).only(
        'nome', 'apelido', 'datanascimento'
    )
    for irmao in candidatos:
        par = (irmao.datanascimento.month, irmao.datanascimento.day)
        if par in pares_mes_dia:
            aniv_este_ano = irmao.datanascimento.replace(year=hoje.year)
            # corrige para o dia correcto na lista
            for d in dias_para_verificar:
                if d.month == par[0] and d.day == par[1]:
                    aniv_real = d
                    break
            aniversariantes.append({
                'irmao': irmao,
                'data': aniv_real,
                'idade': aniv_real.year - irmao.datanascimento.year,
            })
    aniversariantes.sort(key=lambda x: x['data'])

    context = {
        'alertas_novos': alertas_novos,
        'casos_abertos': casos_abertos,
        'novos_sem_acomp': novos_sem_acomp,
        'visitantes_recorrentes': visitantes_recorrentes,
        'membros_inactivos': membros_inactivos,
        'retrato': retrato,
        'alertas_urgentes': alertas_urgentes,
        'casos_recentes': casos_recentes,
        'aniversariantes': aniversariantes,
    }
    return render(request, 'pastoral_dashboard.html', context)


@login_required
def pastoral_alertas(request):
    """Lista de alertas pastorais com filtros."""
    if not request.user.has_perm('sitetibl.view_alertapastoral'):
        messages.error(request, 'Não tem permissão para ver alertas pastorais.')
        return redirect('index')

    qs = AlertaPastoral.objects.select_related('membro', 'celula', 'caso_associado')
    tipo_filtro = request.GET.get('tipo', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    if tipo_filtro:
        qs = qs.filter(tipo=tipo_filtro)
    if estado_filtro:
        qs = qs.filter(estado=estado_filtro)
    qs = qs.order_by('-data_criacao')
    paginador = Paginator(qs, 20)
    pagina = request.GET.get('pagina', 1)
    alertas = paginador.get_page(pagina)

    context = {
        'alertas': alertas,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'tipos': AlertaPastoral.TIPO_CHOICES,
        'estados': AlertaPastoral.ESTADO_CHOICES,
    }
    return render(request, 'pastoral_alertas.html', context)


@login_required
def pastoral_alerta_accao(request, alerta_id):
    """Mudar estado de um alerta ou criar caso a partir dele."""
    if not request.user.has_perm('sitetibl.change_alertapastoral'):
        messages.error(request, 'Não tem permissão para gerir alertas.')
        return redirect('sitetibl:pastoral_alertas')

    alerta = get_object_or_404(AlertaPastoral, id=alerta_id)
    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'resolver':
            alerta.estado = 'resolvido'
            alerta.save(update_fields=['estado', 'data_atualizacao'])
            messages.success(request, 'Alerta resolvido.')
        elif action == 'ignorar':
            alerta.estado = 'ignorado'
            alerta.save(update_fields=['estado', 'data_atualizacao'])
            messages.info(request, 'Alerta ignorado.')
        elif action == 'em_tratamento':
            alerta.estado = 'em_tratamento'
            alerta.save(update_fields=['estado', 'data_atualizacao'])
            messages.info(request, 'Alerta em tratamento.')
        elif action == 'criar_caso':
            irmao_logado = Irmao.objects.filter(user=request.user).first()
            if alerta.membro:
                caso = CasoPastoral.objects.create(
                    membro=alerta.membro,
                    tipo='outro',
                    titulo=f'Caso a partir de alerta: {alerta.titulo}',
                    descricao=alerta.descricao,
                    responsavel=irmao_logado,
                    criado_por=irmao_logado,
                )
                alerta.caso_associado = caso
                alerta.estado = 'em_tratamento'
                alerta.save(update_fields=['caso_associado', 'estado', 'data_atualizacao'])
                messages.success(request, f'Caso pastoral #{caso.id} criado a partir do alerta.')
                return redirect(reverse('sitetibl:mostra_detalhe', args=['casospastorais', caso.id]))
            else:
                messages.error(request, 'Não é possível criar caso — alerta sem membro associado.')

    return redirect('sitetibl:pastoral_alertas')


@login_required
def pastoral_inactivos(request):
    """Lista de membros inactivos."""
    if not request.user.has_perm('sitetibl.view_casopastoral'):
        messages.error(request, 'Não tem permissão para aceder ao painel pastoral.')
        return redirect('index')

    from datetime import timedelta as td
    hoje = date.today()
    dias_limite = int(request.GET.get('dias', 60))
    limite = hoje - td(days=dias_limite)

    # IDs de irmãos activos
    activos_ids = Escala.objects.filter(
        actividade__data__gte=limite
    ).values_list('irmao_id', flat=True).distinct()

    # Última participação de cada irmão inactivo
    from django.db.models import Max
    inactivos = (
        Irmao.objects.exclude(id__in=activos_ids)
        .select_related('celula', 'localcongregacao')
        .annotate(ultima_participacao=Max('particact__data'))
        .order_by('ultima_participacao')
    )

    paginador = Paginator(inactivos, 30)
    pagina = request.GET.get('pagina', 1)
    resultado = paginador.get_page(pagina)

    context = {
        'inactivos': resultado,
        'dias_limite': dias_limite,
        'hoje': hoje,
    }
    return render(request, 'pastoral_inactivos.html', context)


@login_required
def pastoral_novos(request):
    """Novos convertidos sem acompanhamento."""
    if not request.user.has_perm('sitetibl.view_casopastoral'):
        messages.error(request, 'Não tem permissão para aceder ao painel pastoral.')
        return redirect('index')

    from datetime import timedelta as td
    novos_ids_com_caso = CasoPastoral.objects.filter(
        tipo='integracao', membro__isnull=False
    ).values_list('membro_id', flat=True)

    trinta_dias = now() - td(days=30)
    novos = Irmao.objects.filter(
        data_criacao__lt=trinta_dias, batizado=False,
    ).exclude(categoria='crianca').exclude(id__in=novos_ids_com_caso).select_related('celula').order_by('-data_criacao')

    paginador = Paginator(novos, 30)
    pagina = request.GET.get('pagina', 1)
    resultado = paginador.get_page(pagina)

    context = {'novos': resultado}
    return render(request, 'pastoral_novos.html', context)


# â”€â”€ APIs JSON para gráficos pastorais â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@login_required
def pastoral_api_tendencias(request):
    """Novos membros, baptismos e visitantes por mês (12 meses)."""
    from datetime import timedelta as td
    hoje = date.today()
    inicio = hoje - td(days=365)

    novos_por_mes = (
        Irmao.objects.filter(data_criacao__date__gte=inicio)
        .annotate(mes=TruncMonth('data_criacao'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    baptismos_por_mes = (
        Irmao.objects.filter(data_criacao__date__gte=inicio, batizado=True)
        .annotate(mes=TruncMonth('data_criacao'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    visitantes_por_mes = (
        VisitanteRecorrente.objects.filter(primeira_visita__gte=inicio)
        .annotate(mes=TruncMonth('primeira_visita'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    data = {
        'novos': [{'mes': r['mes'].strftime('%Y-%m'), 'total': r['total']} for r in novos_por_mes],
        'baptismos': [{'mes': r['mes'].strftime('%Y-%m'), 'total': r['total']} for r in baptismos_por_mes],
        'visitantes': [{'mes': r['mes'].strftime('%Y-%m'), 'total': r['total']} for r in visitantes_por_mes],
    }
    return JsonResponse(data)


@login_required
def pastoral_api_celulas(request):
    """Participação média por célula nas últimas 8 semanas."""
    from datetime import timedelta as td
    hoje = date.today()
    inicio = hoje - td(weeks=8)

    dados = (
        RelatorioSemanalCelula.objects.filter(data_reuniao__gte=inicio)
        .values('nome_celula__designacao')
        .annotate(
            media_membros=Count('numero_participantes_membros'),
            media_visitantes=Count('numero_participantes_visitantes'),
            total_relatorios=Count('id'),
        )
        .order_by('nome_celula__designacao')
    )
    from django.db.models import Avg
    dados = (
        RelatorioSemanalCelula.objects.filter(data_reuniao__gte=inicio)
        .values('nome_celula__designacao')
        .annotate(
            media_membros=Avg('numero_participantes_membros'),
            media_visitantes=Avg('numero_participantes_visitantes'),
            total_relatorios=Count('id'),
        )
        .order_by('nome_celula__designacao')
    )
    result = []
    for d in dados:
        result.append({
            'celula': d['nome_celula__designacao'] or 'Sem Nome',
            'media_membros': round(d['media_membros'] or 0, 1),
            'media_visitantes': round(d['media_visitantes'] or 0, 1),
            'total_relatorios': d['total_relatorios'],
        })
    return JsonResponse(result, safe=False)


@login_required
def pastoral_api_alertas_resumo(request):
    """Contagem de alertas por tipo e estado."""
    por_tipo = list(
        AlertaPastoral.objects.values('tipo').annotate(total=Count('id')).order_by('tipo')
    )
    por_estado = list(
        AlertaPastoral.objects.values('estado').annotate(total=Count('id')).order_by('estado')
    )
    return JsonResponse({'por_tipo': por_tipo, 'por_estado': por_estado})


@login_required
def pastoral_api_casos_resumo(request):
    """Contagem de casos por tipo e estado."""
    por_tipo = list(
        CasoPastoral.objects.values('tipo').annotate(total=Count('id')).order_by('tipo')
    )
    por_estado = list(
        CasoPastoral.objects.values('estado').annotate(total=Count('id')).order_by('estado')
    )
    return JsonResponse({'por_tipo': por_tipo, 'por_estado': por_estado})


# â”€â”€ Relatórios PDF Pastorais â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@login_required
def relatorio_pastoral_selecionar_mes(request):
    """Página de seleção do mês para o relatório pastoral mensal."""
    if not request.user.has_perm('sitetibl.view_casopastoral'):
        messages.error(request, 'Não tem permissão para gerar relatórios pastorais.')
        return redirect('index')

    from django.db.models.functions import TruncMonth
    from django.db.models import Count

    # Recolher todos os meses com pelo menos um registo em qualquer tabela pastoral
    meses_casos = (
        CasoPastoral.objects
        .annotate(mes=TruncMonth('data_abertura'))
        .values_list('mes', flat=True)
        .distinct()
    )
    meses_alertas = (
        AlertaPastoral.objects
        .annotate(mes=TruncMonth('data_criacao'))
        .values_list('mes', flat=True)
        .distinct()
    )
    meses_visitantes = (
        VisitanteRecorrente.objects
        .annotate(mes=TruncMonth('primeira_visita'))
        .values_list('mes', flat=True)
        .distinct()
    )
    meses_membros = (
        Irmao.objects
        .annotate(mes=TruncMonth('data_criacao'))
        .values_list('mes', flat=True)
        .distinct()
    )

    # Juntar e ordenar
    todos_meses = sorted(
        set(
            list(meses_casos) + list(meses_alertas) +
            list(meses_visitantes) + list(meses_membros)
        ),
        reverse=True
    )

    hoje = date.today()
    MESES_PT = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']

    meses_opcoes = [
        {
            'valor': f'{m.year}-{m.month:02d}',
            'label': f'{MESES_PT[m.month - 1]} {m.year}',
        }
        for m in todos_meses
    ]

    # Se não há registos em nenhum mês, mostrar pelo menos o mês actual
    if not meses_opcoes:
        meses_opcoes = [{
            'valor': f'{hoje.year}-{hoje.month:02d}',
            'label': f'{MESES_PT[hoje.month - 1]} {hoje.year}',
        }]

    return render(request, 'relatorio_pastoral_selecionar_mes.html', {
        'meses_opcoes': meses_opcoes,
    })


@login_required
def relatorio_pastoral_mensal_pdf(request):
    """Relatório Pastoral Mensal em PDF."""
    if not request.user.has_perm('sitetibl.view_casopastoral'):
        messages.error(request, 'Não tem permissão para gerar relatórios pastorais.')
        return redirect('index')

    from datetime import timedelta as td
    hoje = date.today()

    # Aceitar mês/ano via GET param (ex: ?mes=2024-03)
    mes_param = request.GET.get('mes', '')
    try:
        ano_sel, mes_sel = int(mes_param.split('-')[0]), int(mes_param.split('-')[1])
        primeiro_dia = date(ano_sel, mes_sel, 1)
    except (ValueError, IndexError, AttributeError):
        primeiro_dia = hoje.replace(day=1)

    # Último dia do mês selecionado
    import calendar
    ultimo_dia = date(primeiro_dia.year, primeiro_dia.month,
                      calendar.monthrange(primeiro_dia.year, primeiro_dia.month)[1])

    MESES_PT = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    label_mes = f'{MESES_PT[primeiro_dia.month - 1]} {primeiro_dia.year}'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_pastoral_{primeiro_dia.strftime("%Y_%m")}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('TituloPastoral', parent=styles['Heading1'], fontSize=16, spaceAfter=12, alignment=1)
    subtitulo_style = ParagraphStyle('SubtituloPastoral', parent=styles['Heading2'], fontSize=12, spaceAfter=8)
    normal = styles['Normal']

    elements = []
    elements.append(Paragraph(f'Relatório Pastoral Mensal — {label_mes}', titulo_style))
    elements.append(Paragraph(f'Gerado em {hoje.strftime("%d/%m/%Y")}', normal))
    elements.append(Paragraph('<br/>', normal))

    # KPIs
    novos_mes = Irmao.objects.filter(data_criacao__date__gte=primeiro_dia, data_criacao__date__lte=ultimo_dia).count()
    baptismos_mes = Irmao.objects.filter(data_criacao__date__gte=primeiro_dia, data_criacao__date__lte=ultimo_dia, batizado=True).count()
    casos_abertos = CasoPastoral.objects.filter(estado__in=['aberto', 'em_acompanhamento']).count()
    casos_resolvidos_mes = CasoPastoral.objects.filter(estado='resolvido', data_atualizacao__date__gte=primeiro_dia, data_atualizacao__date__lte=ultimo_dia).count()
    alertas_mes = AlertaPastoral.objects.filter(data_criacao__date__gte=primeiro_dia, data_criacao__date__lte=ultimo_dia).count()
    visitantes_mes = VisitanteRecorrente.objects.filter(primeira_visita__gte=primeiro_dia, primeira_visita__lte=ultimo_dia).count()

    kpi_data = [
        ['Indicador', 'Valor'],
        ['Novos membros no mês', str(novos_mes)],
        ['Baptismos no mês', str(baptismos_mes)],
        ['Casos pastorais abertos', str(casos_abertos)],
        ['Casos resolvidos no mês', str(casos_resolvidos_mes)],
        ['Alertas gerados no mês', str(alertas_mes)],
        ['Novos visitantes no mês', str(visitantes_mes)],
    ]
    elements.append(Paragraph('Indicadores do Mês', subtitulo_style))
    t = Table(kpi_data, colWidths=[12*cm, 5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ]))
    elements.append(t)
    elements.append(Paragraph('<br/>', normal))

    # Casos em acompanhamento
    casos = CasoPastoral.objects.filter(
        estado__in=['aberto', 'em_acompanhamento']
    ).select_related('membro', 'responsavel').order_by('-prioridade', '-data_abertura')[:20]

    if casos:
        elements.append(Paragraph('Casos em Acompanhamento', subtitulo_style))
        caso_data = [['Membro', 'Tipo', 'Prioridade', 'Estado', 'Responsável']]
        for c in casos:
            caso_data.append([
                str(c.membro),
                c.get_tipo_display(),
                c.get_prioridade_display(),
                c.get_estado_display(),
                str(c.responsavel) if c.responsavel else '—',
            ])
        t2 = Table(caso_data, colWidths=[4*cm, 3*cm, 2.5*cm, 3*cm, 4*cm])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(t2)

    doc.build(elements)
    return response


@login_required
def relatorio_inactivos_pdf(request):
    """PDF com lista de membros inactivos."""
    if not request.user.has_perm('sitetibl.view_casopastoral'):
        messages.error(request, 'Não tem permissão para gerar relatórios pastorais.')
        return redirect('index')

    from datetime import timedelta as td
    from django.db.models import Max
    hoje = date.today()
    limite = hoje - td(days=60)
    activos_ids = Escala.objects.filter(actividade__data__gte=limite).values_list('irmao_id', flat=True).distinct()
    inactivos = (
        Irmao.objects.exclude(id__in=activos_ids)
        .select_related('celula')
        .annotate(ultima_participacao=Max('particact__data'))
        .order_by('ultima_participacao')[:100]
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="membros_inactivos_{hoje.strftime("%Y%m%d")}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=16, alignment=1)
    normal = styles['Normal']

    elements = []
    elements.append(Paragraph('Membros Inactivos (60+ dias)', titulo))
    elements.append(Paragraph(f'Gerado em {hoje.strftime("%d/%m/%Y")}', normal))
    elements.append(Paragraph('<br/>', normal))

    data_table = [['Nome', 'Célula', 'Última Participação', 'Dias Inactivo']]
    for i in inactivos:
        ult = i.ultima_participacao
        dias = (hoje - ult).days if ult else '—'
        data_table.append([
            f'{i.nome} {i.apelido}',
            str(i.celula) if i.celula else '—',
            ult.strftime('%d/%m/%Y') if ult else 'Nunca',
            str(dias),
        ])

    t = Table(data_table, colWidths=[5*cm, 4*cm, 4*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)
    doc.build(elements)
    return response


@login_required
def acta_actividade_pdf(request, actividade_id):
    """Página intermédia para preencher a acta (GET) e geração do PDF (POST)."""
    actividade = get_object_or_404(Actividade, id=actividade_id)
    todas_escalas = Escala.objects.filter(actividade=actividade).select_related('irmao', 'irmao__celula', 'funcao')

    if not todas_escalas.exists():
        messages.error(request, 'Esta actividade não possui escalas associadas.')
        return redirect(reverse('sitetibl:mostra_detalhe', args=['actividades', actividade_id]))

    # Recolher todos os irmãos de todas as escalas (protocolo via M2M + normal via FK), sem duplicados
    irmaos_set = set()
    for esc in todas_escalas:
        if esc.eh_protocolo:
            for i in esc.irmao_protocolo.all():
                irmaos_set.add(i)
        else:
            irmaos_set.add(esc.irmao)
    irmaos_protocolo = sorted(irmaos_set, key=lambda x: x.nome)

    # ── GET: mostrar formulário de preenchimento ──────────────────────────
    if request.method == 'GET':
        return render(request, 'acta_protocolo_form.html', {
            'actividade': actividade,
            'irmaos_protocolo': irmaos_protocolo,
        })

    # ── POST: gerar PDF com os dados submetidos ───────────────────────────
    ESTADO_LABELS = {
        'presente': 'Presente',
        'ausente': 'Ausente',
    }
    CORES_ESTADO = {
        'presente': colors.HexColor('#dcfce7'),
        'ausente':  colors.HexColor('#fee2e2'),
    }

    ocorrencias = request.POST.get('ocorrencias', '').strip()
    nome_responsavel = request.POST.get('nome_responsavel', '').strip()
    nome_secretario  = request.POST.get('nome_secretario', '').strip()

    # Estado de cada irmão
    estados = {}
    for irmao in irmaos_protocolo:
        key = f'estado_{irmao.id}'
        estados[irmao.id] = request.POST.get(key, 'presente')

    # ── Construção do PDF ─────────────────────────────────────────────────
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="acta_actividade_{actividade_id}_{actividade.data}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm,  bottomMargin=2 * cm,
        title=f'Acta da Actividade — {actividade.designacao}',
        author='Sistema TIBL',
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ActaTitle', parent=styles['Title'],
        fontSize=16, leading=20,
        textColor=colors.HexColor('#1e3a5f'),
        alignment=1, spaceAfter=10,
    )
    section_style = ParagraphStyle(
        'ActaSection', parent=styles['Heading2'],
        fontSize=11, leading=14,
        textColor=colors.HexColor('#548c2f'),
        spaceBefore=10, spaceAfter=5, keepWithNext=True,
    )
    body_style = ParagraphStyle(
        'ActaBody', parent=styles['Normal'],
        fontSize=9, leading=13,
        textColor=colors.HexColor('#333333'), spaceAfter=3,
    )
    label_style = ParagraphStyle(
        'ActaLabel', parent=styles['Normal'],
        fontSize=9, leading=13, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e3a5f'),
    )
    sig_style = ParagraphStyle(
        'ActaSig', parent=styles['Normal'],
        fontSize=9, alignment=1,
    )

    elements = []

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'fotos', '2022', 'cba.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=60, height=60)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Paragraph('<b>ACTA DA ACTIVIDADE</b>', title_style))
    elements.append(Paragraph("<hr color='#1e3a5f' width='100%'/>", styles['Normal']))
    elements.append(Paragraph('<br/>', styles['Normal']))

    # ── Cabeçalho da actividade ───────────────────────────────────────────
    info_data = [
        [Paragraph('<b>Actividade:</b>', label_style), Paragraph(str(actividade.designacao), body_style)],
        [Paragraph('<b>Tema:</b>',        label_style), Paragraph(actividade.tema or '—', body_style)],
        [Paragraph('<b>Data:</b>',        label_style), Paragraph(actividade.data.strftime('%d/%m/%Y'), body_style)],
        [Paragraph('<b>Horário:</b>',     label_style), Paragraph(f"{actividade.inicio.strftime('%H:%M')} às {actividade.fim.strftime('%H:%M')}", body_style)],
        [Paragraph('<b>Local:</b>',       label_style), Paragraph(str(actividade.localactividade or 'Sede'), body_style)],
        [Paragraph('<b>Versos Bíblicos:</b>', label_style), Paragraph(actividade.versosbiblicos or '—', body_style)],
        [Paragraph('<b>Hinos:</b>',       label_style), Paragraph(actividade.hinos or '—', body_style)],
    ]
    info_table = Table(info_data, colWidths=[4 * cm, 13 * cm])
    info_table.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 3),
        ('TOPPADDING',   (0, 0), (-1, -1), 3),
        ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(info_table)
    elements.append(Paragraph('<br/>', styles['Normal']))

    # ── Membros do Protocolo ──────────────────────────────────────────────
    elements.append(Paragraph('Membros Escalados', section_style))

    team_header = [
        Paragraph('<b>Nome Completo</b>', label_style),
        Paragraph('<b>Telefone</b>',     label_style),
        Paragraph('<b>Célula</b>',       label_style),
        Paragraph('<b>Presença</b>',     label_style),
    ]
    team_data = [team_header]

    presentes = 0
    ausentes  = 0

    for irmao in irmaos_protocolo:
        estado = estados.get(irmao.id, 'presente')
        cor    = CORES_ESTADO.get(estado, colors.white)
        label  = ESTADO_LABELS.get(estado, estado.capitalize())

        if estado == 'presente':
            presentes += 1
        else:
            ausentes += 1

        row = [
            Paragraph(f'{irmao.nome} {irmao.apelido}', body_style),
            Paragraph(irmao.telefone or '—', body_style),
            Paragraph(str(irmao.celula) if irmao.celula else '—', body_style),
            Paragraph(label, body_style),
        ]
        team_data.append((row, cor))

    # Construir tabela com cores por linha
    raw_rows = [team_header] + [r for r, _ in team_data[1:]]
    team_table = Table(raw_rows, colWidths=[6*cm, 3.5*cm, 3.5*cm, 4*cm])
    style_cmds = [
        ('BACKGROUND',   (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
    ]
    for idx, (_, cor) in enumerate(team_data[1:], start=1):
        style_cmds.append(('BACKGROUND', (0, idx), (-1, idx), cor))
    team_table.setStyle(TableStyle(style_cmds))
    elements.append(team_table)
    elements.append(Paragraph('<br/>', styles['Normal']))

    # Resumo de presenças
    resumo_data = [
        [
            Paragraph(f'<b>Presentes:</b> {presentes}', body_style),
            Paragraph(f'<b>Ausentes:</b> {ausentes}', body_style),
            Paragraph(f'<b>Total:</b> {len(irmaos_protocolo)}', body_style),
        ]
    ]
    resumo_table = Table(resumo_data, colWidths=[5.67*cm, 5.67*cm, 5.66*cm])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX',        (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID',  (0, 0), (-1, -1), 0.4, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(resumo_table)
    elements.append(Paragraph('<br/>', styles['Normal']))

    # ── Ocorrências ───────────────────────────────────────────────────────
    elements.append(Paragraph('Ocorrências / Observações', section_style))
    elements.append(Paragraph(
        ocorrencias if ocorrencias else 'Sem ocorrências registadas.',
        body_style,
    ))
    elements.append(Paragraph('<br/><br/>', styles['Normal']))

    # ── Assinaturas ───────────────────────────────────────────────────────
    elements.append(Paragraph('Assinaturas', section_style))

    linha_resp = nome_responsavel if nome_responsavel else '_' * 38
    linha_sec  = nome_secretario  if nome_secretario  else '_' * 38

    sig_data = [[
        Paragraph(
            f'<br/><br/><br/>______________________________<br/>{linha_resp}<br/><b>Responsável pela Actividade</b>',
            sig_style,
        ),
        Paragraph(
            f'<br/><br/><br/>______________________________<br/>{linha_sec}<br/><b>Secretário(a)</b>',
            sig_style,
        ),
    ]]
    sig_table = Table(sig_data, colWidths=[8.5 * cm, 8.5 * cm])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN',  (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(sig_table)

    # Data de emissão
    elements.append(Paragraph('<br/>', styles['Normal']))
    elements.append(Paragraph(
        f'Emitido em {date.today().strftime("%d/%m/%Y")} pelo Sistema TIBL',
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8,
                       textColor=colors.HexColor('#94a3b8'), alignment=2),
    ))

    doc.build(elements, onFirstPage=_desenhar_rodape_pdf, onLaterPages=_desenhar_rodape_pdf)
    return response

