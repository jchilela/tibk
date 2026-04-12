"""
Seeder idempotente — Actividades recorrentes semanais da TIBL.

Uso:
    python manage.py seed_actividades_recorrentes
    python manage.py seed_actividades_recorrentes --dry-run   # apenas lista o que seria criado
"""
import datetime

from django.core.management.base import BaseCommand

from sitetibl.models import Actividade, Listaactividades


# ---------------------------------------------------------------------------
# Definição das actividades recorrentes
# Chave: nome da Listaactividades
# Valor: lista de dicts com campos da Actividade-pai
#   dia_semana: 0=Segunda … 6=Domingo (conforme Actividade.DIAS_SEMANA_NOMES)
#   inicio / fim: strings "HH:MM"
# ---------------------------------------------------------------------------
ACTIVIDADES = [
    {
        'designacao': 'Culto da União Masculina',
        'dia_semana': '0',  # Segunda
        'inicio': '18:00',
        'fim': '19:30',
    },
    {
        'designacao': 'Culto das Moças',
        'dia_semana': '1',  # Terça
        'inicio': '18:00',
        'fim': '19:30',
    },
    {
        'designacao': 'Culto de Sociedade de Senhoras',
        'dia_semana': '2',  # Quarta
        'inicio': '06:00',
        'fim': '07:30',
    },
    {
        'designacao': 'Culto de Oração',
        'dia_semana': '2',  # Quarta
        'inicio': '18:00',
        'fim': '19:30',
    },
    {
        'designacao': 'Culto do GAm',
        'dia_semana': '3',  # Quinta
        'inicio': '18:00',
        'fim': '19:30',
    },
    {
        'designacao': 'Culto de Estudo Bíblico',
        'dia_semana': '4',  # Sexta
        'inicio': '18:00',
        'fim': '19:30',
    },
    {
        'designacao': 'Ensaio dos Grupos Corais',
        'dia_semana': '5',  # Sábado
        'inicio': '09:00',
        'fim': '11:00',
    },
    {
        'designacao': 'Ensaio do Ministério de Louvor e Adoração',
        'dia_semana': '5',  # Sábado
        'inicio': '09:00',
        'fim': '11:00',
    },
]

# Data de referência para a actividade-pai (próxima Segunda a contar de hoje)
# O seeder usa a data do dia da semana mais próxima para cada actividade.
def _proxima_data(dia_semana: int) -> datetime.date:
    """Devolve a data da próxima ocorrência do dia da semana a partir de hoje (inclusive)."""
    hoje = datetime.date.today()
    dias_ate = (dia_semana - hoje.weekday()) % 7
    return hoje + datetime.timedelta(days=dias_ate)


class Command(BaseCommand):
    help = 'Cria actividades recorrentes semanais (idempotente).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria criado sem persistir.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        criadas = 0
        existentes = 0

        for item in ACTIVIDADES:
            # 1. Garantir que a Listaactividades existe
            lista_act, la_created = Listaactividades.objects.get_or_create(
                designacao=item['designacao'],
            )
            if la_created and not dry_run:
                self.stdout.write(f'  [+] Listaactividades criada: "{item["designacao"]}"')

            dia_int = int(item['dia_semana'])
            data_ref = _proxima_data(dia_int)
            inicio = datetime.time.fromisoformat(item['inicio'])
            fim = datetime.time.fromisoformat(item['fim'])
            dia_str = item['dia_semana']

            # 2. Verificar se já existe uma actividade-pai recorrente com esta designação e dia
            existe = Actividade.objects.filter(
                designacao=lista_act,
                is_recorrente=True,
                parent_event__isnull=True,
                dias_semana=dia_str,
            ).exists()

            if existe:
                existentes += 1
                self.stdout.write(
                    f'  [=] Já existe: "{item["designacao"]}" ({dia_str})'
                )
                continue

            if dry_run:
                self.stdout.write(
                    f'  [DRY] Criaria: "{item["designacao"]}" '
                    f'dia={dia_str} {item["inicio"]}-{item["fim"]}'
                )
                criadas += 1
                continue

            Actividade.objects.create(
                designacao=lista_act,
                data=data_ref,
                inicio=inicio,
                fim=fim,
                is_recorrente=True,
                dias_semana=dia_str,
                totalpresentes=0,
            )
            criadas += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'  [+] Criada: "{item["designacao"]}" '
                    f'({Actividade.DIAS_SEMANA_NOMES[dia_str]}, {item["inicio"]}-{item["fim"]})'
                )
            )

        prefixo = '[DRY-RUN] ' if dry_run else ''
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{prefixo}Concluído — {criadas} criada(s), {existentes} já existia(m).'
            )
        )
