import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
import requests

from .models import EnvioMensagem, Irmao, PedidoSaida, Dizimooferta, Entradabanco, Entradacaixa

logger = logging.getLogger(__name__)

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


@receiver(post_save, sender=PedidoSaida)
def notificar_lideres_departamento(sender, instance, created, **kwargs):
    if not created:
        return

    departamento = instance.departamento
    if not departamento:
        return

    emails_destino = []
    telefones = []

    subject = 'Pedido de Saída de Caixa - TIBL'
    from_email = 'noreply@suaigreja.ao'

    # Líder
    if departamento.lider_departamento:
        lider = departamento.lider_departamento
        if lider.email:
            emails_destino.append(lider.email)
        if getattr(lider, 'telefone', None):
            telefones.append(lider.telefone)

    # Vice-líder
    if departamento.vice_lider_departamento:
        vice = departamento.vice_lider_departamento
        if vice.email:
            emails_destino.append(vice.email)
        if getattr(vice, 'telefone', None):
            telefones.append(vice.telefone)

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
