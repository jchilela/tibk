import logging

from django.contrib.auth.models import Group, User
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
from django.utils.crypto import get_random_string

from .models import Departamento, EnvioMensagem, Escala, Irmao, Mandato, PedidoSaida, Dizimooferta, Entrada, Actividade
from .sms import enviar_sms

logger = logging.getLogger(__name__)

from django.conf import settings as django_settings


# =========================================
# � GRUPOS AUTOMÁTICOS — IRMÃO
# =========================================

GRUPO_GERAL = 'Membro Geral'
GRUPO_BATIZADOS = 'Membros Baptizados'


def _atribuir_grupos_irmao(user, categoria):
    """Garante que o user tem os grupos base correctos conforme a categoria."""
    try:
        user.groups.add(Group.objects.get(name=GRUPO_GERAL))
    except Group.DoesNotExist:
        logger.warning('Grupo "%s" não encontrado — verifique o seeder.', GRUPO_GERAL)
    try:
        grupo_batizados = Group.objects.get(name=GRUPO_BATIZADOS)
        if categoria == 'membro_batizado':
            user.groups.add(grupo_batizados)
        else:
            user.groups.remove(grupo_batizados)
    except Group.DoesNotExist:
        logger.warning('Grupo "%s" não encontrado — verifique o seeder.', GRUPO_BATIZADOS)


@receiver(pre_save, sender=Irmao)
def _guardar_categoria_anterior(sender, instance, **kwargs):
    """Memoriza a categoria actual antes de qualquer actualização."""
    if instance.pk:
        try:
            instance._categoria_anterior = (
                Irmao.objects.values_list('categoria', flat=True).get(pk=instance.pk)
            )
        except Irmao.DoesNotExist:
            instance._categoria_anterior = None
    else:
        instance._categoria_anterior = None


@receiver(post_save, sender=Irmao)
def _gerir_grupos_irmao(sender, instance, created, **kwargs):
    """
    Atribui grupos quando:
    - Irmão criado com user já vinculado (created=True, user not None)
    - categoria muda em actualização
    """
    user = instance.user
    if not user:
        # Será tratado em criar_user_para_irmao após criar o user
        return

    if created:
        _atribuir_grupos_irmao(user, instance.categoria)
        return

    categoria_anterior = getattr(instance, '_categoria_anterior', None)
    if categoria_anterior is not None and instance.categoria != categoria_anterior:
        _atribuir_grupos_irmao(user, instance.categoria)


# =========================================
# �👤 AUTO-CRIAR USER AO CRIAR IRMÃO
# =========================================

@receiver(post_save, sender=Irmao)
def criar_user_para_irmao(sender, instance, created, **kwargs):
    """
    Quando um Irmao é guardado sem User associado, cria automaticamente
    um User Django e envia as credenciais por email ou SMS.
    """
    if instance.user is not None:
        return

    # Gerar username unico: email (parte antes do @) ou nome.apelido
    if instance.email:
        base_username = instance.email.split('@')[0].lower().replace(' ', '')
    else:
        base_username = f'{instance.nome}.{instance.apelido}'.lower().replace(' ', '')
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f'{base_username}{counter}'
        counter += 1

    # Gerar palavra-passe temporaria segura (12 caracteres)
    temp_password = get_random_string(length=12)

    user = User.objects.create_user(
        username=username,
        email=instance.email or '',
        password=temp_password,
        first_name=instance.nome or '',
        last_name=instance.apelido or '',
    )

    # Vincular sem disparar o signal novamente
    Irmao.objects.filter(pk=instance.pk).update(user=user)

    # Atribuir grupos base imediatamente após criar o user
    _atribuir_grupos_irmao(user, instance.categoria)

    logger.info('User "%s" criado para Irmao ID %s', username, instance.pk)

    enviar_credenciais(instance, username, temp_password)


def _telefone_irmao(irmao):
    """Devolve o primeiro telefone disponível (telefone ou WhatsApp)."""
    for campo in ('telefone', 'telefonewhatsapp'):
        valor = (getattr(irmao, campo, None) or '').strip()
        if valor:
            return valor
    return ''


def enviar_credenciais(irmao, username, password):
    """
    Envia credenciais por email e/ou SMS.
    Retorna True se pelo menos um canal foi enviado com sucesso.
    """
    email = (irmao.email or '').strip()
    telefone = _telefone_irmao(irmao)

    if not email and not telefone:
        logger.warning(
            'Irmao ID %s sem email nem telefone — credenciais nao enviadas. '
            'Username: %s', irmao.pk, username,
        )
        return False

    if email:
        if _enviar_credenciais_email(irmao, username, password):
            return True
        if telefone:
            logger.warning(
                'Email falhou para Irmao ID %s — a tentar SMS para %s.',
                irmao.pk, telefone,
            )
            return _enviar_credenciais_sms(irmao, username, password)
        return False

    return _enviar_credenciais_sms(irmao, username, password)


def _enviar_credenciais_email(irmao, username, password):
    """Envia email de boas-vindas com credenciais de acesso."""
    email = (irmao.email or '').strip()
    if not email:
        return False
    try:
        html_content = render_to_string(
            'emails/email_boas_vindas.html',
            {
                'nome': irmao.nome,
                'username': username,
                'password': password,
            },
        )

        msg = EmailMultiAlternatives(
            subject='Bem-vindo ao sistema TIBL — As suas credenciais de acesso',
            body=f'Olá {irmao.nome}, o seu acesso ao TIBL foi criado. '
                 f'Utilizador: {username} | Palavra-passe temporária: {password} '
                 f'| Aceda em: https://gestao.tibl.ao',
            from_email=getattr(django_settings, 'EMAIL_HOST_USER', None) or None,
            to=[email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        logger.info('Email de boas-vindas enviado para %s', email)
        return True
    except Exception as e:
        logger.error('Falha ao enviar email de boas-vindas para %s: %s', email, e)
        return False


def _enviar_credenciais_sms(irmao, username, password):
    """Envia SMS com credenciais de acesso via TelcoSMS."""
    telefone = _telefone_irmao(irmao)
    if not telefone:
        return False
    mensagem = (
        f'TIBL - Bem-vindo {irmao.nome}! '
        f'Utilizador: {username} | Senha: {password} '
        f'Altere a senha no primeiro acesso. '
        f'Aceda em: https://gestao.tibl.ao'
    )
    return enviar_sms(telefone, mensagem)



# =========================================
# 📬 NOTIFICAÇÃO DE MUDANÇA DE ESTADO — PEDIDOS DE SAÍDA
# =========================================

ESTADO_CONFIG = {
    'em_analise': {
        'titulo': 'Pedido em Análise',
        'mensagem': 'O seu pedido de saída de caixa está a ser analisado pela equipa financeira.',
        'estado_display': 'Em Análise',
        'destino': 'requerente',
    },
    'aprovado': {
        'titulo': 'Pedido Aprovado',
        'mensagem': 'O seu pedido de saída de caixa foi aprovado e aguarda efectivação do pagamento.',
        'estado_display': 'Aprovado',
        'destino': 'requerente',
    },
    'rejeitado': {
        'titulo': 'Pedido Rejeitado',
        'mensagem': 'O seu pedido de saída de caixa foi rejeitado. Consulte a observação abaixo.',
        'estado_display': 'Rejeitado',
        'destino': 'requerente',
    },
    'pago': {
        'titulo': 'Pagamento Efectuado',
        'mensagem': 'O pagamento referente ao seu pedido de saída de caixa foi efectuado.',
        'estado_display': 'Pago',
        'destino': 'requerente_e_lideres',
    },
}


def notificar_mudanca_estado_pedido(pedido, novo_estado, aprovador_irmao=None):
    """
    Envia e-mail de notificação sempre que o estado de um PedidoSaida muda.
    Chamado directamente a partir da view após cada acção bem-sucedida.
    """
    config = ESTADO_CONFIG.get(novo_estado)
    if not config:
        return

    from_email = 'noreply@suaigreja.ao'
    emails_destino = []

    # Requerente
    if pedido.requerente and pedido.requerente.email:
        emails_destino.append(pedido.requerente.email)

    # Para 'pago', notificar também líderes do departamento
    if config['destino'] == 'requerente_e_lideres' and pedido.departamento:
        dept = pedido.departamento
        if dept.lider_departamento and dept.lider_departamento.email:
            if dept.lider_departamento.email not in emails_destino:
                emails_destino.append(dept.lider_departamento.email)
        if dept.vice_lider_departamento and dept.vice_lider_departamento.email:
            if dept.vice_lider_departamento.email not in emails_destino:
                emails_destino.append(dept.vice_lider_departamento.email)

    if emails_destino:
        aprovador_nome = ''
        if aprovador_irmao:
            aprovador_nome = f'{aprovador_irmao.nome} {aprovador_irmao.apelido}'

        try:
            html_content = render_to_string(
                'emails/email_pedido_saida_estado.html',
                {
                    'titulo': config['titulo'],
                    'mensagem': config['mensagem'],
                    'novo_estado': novo_estado,
                    'estado_display': config['estado_display'],
                    'projecto': pedido.projecto,
                    'montante': pedido.montante,
                    'moeda': pedido.moeda.abreviatura if pedido.moeda else '',
                    'departamento': pedido.departamento.designacao if pedido.departamento else '',
                    'aprovador': aprovador_nome,
                    'observacao': pedido.observacao_aprovador or '',
                }
            )

            connection = get_connection()
            connection.open()
            msg = EmailMultiAlternatives(
                subject=f'{config["titulo"]} — #{pedido.id} {pedido.projecto}',
                body=config['mensagem'],
                from_email=from_email,
                to=emails_destino,
                connection=connection,
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            connection.close()
        except Exception:
            logger.exception('Erro ao enviar notificação de mudança de estado do pedido #%s', pedido.id)

    # SMS ao requerente se tiver telefone mas não email (ou adicionalmente)
    if pedido.requerente and getattr(pedido.requerente, 'telefone', None):
        mensagem_sms = (
            f'TIBL — {config["titulo"]}: '
            f'Pedido #{pedido.id} ({pedido.projecto}). '
            f'{config["mensagem"]}'
        )
        enviar_sms(pedido.requerente.telefone, mensagem_sms)


# =========================================
# 📬 NOTIFICAÇÃO DE CRIAÇÃO — PEDIDOS DE SAÍDA (FINANCEIRO + LÍDERES)
# =========================================

@receiver(post_save, sender=PedidoSaida)
def notificar_lideres_departamento(sender, instance, created, **kwargs):
    if not created:
        return

    emails_destino = []
    telefones = []

    subject = 'Pedido de Saída de Caixa - TIBL'
    from_email = 'noreply@suaigreja.ao'

    # Apenas membros do grupo Financeiro
    try:
        grupo_financeiro = Group.objects.get(name='Financeiro')
        for user in grupo_financeiro.user_set.select_related('irmao').all():
            irmao = getattr(user, 'irmao', None)
            if irmao:
                if irmao.email and irmao.email not in emails_destino:
                    emails_destino.append(irmao.email)
                if getattr(irmao, 'telefone', None) and irmao.telefone not in telefones:
                    telefones.append(irmao.telefone)
    except Group.DoesNotExist:
        logger.warning('Grupo "Financeiro" não encontrado — notificação de pedido de saída não enviada.')

    # ---------- EMAIL ----------
    if emails_destino:
        connection = get_connection()
        connection.open()

        html_content = render_to_string(
            'emails/email_pedido_saida_de_caixa_lideres.html',
            {
                'projecto': instance.projecto,
                'montante': instance.montante,
                'moeda': instance.moeda.abreviatura if instance.moeda else '',
                'justificativa': instance.justificativa_custo,
                'requerente': instance.requerente,
            }
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            body='Novo pedido de saída de caixa.',
            from_email=from_email,
            to=emails_destino,
            connection=connection
        )

        msg.attach_alternative(html_content, "text/html")
        msg.send()

        connection.close()

    
    # ---------- SMS ----------
    mensagem_sms = (
        f'TIBL — Novo pedido de saída de caixa: '
        f'{instance.projecto or "sem título"}, '
        f'Montante: {instance.montante} {instance.moeda.abreviatura if instance.moeda else ""}. '
        f'Requerente: {instance.requerente}.'
    )
    enviar_sms(telefones, mensagem_sms)


# =========================================
# � NOTIFICAÇÃO IMEDIATA AO SER ESCALADO
# =========================================

def enviar_notificacao_irmao_escalado(instance):
    """Envia email e/ou SMS ao irmão para uma escala específica."""

    irmao = instance.irmao
    actividade = instance.actividade

    if not irmao:
        return

    data_fmt = actividade.data.strftime('%d/%m/%Y') if actividade.data else '—'
    funcao_str = str(instance.funcao) if instance.funcao else 'Sem função específica'
    actividade_str = str(actividade.designacao)

    # ---------- EMAIL ----------
    if irmao.email:
        try:
            context = {
                'nome': irmao.nome,
                'apelido': irmao.apelido,
                'actividade': actividade_str,
                'data': data_fmt,
                'hora': actividade.inicio if actividade.inicio else '',
                'local': str(actividade.localactividade) if actividade.localactividade else '',
                'funcao': funcao_str,
                'departamento': str(actividade.departamento) if actividade.departamento else '',
            }
            html_content = render_to_string('emails/confirmacao_escala.html', context)
            from django.utils.html import strip_tags
            msg = EmailMultiAlternatives(
                subject=f'Confirmação de Escala — {actividade_str} ({data_fmt})',
                body=strip_tags(html_content),
                from_email=None,
                to=[irmao.email],
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            logger.info('Email de escala enviado para %s (Escala ID %s)', irmao.email, instance.pk)
        except Exception:
            logger.exception('Erro ao enviar email de escala ID %s', instance.pk)
    else:
        logger.info('Escala ID %s: irmão sem email — email ignorado.', instance.pk)

    # ---------- SMS ----------
    if getattr(irmao, 'telefone', None):
        mensagem_sms = (
            f'TIBL — Está escalado para {actividade_str} no dia {data_fmt}'
            f'{" às " + str(actividade.inicio) if actividade.inicio else ""}. '
            f'Função: {funcao_str}.'
        )
        enviar_sms(irmao.telefone, mensagem_sms)
    else:
        logger.info('Escala ID %s: irmão sem telefone — SMS ignorado.', instance.pk)


@receiver(post_save, sender=Escala)
def notificar_irmao_escalado(sender, instance, created, **kwargs):
    """
    Envia email e/ou SMS ao irmão quando é adicionado a uma escala.
    """
    if not created:
        return

    enviar_notificacao_irmao_escalado(instance)


# =========================================
# 🔗 AUTO-LINK DIZIMOS COM ENTRADAS (BANCO)
# =========================================
# Sentido: Entrada (tipo=banco) salva → vincula automaticamente Dizimooferta correspondente

def tentar_vincular_banco_com_dizimos(entrada):
    """
    Tenta vincular automaticamente uma entrada bancária com dízimos.
    Critérios:
    - Mesma data
    - Mesmo valor
    - Mesma moeda
    - Ainda não vinculados
    """
    try:
        # Procura dízimos que correspondam
        dizimos = Dizimooferta.objects.filter(
            datacorrespondente=entrada.data,
            valor=entrada.valor,
            moeda=entrada.moeda,
            entrada__isnull=True
        )

        for dizimo in dizimos:
            Dizimooferta.objects.filter(pk=dizimo.pk).update(entrada=entrada)
            logger.info('Entrada Bancaria ID %s vinculada com Dizimo ID %s', entrada.id, dizimo.id)
    except Exception as e:
        logger.error('Erro ao vincular entrada bancaria ID %s: %s', entrada.id, e)


@receiver(post_save, sender=Entrada)
def auto_vincular_entrada_com_dizimos(sender, instance, created, **kwargs):
    """
    Signal que dispara quando uma entrada é criada ou atualizada.
    Se for tipo=banco, procura dízimos/ofertas com mesma data, valor e moeda e vincula automaticamente.
    """
    if instance.tipo == 'banco':
        tentar_vincular_banco_com_dizimos(instance)


# =========================================
# 🏪 AUTO-LINK DIZIMOS COM ENTRADAS (CAIXA)
# =========================================
# Sentido: Entrada (tipo=caixa) salva → vincula automaticamente Dizimooferta correspondente

def tentar_vincular_caixa_com_dizimos(entrada):
    """
    Tenta vincular automaticamente uma entrada de caixa com dízimos.
    Critérios:
    - Mesma data
    - Mesmo valor
    - Mesma moeda
    - Ainda não vinculados
    """
    try:
        # Procura dízimos que correspondam
        dizimos = Dizimooferta.objects.filter(
            datacorrespondente=entrada.data,
            valor=entrada.valor,
            moeda=entrada.moeda,
            entrada__isnull=True
        )

        for dizimo in dizimos:
            Dizimooferta.objects.filter(pk=dizimo.pk).update(entrada=entrada)
            logger.info('Entrada Caixa ID %s vinculada com Dizimo ID %s', entrada.id, dizimo.id)
    except Exception as e:
        logger.error('Erro ao vincular entrada caixa ID %s: %s', entrada.id, e)


@receiver(post_save, sender=Entrada)
def auto_vincular_entrada_caixa_com_dizimos(sender, instance, created, **kwargs):
    """
    Signal que dispara quando uma entrada de caixa é criada ou atualizada.
    Procura dízimos/ofertas com mesma data, valor e moeda e vincula automaticamente.
    """
    if instance.tipo == 'caixa':
        tentar_vincular_caixa_com_dizimos(instance)


# =========================================
# 🔄 SINCRONIZAR DEPARTAMENTO AO APAGAR MANDATO
# =========================================

@receiver(post_delete, sender=Mandato)
def limpar_lider_ao_apagar_mandato(sender, instance, **kwargs):
    """
    Quando um Mandato é apagado, se era líder ou vice-líder,
    limpa o FK correspondente no Departamento e sincroniza grupos.
    """
    if instance.funcao == 'lider':
        Departamento.objects.filter(
            pk=instance.departamento_id,
            lider_departamento=instance.irmao,
        ).update(lider_departamento=None)
    elif instance.funcao == 'vice_lider':
        Departamento.objects.filter(
            pk=instance.departamento_id,
            vice_lider_departamento=instance.irmao,
        ).update(vice_lider_departamento=None)
    try:
        irmao = Irmao.objects.select_related('user').get(pk=instance.irmao_id)
        _sincronizar_grupos_lideranca(irmao)
    except Irmao.DoesNotExist:
        pass


# =========================================
# 👥 SINCRONIZAÇÃO DE GRUPOS DE LIDERANÇA
# =========================================

_GRUPO_LIDER = 'Líder de Departamento'
_GRUPO_VICE_LIDER = 'Vice-Líder de Departamento'
_GRUPO_SEC_DEPT = 'Secretário departamental'
_GRUPO_SEC_GERAL = 'Secretário Geral'


def _sincronizar_grupos_lideranca(irmao):
    """
    Garante que os grupos 'Líder de Departamento', 'Vice-Líder de Departamento'
    e 'Secretário departamental' reflectem o estado actual dos Mandatos para este irmão.
    Chamada sempre que lider_departamento ou vice_lider_departamento mudam,
    quer via edição de Departamento quer via criação/edição/eliminação de Mandato.
    """
    if not irmao or not irmao.user_id:
        return
    try:
        user = irmao.user
    except Exception:
        return

    try:
        grupo_lider = Group.objects.get(name=_GRUPO_LIDER)
        grupo_vice = Group.objects.get(name=_GRUPO_VICE_LIDER)
        grupo_sec = Group.objects.get(name=_GRUPO_SEC_DEPT)
        grupo_sec_geral = Group.objects.get(name=_GRUPO_SEC_GERAL)
    except Group.DoesNotExist:
        logger.warning('Grupos de liderança não encontrados — execute seed_config_essencial')
        return

    e_lider = Departamento.objects.filter(lider_departamento=irmao).exists()
    e_vice = Departamento.objects.filter(vice_lider_departamento=irmao).exists()
    e_sec = irmao.mandato_set.filter(funcao='secretario').exists()
    e_sec_geral = irmao.mandato_set.filter(funcao='secretario_geral').exists()

    if e_lider:
        user.groups.add(grupo_lider)
    else:
        user.groups.remove(grupo_lider)

    if e_vice:
        user.groups.add(grupo_vice)
    else:
        user.groups.remove(grupo_vice)

    if e_sec:
        user.groups.add(grupo_sec)
    else:
        user.groups.remove(grupo_sec)

    if e_sec_geral:
        user.groups.add(grupo_sec_geral)
    else:
        user.groups.remove(grupo_sec_geral)


# Signal: Departamento pre_save — captura valores anteriores
@receiver(pre_save, sender=Departamento)
def departamento_pre_save_lideranca(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Departamento.objects.get(pk=instance.pk)
            instance._old_lider_id = old.lider_departamento_id
            instance._old_vice_lider_id = old.vice_lider_departamento_id
        except Departamento.DoesNotExist:
            instance._old_lider_id = None
            instance._old_vice_lider_id = None
    else:
        instance._old_lider_id = None
        instance._old_vice_lider_id = None


# Signal: Departamento post_save — sincroniza grupos para lider/vice afectados
@receiver(post_save, sender=Departamento)
def departamento_post_save_lideranca(sender, instance, **kwargs):
    ids_afectados = set(filter(None, [
        getattr(instance, '_old_lider_id', None),
        getattr(instance, '_old_vice_lider_id', None),
        instance.lider_departamento_id,
        instance.vice_lider_departamento_id,
    ]))
    for irmao_id in ids_afectados:
        try:
            irmao = Irmao.objects.select_related('user').get(pk=irmao_id)
            _sincronizar_grupos_lideranca(irmao)
        except Irmao.DoesNotExist:
            pass


# Signal: Mandato pre_save — captura estado anterior do mandato e do departamento
@receiver(pre_save, sender=Mandato)
def mandato_pre_save_lideranca(sender, instance, **kwargs):
    # Captura quem é actualmente lider/vice no departamento antes do .update()
    try:
        dept = Departamento.objects.get(pk=instance.departamento_id)
        instance._dept_lider_id = dept.lider_departamento_id
        instance._dept_vice_id = dept.vice_lider_departamento_id
    except Departamento.DoesNotExist:
        instance._dept_lider_id = None
        instance._dept_vice_id = None
    # Captura funcao anterior se for edição
    if instance.pk:
        try:
            old = Mandato.objects.get(pk=instance.pk)
            instance._old_irmao_id = old.irmao_id
        except Mandato.DoesNotExist:
            instance._old_irmao_id = None
    else:
        instance._old_irmao_id = None


# Signal: Mandato post_save — sincroniza grupos para todos os irmaos afectados
@receiver(post_save, sender=Mandato)
def mandato_post_save_lideranca(sender, instance, **kwargs):
    ids_afectados = set(filter(None, [
        instance.irmao_id,
        getattr(instance, '_old_irmao_id', None),
        getattr(instance, '_dept_lider_id', None),
        getattr(instance, '_dept_vice_id', None),
    ]))
    for irmao_id in ids_afectados:
        try:
            irmao = Irmao.objects.select_related('user').get(pk=irmao_id)
            _sincronizar_grupos_lideranca(irmao)
        except Irmao.DoesNotExist:
            pass


# ---------------------------------------------------------------------------
# Expansão de ocorrências de actividades recorrentes
# ---------------------------------------------------------------------------

_FREQ_MAP = None  # importado lazily para evitar import circular ao arrancar


def _get_freq_map():
    global _FREQ_MAP
    if _FREQ_MAP is None:
        from dateutil.rrule import WEEKLY, DAILY, MONTHLY
        _FREQ_MAP = {'WEEKLY': WEEKLY, 'DAILY': DAILY, 'MONTHLY': MONTHLY}
    return _FREQ_MAP


@receiver(post_save, sender=Actividade)
def expandir_ocorrencias_recorrentes(sender, instance, **kwargs):
    """
    Quando se grava uma actividade-pai recorrente com Event configurado,
    elimina ocorrências-filho existentes e recria-as com base na rrule.
    bulk_create não dispara post_save, pelo que não há recursão.
    """
    import datetime
    from dateutil.rrule import rrule, MO, TU, WE, TH, FR, SA, SU

    WEEKDAY_MAP = {0: MO, 1: TU, 2: WE, 3: TH, 4: FR, 5: SA, 6: SU}

    # Só processar actividades-pai recorrentes com Event atribuído
    if not instance.is_recorrente or not instance.event_id or instance.parent_event_id:
        return

    freq_map = _get_freq_map()
    event = instance.event
    freq_str = event.rule.frequency if event.rule_id else 'WEEKLY'
    freq = freq_map.get(freq_str, freq_map['WEEKLY'])

    hora_inicio = instance.inicio or datetime.time(0, 0)
    hora_fim = instance.fim or datetime.time(23, 59)
    dtstart = datetime.datetime.combine(instance.data, hora_inicio)
    # Sem data de fim: expandir 2 anos a partir da data de início
    if instance.recorrencia_fim:
        until = datetime.datetime.combine(instance.recorrencia_fim, hora_fim)
    else:
        until = dtstart + datetime.timedelta(days=730)

    rrule_kwargs = {'dtstart': dtstart, 'until': until}
    if freq == freq_map['WEEKLY'] and instance.dias_semana:
        dias = [int(d.strip()) for d in instance.dias_semana.split(',') if d.strip().isdigit()]
        byweekday = [WEEKDAY_MAP[d] for d in dias if d in WEEKDAY_MAP]
        if byweekday:
            rrule_kwargs['byweekday'] = byweekday

    dates = list(rrule(freq, **rrule_kwargs))

    # Eliminar ocorrências existentes
    Actividade.objects.filter(parent_event=instance).delete()

    # Criar novas ocorrências-filho
    dur = (datetime.datetime.combine(instance.data, hora_fim)
           - datetime.datetime.combine(instance.data, hora_inicio))
    children = []
    for dt in dates:
        fim_dt = dt + dur
        children.append(Actividade(
            designacao=instance.designacao,
            inicio=dt.time(),
            fim=fim_dt.time(),
            data=dt.date(),
            tema=instance.tema,
            localactividade=instance.localactividade,
            versosbiblicos=instance.versosbiblicos,
            hinos=instance.hinos,
            totalpresentes=0,
            observacao='',
            departamento=instance.departamento,
            criado_por=instance.criado_por,
            is_recorrente=False,
            parent_event=instance,
        ))
    if children:
        Actividade.objects.bulk_create(children)
