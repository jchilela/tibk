import logging

from django.contrib.auth.models import Group, User
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
from django.utils.crypto import get_random_string
import requests

from .models import Departamento, EnvioMensagem, Irmao, Mandato, PedidoSaida, Dizimooferta, Entradabanco, Entradacaixa, Actividade

logger = logging.getLogger(__name__)


# =========================================
# 👤 AUTO-CRIAR USER AO CRIAR IRMÃO
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

    logger.info('User "%s" criado para Irmao ID %s', username, instance.pk)

    # Enviar credenciais: email se disponivel, senao SMS
    if instance.email:
        _enviar_credenciais_email(instance, username, temp_password)
    elif instance.telefone:
        _enviar_credenciais_sms(instance, username, temp_password)
    else:
        logger.warning(
            'Irmao ID %s sem email nem telefone — credenciais nao enviadas. '
            'Username: %s', instance.pk, username,
        )


def _enviar_credenciais_email(irmao, username, password):
    """Envia email de boas-vindas com credenciais de acesso."""
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
                 f'Utilizador: {username} | Palavra-passe temporária: {password}',
            from_email=None,  # usa DEFAULT_FROM_EMAIL do settings
            to=[irmao.email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        logger.info('Email de boas-vindas enviado para %s', irmao.email)
    except Exception as e:
        logger.error('Falha ao enviar email de boas-vindas para %s: %s', irmao.email, e)


def _enviar_credenciais_sms(irmao, username, password):
    """Envia SMS com credenciais de acesso via TelcoSMS."""
    sms_url = 'https://telcosms.co.ao/send_message'
    mensagem = (
        f'TIBL - Bem-vindo {irmao.nome}! '
        f'Utilizador: {username} | Senha: {password} '
        f'Altere a senha no primeiro acesso.'
    )
    sms_data = {
        'message': {
            'api_key_app': 'prdc4b5a87b97d15edf8aa0cb5929',
            'phone_number': irmao.telefone,
            'message_body': mensagem,
        }
    }
    try:
        response = requests.post(sms_url, json=sms_data, timeout=10)
        if response.status_code == 200:
            logger.info('SMS de boas-vindas enviado para %s', irmao.telefone)
        else:
            logger.error(
                'Falha ao enviar SMS para %s — status %s: %s',
                irmao.telefone, response.status_code, response.text,
            )
    except requests.exceptions.RequestException as e:
        logger.error('Erro ao enviar SMS para %s: %s', irmao.telefone, e)

@receiver(post_save, sender=EnvioMensagem)
def enviar_email_sms_massivo(sender, instance, created, **kwargs):
    irmaos = Irmao.objects.exclude(email__isnull=True).exclude(email='')
    irmaos_telefone = Irmao.objects.exclude(email__isnull=True).exclude(email='').exclude(telefone__isnull=True) #exclui irmaos que não têm numero de telefone


    if created and instance.email:

        

        if not irmaos.exists():
            return

        subject = 'Mensagem da TIBL'
        from_email = 'noreply@suaigreja.ao'

        connection = get_connection()  # 🔴 UMA conexão só
        connection.open()

        emails = []

        for irmao in irmaos:
            html_content = render_to_string(
                'emails/email_mensagem_massiva.html',
                {
                    'mensagem': instance.mensagem,
                    'autor': instance.quemenviou,
                    
                }
            )

            email = EmailMultiAlternatives(
                subject,
                instance.mensagem,
                from_email,
                [irmao.email],
                connection=connection
            )

            email.attach_alternative(html_content, "text/html")
            emails.append(email)
            print("email enviado para:", irmao.nome)
        

        connection.send_messages(emails)
        connection.close()
    
    irmaos_telefone_unico = list(set(irmaos_telefone)) # lista sem numero repetidos e sem numeros nulos
    # if instance.sms:
    #         for irmao in  irmaos_telefone_unico :
    #             # Enviar SMS 
    #             sms_url = 'https://telcosms.co.ao/send_message'
    #             sms_data = {
    #                 "message": {
    #                     "api_key_app": "prdc4b5a87b97d15edf8aa0cb5929",
    #                     "phone_number": irmao.telefone,  # campo para passar o numero de telefone do User
    #                     "message_body": f"{instance.mensagem}.Antenciosamente a equipa TIBL."
    #                 }
    #             }
                
    #             try:
    #                 sms_response = requests.post(sms_url, json=sms_data)
    #                 if sms_response.status_code == 200:
    #                     print('Mensagem SMS enviada com sucesso!')
    #                 else:
    #                     print('Falha ao enviar a mensagem SMS. Código de status:', sms_response.status_code)
    #                     print('Resposta do servidor:', sms_response.text)
    #             except requests.exceptions.RequestException as e:
    #                 print('Ocorreu um erro ao tentar enviar a mensagem SMS:', e)


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

    if not emails_destino:
        return

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


# =========================================
# 📬 NOTIFICAÇÃO DE CRIAÇÃO — PEDIDOS DE SAÍDA (FINANCEIRO + LÍDERES)
# =========================================

@receiver(post_save, sender=PedidoSaida)
def notificar_lideres_departamento(sender, instance, created, **kwargs):
    if not created:
        return

    departamento = instance.departamento

    emails_destino = []
    telefones = []

    subject = 'Pedido de Saída de Caixa - TIBL'
    from_email = 'noreply@suaigreja.ao'

    # Líder e Vice-líder do departamento
    if departamento:
        if departamento.lider_departamento:
            lider = departamento.lider_departamento
            if lider.email:
                emails_destino.append(lider.email)
            if getattr(lider, 'telefone', None):
                telefones.append(lider.telefone)

        if departamento.vice_lider_departamento:
            vice = departamento.vice_lider_departamento
            if vice.email:
                emails_destino.append(vice.email)
            if getattr(vice, 'telefone', None):
                telefones.append(vice.telefone)

    # Membros do grupo Financeiro
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
        pass

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
    # telefones_unicos = list(set(telefones)) #eliminar numeros repetidos
    # for telefone in telefones_unicos:
        
    #     # Enviar SMS 
    #     sms_url = 'https://telcosms.co.ao/send_message'
    #     sms_data = {
    #         "message": {
    #             "api_key_app": "prdc4b5a87b97d15edf8aa0cb5929",
    #             "phone_number": telefone,  # campo para passar o numero de telefone do User
    #             "message_body": f"Novo pedido de saida de caixa, Montante:{instance.montante}, Requerente:{instance.requerente}.Antenciosamente a equipa TIBL."
    #         }
    #     }
        
    #     try:
    #         sms_response = requests.post(sms_url, json=sms_data)
    #         if sms_response.status_code == 200:
    #             print('Mensagem SMS enviada com sucesso!')
    #         else:
    #             print('Falha ao enviar a mensagem SMS. Código de status:', sms_response.status_code)
    #             print('Resposta do servidor:', sms_response.text)
    #     except requests.exceptions.RequestException as e:
    #         print('Ocorreu um erro ao tentar enviar a mensagem SMS:', e)

    
    #     print(telefones_unicos)


# =========================================
# 🔗 AUTO-LINK DIZIMOS COM ENTRADAS BANCARIAS
# =========================================
# Sentido: Entradabanco salva → vincula automaticamente Dizimooferta correspondente

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
            entradabanco__isnull=True,
            entradacaixa__isnull=True
        )

        for dizimo in dizimos:
            Dizimooferta.objects.filter(pk=dizimo.pk).update(entradabanco=entrada)
            logger.info('Entrada Bancaria ID %s vinculada com Dizimo ID %s', entrada.id, dizimo.id)
    except Exception as e:
        logger.error('Erro ao vincular entrada bancaria ID %s: %s', entrada.id, e)


@receiver(post_save, sender=Entradabanco)
def auto_vincular_banco_com_dizimos(sender, instance, created, **kwargs):
    """
    Signal que dispara quando uma entrada bancária é criada ou atualizada.
    Procura dízimos/ofertas com mesma data, valor e moeda e vincula automaticamente.
    """
    tentar_vincular_banco_com_dizimos(instance)


# =========================================
# 🏪 AUTO-LINK DIZIMOS COM ENTRADAS CAIXA
# =========================================
# Sentido: Entradacaixa salva → vincula automaticamente Dizimooferta correspondente

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
            entradacaixa__isnull=True,
            entradabanco__isnull=True
        )

        for dizimo in dizimos:
            Dizimooferta.objects.filter(pk=dizimo.pk).update(entradacaixa=entrada)
            logger.info('Entrada Caixa ID %s vinculada com Dizimo ID %s', entrada.id, dizimo.id)
    except Exception as e:
        logger.error('Erro ao vincular entrada caixa ID %s: %s', entrada.id, e)


@receiver(post_save, sender=Entradacaixa)
def auto_vincular_caixa_com_dizimos(sender, instance, created, **kwargs):
    """
    Signal que dispara quando uma entrada de caixa é criada ou atualizada.
    Procura dízimos/ofertas com mesma data, valor e moeda e vincula automaticamente.
    """
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


def _sincronizar_grupos_lideranca(irmao):
    """
    Garante que os grupos 'Líder de Departamento' e 'Vice-Líder de Departamento'
    reflectem o estado actual das FKs em Departamento para este irmão.
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
    except Group.DoesNotExist:
        logger.warning('Grupos de liderança não encontrados — execute seed_config_essencial')
        return

    e_lider = Departamento.objects.filter(lider_departamento=irmao).exists()
    e_vice = Departamento.objects.filter(vice_lider_departamento=irmao).exists()

    if e_lider:
        user.groups.add(grupo_lider)
    else:
        user.groups.remove(grupo_lider)

    if e_vice:
        user.groups.add(grupo_vice)
    else:
        user.groups.remove(grupo_vice)


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
    if not instance.recorrencia_fim:
        return

    freq_map = _get_freq_map()
    event = instance.event
    freq_str = event.rule.frequency if event.rule_id else 'WEEKLY'
    freq = freq_map.get(freq_str, freq_map['WEEKLY'])

    hora_inicio = instance.inicio or datetime.time(0, 0)
    hora_fim = instance.fim or datetime.time(23, 59)
    dtstart = datetime.datetime.combine(instance.data, hora_inicio)
    until = datetime.datetime.combine(instance.recorrencia_fim, hora_fim)

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
