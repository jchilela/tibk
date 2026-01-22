from datetime import date, timedelta
from django.core.mail import send_mail
from .models import Actividade, Escala
from django.conf import settings




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

                mensagem = (
                    f"Olá {irmao.nome},\n\n"
                    f"Lembrete: você está escalado para a actividade "
                    f"'{actividade.designacao}' no dia {actividade.data} "
                    f"às {actividade.inicio}.\n"
                    f"Função: {escala.funcao}\n\n"
                    "Deus abençoe."
                )

                # 📧 EMAIL
                if irmao.email:
                    send_mail(
                        subject='Lembrete de Escala',
                        message=mensagem,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[irmao.email],
                        fail_silently=False,
                    )

                # 📱 SMS (exemplo)
                # if irmao.telefone:
                #     send_sms(irmao.telefone, mensagem)
