# sitetibl/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta
from .models import Actividade, Escala
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .sms import enviar_sms



def _lembrete_email_sms(irmao, actividade, escala_funcao):
    """Envia email e SMS de lembrete de escala a um irmão."""
    if irmao.email:
        context = {
            'nome': irmao.nome,
            'apelido': irmao.apelido,
            'actividade': actividade.designacao,
            'data': actividade.data.strftime('%d/%m/%Y'),
            'hora': actividade.inicio,
            'funcao': escala_funcao,
        }
        html_content = render_to_string('emails/lembrete_escala.html', context)
        text_content = strip_tags(html_content)
        send_mail(
            subject='Lembrete de Escala - TIBL',
            message=text_content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[irmao.email],
            html_message=html_content,
            fail_silently=False,
        )

    if irmao.telefone:
        sms_url = 'https://telcosms.co.ao/send_message'
        sms_data = {
            'message': {
                'api_key_app': settings.TELCOSMS_API_KEY,
                'phone_number': irmao.telefone,
                'message_body': (
                    f'{irmao.nome} {irmao.apelido}, lembrete: está escalado(a) para '
                    f'"{actividade.designacao}" no dia {actividade.data.strftime("%d/%m/%Y")} '
                    f'às {actividade.inicio.strftime("%H:%M")}. Deus abençoe!'
                ),
            }
        }
        try:
            sms_response = requests.post(sms_url, json=sms_data, timeout=10)
            if sms_response.status_code == 200:
                print('SMS lembrete enviado para', irmao.telefone)
            else:
                print('Falha SMS lembrete para', irmao.telefone, '— status', sms_response.status_code)
        except requests.exceptions.RequestException as e:
            print('Erro SMS lembrete para', irmao.telefone, ':', e)


@shared_task
def enviar_notificacoes_escala():
    hoje = date.today()

    # Lembretes enviados 2 dias (48h) e 1 dia antes para escalas normais
    # Lembretes de protocolo apenas 48h antes (2 dias)
    dias_antes = [2, 1]

    for dias in dias_antes:
        data_alvo = hoje + timedelta(days=dias)

        actividades = Actividade.objects.filter(data=data_alvo)

        for actividade in actividades:
            escalas = Escala.objects.select_related(
                'irmao', 'funcao'
            ).prefetch_related('irmao_protocolo').filter(actividade=actividade)

            for escala in escalas:
                if escala.eh_protocolo:
                    # Lembrete de protocolo: apenas 48 horas antes (dias == 2)
                    if dias == 2:
                        funcao_str = str(escala.funcao) if escala.funcao else 'Protocolo'
                        for membro in escala.irmao_protocolo.all():
                            _lembrete_email_sms(membro, actividade, funcao_str)
                else:
                    irmao = escala.irmao
                    if irmao:
                        _lembrete_email_sms(irmao, actividade, escala.funcao)

