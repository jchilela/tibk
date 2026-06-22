"""
Alinha a categoria dos irmãos com a idade (idempotente).

Regras:
- Idade < 18 e categoria != 'crianca'  -> passa a 'crianca'.
- Categoria == 'crianca' e idade >= 18 -> passa a 'assistente' (revisão manual recomendada).

Uso:
    python manage.py reclassificar_criancas
    python manage.py reclassificar_criancas --dry-run
"""
from django.core.management.base import BaseCommand

from sitetibl.models import Irmao


class Command(BaseCommand):
    help = 'Alinha a categoria dos irmãos com a idade (0-17 = Criança). Idempotente.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas lista o que seria alterado, sem gravar.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        promovidos_a_crianca = []
        despromovidos_de_crianca = []

        for irmao in Irmao.objects.filter(datanascimento__isnull=False):
            idade = irmao.idade
            if idade is None:
                continue

            if idade < 18 and irmao.categoria != 'crianca':
                promovidos_a_crianca.append((irmao, idade))
                if not dry_run:
                    irmao.categoria = 'crianca'
                    irmao.save(update_fields=['categoria', 'batizado', 'data_atualizacao'])

            elif idade >= 18 and irmao.categoria == 'crianca':
                despromovidos_de_crianca.append((irmao, idade))
                if not dry_run:
                    irmao.categoria = 'assistente'
                    irmao.save(update_fields=['categoria', 'batizado', 'data_atualizacao'])

        prefixo = '[DRY-RUN] ' if dry_run else ''

        self.stdout.write(self.style.MIGRATE_HEADING(
            f'{prefixo}Menores classificados como Criança: {len(promovidos_a_crianca)}'
        ))
        for irmao, idade in promovidos_a_crianca:
            self.stdout.write(f'  + {irmao} (idade {idade})')

        self.stdout.write(self.style.MIGRATE_HEADING(
            f'{prefixo}Maiores de idade removidos de Criança -> Assistente '
            f'(rever manualmente): {len(despromovidos_de_crianca)}'
        ))
        for irmao, idade in despromovidos_de_crianca:
            self.stdout.write(f'  - {irmao} (idade {idade})')

        total = len(promovidos_a_crianca) + len(despromovidos_de_crianca)
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nada a reclassificar — categorias já alinhadas com a idade.'))
        elif dry_run:
            self.stdout.write(self.style.WARNING(
                f'{total} registo(s) seriam alterados. Execute sem --dry-run para aplicar.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f'{total} registo(s) reclassificados com sucesso.'))
