# sitetibl/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta
from .models import Actividade, Escala
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests



@shared_task
def enviar_notificacoes_escala():
    hoje = date.today()

    # 2 dias antes e 1 dia antes
    dias_antes = [2, 1]

    for dias in dias_antes:
        data_alvo = hoje + timedelta(days=dias)

        actividades = Actividade.objects.filter(data=data_alvo)

        for actividade in actividades:
            escalas = Escala.objects.select_related(
                'irmao', 'funcao'
            ).filter(actividade=actividade)

            for escala in escalas:
                irmao = escala.irmao

                if irmao.email:
                    context = {
                        'nome': irmao.nome,
                        'apelido':irmao.apelido,
                        'actividade': actividade.designacao,
                        'data': actividade.data.strftime('%d/%m/%Y'),
                        'hora': actividade.inicio,
                        'funcao': escala.funcao,
                    }
                    
                    # Renderiza o HTML com os dados
                    html_content = render_to_string('emails/lembrete_escala.html', context)
                    # Cria uma versão em texto simples para clientes de email antigos
                    text_content = strip_tags(html_content)

                    send_mail(
                        subject='Lembrete de Escala - TIBL',
                        message=text_content,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[irmao.email],
                        html_message=html_content, # Este campo ativa o HTML
                        fail_silently=False,
                    )

                #Enviar SMS 
                sms_url = 'https://telcosms.co.ao/send_message'
                sms_data = {
                    "message": {
                        "api_key_app": "prd2c1f3fe6d2a990daec5f7bae85",
                        "phone_number": irmao.telefone,  # campo para passar o numero de telefone do User
                        "message_body": f"{irmao.nome} {irmao.apelido}, Este e um lembrete de que você está escalado para uma actividade {actividade.designacao}, no dia {actividade.data}, na hora {actividade.inicio}, com a função {escala.funcao}."
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