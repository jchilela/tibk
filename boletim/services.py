"""Regras de negócio do boletim.

As funções que alimentam as páginas públicas devolvem dicionários simples
com os campos estritamente necessários: nenhum objecto ``Irmao`` (com
telefone, email, etc.) chega aos templates públicos.
"""
import hashlib
import re
from collections import OrderedDict
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone

from boletim.models import (
    Boletim, ConfiguracaoBoletim, FuncaoBoletim, ItemOrdemCulto, ProgramaSemanal,
)
from boletim.textos import TEXTOS, data_extenso, hora, tr
from sitetibl.models import Actividade, Anuncio, Escala, NotificacaoSistema, VisitanteRecorrente


# ── Selecção de boletins ─────────────────────────────────────

def boletins_publicados():
    return (Boletim.objects
            .filter(estado=Boletim.ESTADO_PUBLICADO)
            .select_related('actividade', 'actividade__designacao'))


def boletim_actual(hoje=None):
    """Próximo boletim publicado (a partir de hoje); na falta dele, o último."""
    hoje = hoje or date.today()
    qs = boletins_publicados()
    proximo = qs.filter(actividade__data__gte=hoje).order_by('actividade__data', 'actividade__inicio', 'id').first()
    if proximo:
        return proximo
    return qs.order_by('-actividade__data', '-actividade__inicio', '-id').first()


def boletins_da_data(d):
    return list(boletins_publicados().filter(actividade__data=d).order_by('actividade__inicio', 'id'))


JANELA_DIAS = 7


def _fim_janela(hoje):
    return hoje + timedelta(days=JANELA_DIAS)


def _agora():
    """Hora local da igreja. Com USE_TZ desligado, é a hora do sistema."""
    if settings.USE_TZ:
        return timezone.localtime()
    return timezone.now()


def _q_proximos(agora, hoje, prefixo=''):
    """Ainda não terminou: dias futuros da janela, ou hoje com hora de fim por vir."""
    data = f'{prefixo}data'
    fim = f'{prefixo}fim'
    return (
        Q(**{f'{data}__gt': hoje, f'{data}__lte': _fim_janela(hoje)})
        | Q(**{data: hoje, f'{fim}__gte': agora.time()})
    )


def _url_culto(boletim):
    return reverse('boletim:data', args=[boletim.actividade.data.isoformat()]) + f'?culto={boletim.id}'


def _cartao_culto(boletim, lingua):
    act = boletim.actividade
    return {
        'hora': hora(act.inicio),
        'inicio_iso': f'{act.data.isoformat()}T{act.inicio.isoformat()}' if act.inicio else act.data.isoformat(),
        'titulo': tr(lingua, boletim.titulo_pt, boletim.titulo_en),
        'nome': str(act.designacao),
        'tema': act.tema or '',
        'url': _url_culto(boletim),
    }


def cultos_para_escolher(hoje, lingua, agora=None):
    """Boletins publicados que ainda não terminaram, agrupados por dia.

    Um culto do passado não entra. O segundo valor fica falso: a página
    inicial não mostra boletins anteriores.
    """
    agora = agora or _agora()
    boletins = list(
        boletins_publicados()
        .filter(_q_proximos(agora, hoje, 'actividade__'))
        .order_by('actividade__data', 'actividade__inicio', 'id')
    )
    anteriores = False
    dias = []
    grupo = None
    for boletim in boletins:
        dia = boletim.actividade.data
        if grupo is None or grupo['data'] != dia:
            grupo = {'data': dia, 'data_extenso': data_extenso(dia, lingua), 'cultos': []}
            dias.append(grupo)
        grupo['cultos'].append(_cartao_culto(boletim, lingua))
    return dias, anteriores


def eventos_da_semana(hoje, lingua, agora=None):
    """Actividades que ainda não terminaram. O url só existe com boletim publicado."""
    agora = agora or _agora()
    actividades = (Actividade.objects
                   .filter(_q_proximos(agora, hoje))
                   .exclude(is_recorrente=True, parent_event__isnull=True)
                   .select_related('designacao', 'localactividade')
                   .order_by('data', 'inicio', 'id'))
    publicados = {
        boletim.actividade_id: boletim
        for boletim in boletins_publicados().filter(_q_proximos(agora, hoje, 'actividade__'))
    }
    eventos = []
    for act in actividades:
        boletim = publicados.get(act.id)
        eventos.append({
            'data_extenso': data_extenso(act.data, lingua),
            'hora': hora(act.inicio),
            'titulo': str(act.designacao),
            'tema': act.tema or '',
            'local': act.localactividade.designacao if act.localactividade_id else '',
            'url': _url_culto(boletim) if boletim else '',
        })
    return eventos


# ── Conteúdo ─────────────────────────────────────────────────

def anuncios_para_data(d):
    """Anúncios públicos válidos na data ``d``."""
    return (Anuncio.objects
            .filter(publico=True)
            .filter(Q(data_inicio__lte=d, data_fim__gte=d) | Q(data_fim__isnull=True, data_inicio=d))
            .order_by('ordem', 'id'))


def escalas_do_boletim(actividade, lingua):
    """Escalas do culto, só das funções com FuncaoBoletim, pela ordem definida.

    Devolve [{'rotulo': str, 'nomes': [str, ...], 'designacao': str}, ...].
    Só se lêem o nome e o apelido de cada irmão.
    """
    funcoes = OrderedDict(
        (fb.funcao_id, fb) for fb in FuncaoBoletim.objects.select_related('funcao').order_by('ordem', 'id')
    )
    if not funcoes:
        return []
    nomes = {fid: [] for fid in funcoes}

    linhas = (Escala.objects
              .filter(actividade=actividade, funcao_id__in=list(funcoes))
              .order_by('id')
              .values('id', 'funcao_id', 'eh_protocolo', 'irmao__nome', 'irmao__apelido'))
    protocolo_ids = []
    for linha in linhas:
        nome = _nome_publico(linha['irmao__nome'], linha['irmao__apelido'])
        if nome and nome not in nomes[linha['funcao_id']]:
            nomes[linha['funcao_id']].append(nome)
        if linha['eh_protocolo']:
            protocolo_ids.append(linha['id'])

    if protocolo_ids:
        extra = (Escala.irmao_protocolo.through.objects
                 .filter(escala_id__in=protocolo_ids)
                 .values('escala__funcao', 'irmao__nome', 'irmao__apelido'))
        for linha in extra:
            nome = _nome_publico(linha['irmao__nome'], linha['irmao__apelido'])
            fid = linha['escala__funcao']
            if nome and nome not in nomes[fid]:
                nomes[fid].append(nome)

    resultado = []
    for fid, fb in funcoes.items():
        if nomes[fid]:
            resultado.append({
                'rotulo': tr(lingua, fb.rotulo_pt, fb.rotulo_en),
                'designacao': fb.funcao.designacao,
                'nomes': nomes[fid],
            })
    return resultado


def _nome_publico(nome, apelido):
    return ' '.join(p.strip() for p in (nome or '', apelido or '') if p and p.strip())


def programas_semanais(lingua):
    dias = TEXTOS[lingua]['dias']
    resultado = []
    for p in ProgramaSemanal.objects.filter(activo=True):
        horario = hora(p.hora_inicio)
        if p.hora_fim:
            horario += '–' + hora(p.hora_fim)
        resultado.append({
            'dia': dias[p.dia_semana],
            'horario': horario,
            'titulo': tr(lingua, p.titulo_pt, p.titulo_en),
        })
    return resultado


def configuracao_publica(lingua):
    cfg = ConfiguracaoBoletim.obter()
    redes = []
    for chave, nome, url in (
        ('youtube', 'YouTube', cfg.youtube_url),
        ('facebook', 'Facebook', cfg.facebook_url),
        ('instagram', 'Instagram', cfg.instagram_url),
        ('site', TEXTOS[lingua]['site'], cfg.site_url),
    ):
        if url:
            redes.append({'chave': chave, 'nome': nome, 'url': url})
    return {
        'nome_igreja': tr(lingua, cfg.nome_igreja_pt, cfg.nome_igreja_en),
        'congregacao': tr(lingua, cfg.congregacao_pt, cfg.congregacao_en),
        'lideranca': [l.strip() for l in cfg.lideranca_pastoral.splitlines() if l.strip()],
        'redes': redes,
    }


def contexto_boletim(boletim, lingua):
    """Todos os dados (já traduzidos) de que a página e o PDF precisam."""
    act = boletim.actividade
    itens = [
        {'titulo': tr(lingua, i.titulo_pt, i.titulo_en), 'detalhe': i.detalhe}
        for i in ItemOrdemCulto.objects.filter(boletim=boletim).order_by('ordem', 'id')
    ]
    anuncios = [
        {
            'id': a.id,
            'titulo': tr(lingua, a.titulo, a.titulo_en),
            'texto': tr(lingua, a.texto, a.texto_en),
            'tem_calendario': bool(a.actividade_id),
        }
        for a in anuncios_para_data(act.data)
    ]
    escalas = escalas_do_boletim(act, lingua)
    return {
        'id': boletim.id,
        'publicado': boletim.publicado,
        'titulo': tr(lingua, boletim.titulo_pt, boletim.titulo_en),
        'data': act.data,
        'data_iso': act.data.isoformat(),
        'data_extenso': data_extenso(act.data, lingua),
        'hora_inicio': hora(act.inicio),
        'tema': act.tema,
        'itens': itens,
        'leitura_referencia': boletim.leitura_referencia,
        'leitura_texto': tr(lingua, boletim.leitura_texto_pt, boletim.leitura_texto_en),
        'hino_referencia': boletim.hino_referencia,
        'hino_letra': boletim.hino_letra,
        'escalas': escalas,
        'anuncios': anuncios,
        'programas': programas_semanais(lingua),
        'link_transmissao': boletim.link_transmissao,
        'link_gravacao': boletim.link_gravacao,
        'notas_sermao': boletim.notas_sermao,
        'pregador': pregador(escalas),
    }


def pregador(escalas):
    """Nome(s) de quem prega, deduzido pelo nome da função ou do rótulo."""
    for e in escalas:
        texto = f"{e['designacao']} {e['rotulo']}".lower()
        if 'pregador' in texto or 'pregação' in texto or 'pregacao' in texto or 'preacher' in texto:
            return ', '.join(e['nomes'])
    return ''


def mensagem_whatsapp(boletim, url_publico):
    ctx = contexto_boletim(boletim, 'pt')
    linhas = [f"*{ctx['titulo']}*", ctx['data_extenso']]
    if ctx['hora_inicio']:
        linhas[-1] += f" · {ctx['hora_inicio']}"
    if ctx['pregador']:
        linhas.append(f"Pregador: {ctx['pregador']}")
    if ctx['tema']:
        linhas.append(f"Tema: {ctx['tema']}")
    linhas.append('')
    linhas.append(f'Boletim: {url_publico}')
    return '\n'.join(linhas)


# ── Telefones ────────────────────────────────────────────────

def normalizar_telefone(valor):
    """Só dígitos, sem indicativo de Angola (+244 / 00244)."""
    digitos = re.sub(r'\D', '', valor or '')
    if digitos.startswith('00'):
        digitos = digitos[2:]
    if digitos.startswith('244') and len(digitos) == 12:
        digitos = digitos[3:]
    return digitos


def encontrar_visitante(telefone_normalizado):
    if len(telefone_normalizado) < 4:
        return None
    candidatos = VisitanteRecorrente.objects.filter(telefone__contains=telefone_normalizado[-4:])
    for v in candidatos.order_by('-ultima_visita', '-id'):
        if normalizar_telefone(v.telefone) == telefone_normalizado:
            return v
    # Números gravados com espaços (ex.: «923 456 789») não contêm os 4
    # últimos dígitos seguidos; segunda passagem mais larga.
    for v in VisitanteRecorrente.objects.filter(telefone__contains=telefone_normalizado[-2:]).order_by('-ultima_visita', '-id'):
        if normalizar_telefone(v.telefone) == telefone_normalizado:
            return v
    return None


def registar_visitante(dados, hoje=None):
    """Cria ou actualiza o VisitanteRecorrente. Devolve (visitante, criado)."""
    hoje = hoje or date.today()
    telefone = normalizar_telefone(dados['telefone'])
    nota = '[{}] Cartão de visitante (boletim digital). Primeira vez: {}.{} Consentimento para ser contactado: sim.'.format(
        hoje.strftime('%d/%m/%Y'),
        'sim' if dados.get('primeira_vez') == 'sim' else 'não',
        f" Como soube: {dados['como_soube'].strip()}." if dados.get('como_soube', '').strip() else '',
    )
    visitante = encontrar_visitante(telefone)
    if visitante:
        if visitante.ultima_visita != hoje:
            visitante.numero_visitas = F('numero_visitas') + 1
            visitante.ultima_visita = hoje
        if dados.get('email') and not visitante.email:
            visitante.email = dados['email']
        visitante.observacao = (visitante.observacao + '\n' + nota).strip()
        visitante.save()
        visitante.refresh_from_db()
        return visitante, False
    visitante = VisitanteRecorrente.objects.create(
        nome=dados['nome'].strip(),
        telefone=telefone,
        email=dados.get('email') or '',
        primeira_visita=hoje,
        ultima_visita=hoje,
        numero_visitas=1,
        observacao=nota,
    )
    return visitante, True


# ── Notificações ─────────────────────────────────────────────

def notificar_grupos(grupos, titulo, mensagem, url=''):
    utilizadores = User.objects.filter(is_active=True, groups__name__in=grupos).distinct()
    NotificacaoSistema.objects.bulk_create([
        NotificacaoSistema(destinatario=u, titulo=titulo, mensagem=mensagem, url=url)
        for u in utilizadores
    ])


# ── Protecção dos formulários ────────────────────────────────

def ip_cliente(request):
    if getattr(settings, 'BOLETIM_TRUST_PROXY', False):
        xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if xff:
            return xff.split(',')[0].strip()
        real = request.META.get('HTTP_X_REAL_IP', '')
        if real:
            return real.strip()
    return request.META.get('REMOTE_ADDR', '') or ''


def hash_ip(ip):
    salt = getattr(settings, 'BOLETIM_IP_SALT', '') or hashlib.sha256(
        ('boletim-ip:' + (settings.SECRET_KEY or '')).encode()).hexdigest()
    return hashlib.sha256((salt + '|' + ip).encode()).hexdigest()


def _chave_limite(formulario, ip_h):
    return f'boletim:limite:{formulario}:{ip_h}'


def limite_excedido(formulario, ip_h):
    limite = getattr(settings, 'BOLETIM_LIMITE_SUBMISSOES', 5)
    return (cache.get(_chave_limite(formulario, ip_h)) or 0) >= limite


def contar_submissao(formulario, ip_h):
    chave = _chave_limite(formulario, ip_h)
    if cache.add(chave, 1, 3600):
        return
    try:
        cache.incr(chave)
    except ValueError:
        cache.set(chave, 1, 3600)
