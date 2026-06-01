from django.core.management.base import BaseCommand

from sitetibl.models import (
    Cargo,
    Centro_Custo,
    Funcao,
    Status_Aprovacao,
    Tipo_Celula,
    Tipo_Moeda,
    TipoOferta,
    Tipificacao_Custo,
)


class Command(BaseCommand):
    help = (
        'Popula dados do sistema (referenciais + cargos + funcoes de escala), '
        'sem mexer em irmaos/utilizadores.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-referenciais',
            action='store_true',
            help='Nao cria/atualiza tabelas referenciais do sistema.',
        )
        parser.add_argument(
            '--skip-cargos',
            action='store_true',
            help='Nao cria/atualiza cargos.',
        )
        parser.add_argument(
            '--skip-funcoes-escala',
            action='store_true',
            help='Nao cria/atualiza funcoes para escala.',
        )

    def handle(self, *args, **options):
        if not options['skip_referenciais']:
            self.seed_referenciais()

        if not options['skip_cargos']:
            self.seed_cargos()

        if not options['skip_funcoes_escala']:
            self.seed_funcoes_escala()

        self.stdout.write(self.style.SUCCESS('Seed de dados do sistema concluido.'))

    def seed_referenciais(self):
        moedas = [
            ('Kwanza', 'AKZ'),
            ('Dolar Americano', 'USD'),
            ('Euro', 'EUR'),
        ]
        status_aprovacao = ['Em analise', 'Aprovado', 'Rejeitado']
        tipo_celula = ['Celula Familiar', 'Celula de Jovens', 'Celula de Oracao']
        centro_custo = ['Administracao', 'Missoes', 'Acao Social']
        tipificacao_custo = ['Operacional', 'Investimento', 'Emergencial']
        tipo_oferta = ['Dizimo', 'Oferta', 'Oferta Especial']

        self._seed_designacao_abreviatura(Tipo_Moeda, moedas)
        self._seed_designacao(Status_Aprovacao, status_aprovacao)
        self._seed_designacao(Tipo_Celula, tipo_celula)
        self._seed_designacao(Centro_Custo, centro_custo)
        self._seed_designacao(Tipificacao_Custo, tipificacao_custo)
        self._seed_designacao(TipoOferta, tipo_oferta)

    def seed_cargos(self):
        cargos = [
            'Missionário',
            'Acção social',
            'Tesoureiro(a)',
            'Líder',
            'Estafeta',
            'Secretário(a)',
            'Motorista',
            'Zelador(a)',
            'Diácono(Diaconíza)',
            'Pastor acessor',
            'Pastor principal',
        ]

        created_count = 0
        for designacao in cargos:
            _, created = Cargo.objects.get_or_create(designacao=designacao)
            if created:
                created_count += 1

        self.stdout.write(
            f'Cargo: criados {created_count} | totais verificados {len(cargos)}'
        )

    def seed_funcoes_escala(self):
        funcoes = [
            'Diácono',
            'Recolha de dízimos e ofertas',
            'Ajudante',
            'Secretário(a)',
            'Visitante',
            'Noivo(a)',
            'Responsável',
            'Regente',
            'Dirigente',
            'Pregador(a)',
        ]

        created_count = 0
        for designacao in funcoes:
            _, created = Funcao.objects.get_or_create(
                designacao=designacao,
                defaults={'descricao': 'Função para escala de actividade.'},
            )
            if created:
                created_count += 1

        self.stdout.write(
            f'Funcao: criadas {created_count} | totais verificados {len(funcoes)}'
        )

    def _seed_designacao(self, model, designacoes):
        created_count = 0
        for designacao in designacoes:
            _, created = model.objects.get_or_create(designacao=designacao)
            if created:
                created_count += 1

        self.stdout.write(
            f'{model.__name__}: criados {created_count} | totais verificados {len(designacoes)}'
        )

    def _seed_designacao_abreviatura(self, model, pares):
        created_count = 0
        for designacao, abreviatura in pares:
            _, created = model.objects.get_or_create(
                designacao=designacao,
                defaults={'abreviatura': abreviatura},
            )
            if created:
                created_count += 1

        self.stdout.write(
            f'{model.__name__}: criados {created_count} | totais verificados {len(pares)}'
        )
