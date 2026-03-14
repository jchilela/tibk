"""
Seeder idempotente para criar o Calendário principal TIBL no django-scheduler.
Uso: python manage.py seed_calendar
"""
from django.core.management.base import BaseCommand
from schedule.models import Calendar


class Command(BaseCommand):
    help = 'Cria o calendário principal TIBL (idempotente).'

    def handle(self, *args, **options):
        calendar, created = Calendar.objects.get_or_create(
            slug='tibl',
            defaults={'name': 'TIBL'},
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Calendário TIBL criado.'))
        else:
            self.stdout.write('Calendário TIBL já existe (sem alterações).')
