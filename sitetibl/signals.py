from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
import requests

from .models import EnvioMensagem, Irmao, PedidoSaida, Dizimooferta, Entradabanco, Entradacaixa

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

def tentar_vincular_dizimo_com_banco(dizimo):
    """
    Tenta vincular automaticamente um dízimo com uma entrada bancária.
    Critérios:
    - Mesma data
    - Mesmo valor
    - Mesma moeda
    - Ainda não vinculados
    """
    if dizimo.entradabanco:
        # Já vinculado, não faz nada
        return

    try:
        # Procura uma entrada bancária que corresponda
        entrada = Entradabanco.objects.filter(
            data=dizimo.datacorrespondente,
            valor=dizimo.valor,
            moeda=dizimo.moeda,
            # Entrada ainda não vinculada a outro dízimo
            dizimooferta__isnull=True
        ).first()

        if entrada:
            dizimo.entradabanco = entrada
            # Salva sem disparar signals novamente (para evitar loop infinito)
            Dizimooferta.objects.filter(pk=dizimo.pk).update(entradabanco=entrada)
            print(f"✅ Dízimo ID {dizimo.id} vinculado com Entrada Bancária ID {entrada.id}")
    except Exception as e:
        print(f"❌ Erro ao vincular dízimo ID {dizimo.id}: {str(e)}")


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
            entradabanco__isnull=True
        )

        for dizimo in dizimos:
            dizimo.entradabanco = entrada
            # Salva sem disparar signals
            Dizimooferta.objects.filter(pk=dizimo.pk).update(entradabanco=entrada)
            print(f"✅ Entrada Bancária ID {entrada.id} vinculada com Dízimo ID {dizimo.id}")
    except Exception as e:
        print(f"❌ Erro ao vincular entrada bancária ID {entrada.id}: {str(e)}")


@receiver(post_save, sender=Dizimooferta)
def auto_vincular_dizimo_com_banco(sender, instance, created, **kwargs):
    """
    Signal que dispara quando um dízimo é criado/atualizado.
    Tenta vincular automaticamente com uma entrada bancária.
    """
    if created:
        tentar_vincular_dizimo_com_banco(instance)


@receiver(post_save, sender=Entradabanco)
def auto_vincular_banco_com_dizimos(sender, instance, created, **kwargs):
    """
    Signal que dispara quando uma entrada bancária é criada/atualizada.
    Tenta vincular automaticamente com dízimos.
    """
    if created:
        tentar_vincular_banco_com_dizimos(instance)


# =========================================
# 🏪 AUTO-LINK DIZIMOS COM ENTRADAS CAIXA
# =========================================

def tentar_vincular_dizimo_com_caixa(dizimo):
    """
    Tenta vincular automaticamente um dízimo com uma entrada de caixa.
    Critérios:
    - Mesma data
    - Mesmo valor
    - Mesma moeda
    - Ainda não vinculados
    """
    if dizimo.entradacaixa:
        # Já vinculado, não faz nada
        return

    try:
        # Procura uma entrada de caixa que corresponda
        entrada = Entradacaixa.objects.filter(
            data=dizimo.datacorrespondente,
            valor=dizimo.valor,
            moeda=dizimo.moeda,
            # Entrada ainda não vinculada a outro dízimo
            dizimooferta__isnull=True
        ).first()

        if entrada:
            dizimo.entradacaixa = entrada
            # Salva sem disparar signals novamente (para evitar loop infinito)
            Dizimooferta.objects.filter(pk=dizimo.pk).update(entradacaixa=entrada)
            print(f"✅ Dízimo ID {dizimo.id} vinculado com Entrada Caixa ID {entrada.id}")
    except Exception as e:
        print(f"❌ Erro ao vincular dízimo ID {dizimo.id}: {str(e)}")


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
            entradacaixa__isnull=True
        )

        for dizimo in dizimos:
            dizimo.entradacaixa = entrada
            # Salva sem disparar signals
            Dizimooferta.objects.filter(pk=dizimo.pk).update(entradacaixa=entrada)
            print(f"✅ Entrada Caixa ID {entrada.id} vinculada com Dízimo ID {dizimo.id}")
    except Exception as e:
        print(f"❌ Erro ao vincular entrada caixa ID {entrada.id}: {str(e)}")


@receiver(post_save, sender=Dizimooferta)
def auto_vincular_dizimo_com_caixa(sender, instance, created, **kwargs):
    """
    Signal que dispara quando um dízimo é criado/atualizado.
    Tenta vincular automaticamente com uma entrada de caixa.
    """
    if created:
        tentar_vincular_dizimo_com_caixa(instance)


@receiver(post_save, sender=Entradacaixa)
def auto_vincular_caixa_com_dizimos(sender, instance, created, **kwargs):
    """
    Signal que dispara quando uma entrada de caixa é criada/atualizada.
    Tenta vincular automaticamente com dízimos.
    """
    if created:
        tentar_vincular_caixa_com_dizimos(instance)
