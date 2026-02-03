# tibl/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')

app = Celery('tibl')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuração do agendamento
app.conf.beat_schedule = {
    'notificacoes_escala_cada_1_minuto': {
        'task': 'sitetibl.tasks.enviar_notificacoes_escala',
        'schedule': crontab(hour=4, minute=0),  # executa todos dias as 4h

        #'schedule': crontab(minute='*/1'),  # a cada 1 minuto
    },
}
