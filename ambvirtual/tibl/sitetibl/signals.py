from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
import requests

from .models import EnvioMensagem, Irmao, PedidoSaida

@receiver(post_save, sender=EnvioMensagem)
def enviar_email_sms_massivo(sender, instance, created, **kwargs):
    irmaos = Irmao.objects.exclude(email__isnull=True).exclude(email='')

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
    
    if instance.sms:
            for irmao in irmaos:
                # Enviar SMS 
                sms_url = 'https://telcosms.co.ao/send_message'
                sms_data = {
                    "message": {
                        "api_key_app": "prdc4b5a87b97d15edf8aa0cb5929",
                        "phone_number": "925868498",  # campo para passar o numero de telefone do User
                        "message_body": f"{instance.mensagem}.Antenciosamente a equipa TIBL."
                    }
                }
                
                try:
                    sms_response = requests.post(sms_url, json=sms_data)
                    if sms_response.status_code == 200:
                        print('Mensagem SMS enviada com sucesso!')
                    else:
                        print('Falha ao enviar a mensagem SMS. Código de status:', sms_response.status_code)
                        print('Resposta do servidor:', sms_response.text)
                except requests.exceptions.RequestException as e:
                    print('Ocorreu um erro ao tentar enviar a mensagem SMS:', e)


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
    # for telefone in telefones:
        
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

    
    #     print(
    #         f"SMS para {telefone}: "
    #         f"Novo pedido de saída de caixa ({instance.projecto}) "
    #         f"no valor de {instance.montante}."
    #     )