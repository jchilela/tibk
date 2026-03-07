# sitetibl/management/commands/vincular_dizimos.py
"""
Management command para vincular automaticamente dízimos com entradas bancárias e de caixa.

Uso:
    python manage.py vincular_dizimos
    python manage.py vincular_dizimos --banco            # Apenas banco
    python manage.py vincular_dizimos --caixa            # Apenas caixa
    python manage.py vincular_dizimos --moeda AKZ
    python manage.py vincular_dizimos --dias-tolerancia 2
    python manage.py vincular_dizimos --force
    python manage.py vincular_dizimos --relatorio
    python manage.py vincular_dizimos --desvincular <dizimo_id>
"""

from django.core.management.base import BaseCommand, CommandError
from sitetibl.dizimo_utils import (
    vincular_dizimos_existentes,
    vincular_entradas_bancarias_existentes,
    vincular_dizimos_com_caixa,
    vincular_caixas_existentes,
    relatorio_vinculacao,
    relatorio_vinculacao_completa,
    desvincular_dizimo,
    desvincular_dizimo_caixa,
)


class Command(BaseCommand):
    help = 'Vincula automaticamente dízimos com entradas bancárias e de caixa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--banco',
            action='store_true',
            help='Processa apenas entradas bancárias',
        )
        parser.add_argument(
            '--caixa',
            action='store_true',
            help='Processa apenas entradas de caixa',
        )
        parser.add_argument(
            '--moeda',
            type=str,
            default=None,
            help='Moeda específica para vincular (ex: AKZ, USD)',
        )
        parser.add_argument(
            '--dias-tolerancia',
            type=int,
            default=0,
            help='Tolerância em dias para diferença de datas (padrão: 0)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-vincular registros já vinculados',
        )
        parser.add_argument(
            '--relatorio',
            action='store_true',
            help='Mostrar relatório de vinculação',
        )
        parser.add_argument(
            '--desvincular',
            type=int,
            default=None,
            help='Desvincular um dízimo específico (ID)',
        )
        parser.add_argument(
            '--desvincular-caixa',
            type=int,
            default=None,
            help='Desvincular um dízimo de caixa específico (ID)',
        )

    def handle(self, *args, **options):
        # Mostrar relatório
        if options['relatorio']:
            self.mostrar_relatorio()
            return

        # Desvincular
        if options['desvincular']:
            self.desvincular_dizimo_cmd(options['desvincular'])
            return
        
        if options['desvincular_caixa']:
            self.desvincular_dizimo_caixa_cmd(options['desvincular_caixa'])
            return

        # Vincular
        moeda = options['moeda']
        dias_tolerancia = options['dias_tolerancia']
        force = options['force']
        banco = options['banco']
        caixa = options['caixa']

        processou_algo = False

        # Se nenhum filtro especificado, processa tudo
        if not banco and not caixa:
            banco = True
            caixa = True

        # Vincular com BANCO
        if banco:
            self.stdout.write(
                self.style.HTTP_INFO('🏦 Processando entradas bancárias...')
            )
            
            # Vincular dízimos com banco
            stats = vincular_dizimos_existentes(
                dias_tolerancia=dias_tolerancia,
                moeda=moeda,
                force=force
            )
            self.mostrar_stats(stats, 'Dízimos → Banco')
            
            # Vincular banco com dízimos
            stats = vincular_entradas_bancarias_existentes(
                dias_tolerancia=dias_tolerancia,
                moeda=moeda,
                force=force
            )
            self.mostrar_stats(stats, 'Banco → Dízimos')
            
            processou_algo = True

        # Vincular com CAIXA
        if caixa:
            self.stdout.write(
                self.style.HTTP_INFO('🏪 Processando entradas de caixa...')
            )
            
            # Vincular dízimos com caixa
            stats = vincular_dizimos_com_caixa(
                dias_tolerancia=dias_tolerancia,
                moeda=moeda,
                force=force
            )
            self.mostrar_stats(stats, 'Dízimos → Caixa')
            
            # Vincular caixa com dízimos
            stats = vincular_caixas_existentes(
                dias_tolerancia=dias_tolerancia,
                moeda=moeda,
                force=force
            )
            self.mostrar_stats(stats, 'Caixa → Dízimos')
            
            processou_algo = True

        if processou_algo:
            self.stdout.write(self.style.SUCCESS('✅ Processo concluído!'))

    def mostrar_stats(self, stats, label=''):
        """Mostra as estatísticas de vinculação"""
        prefix = f"[{label}] " if label else ""
        self.stdout.write(
            f"  {prefix}Total processados: {stats['total_processados']}"
        )
        self.stdout.write(
            self.style.SUCCESS(f"  {prefix}✅ Sucesso: {stats['sucesso']}")
        )
        if stats['ja_vinculados'] > 0:
            self.stdout.write(
                f"  {prefix}⏭️  Já vinculados: {stats['ja_vinculados']}"
            )
        if stats['sem_correspondencia'] > 0:
            self.stdout.write(
                f"  {prefix}❌ Sem correspondência: {stats['sem_correspondencia']}"
            )
        if stats['erro'] > 0:
            self.stdout.write(
                self.style.ERROR(f"  {prefix}⚠️  Erros: {stats['erro']}")
            )

    def mostrar_relatorio(self):
        """Mostra o relatório completo de vinculação"""
        relatorio = relatorio_vinculacao_completa()

        self.stdout.write(self.style.HTTP_INFO('\n📊 RELATÓRIO COMPLETO DE VINCULAÇÃO\n'))
        
        # DÍZIMOS
        self.stdout.write(self.style.WARNING('📌 DÍZIMOS:'))
        self.stdout.write(f"  Total: {relatorio['dizimos_total']}")
        self.stdout.write(
            self.style.SUCCESS(
                f"  ✅ Vinculados (total): {relatorio['dizimos_vinculados_total']}"
            )
        )
        self.stdout.write(
            f"     └─ Com Banco: {relatorio['dizimos_vinculados_banco']}"
        )
        self.stdout.write(
            f"     └─ Com Caixa: {relatorio['dizimos_vinculados_caixa']}"
        )
        self.stdout.write(
            f"  Não vinculados: {relatorio['dizimos_nao_vinculados']}"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"  Taxa geral: {relatorio['taxa_vinculacao_dizimos']}"
            )
        )

        # BANCO
        self.stdout.write(self.style.WARNING('\n🏦 ENTRADAS BANCÁRIAS:'))
        self.stdout.write(f"  Total: {relatorio['entradas_banco_total']}")
        self.stdout.write(
            self.style.SUCCESS(
                f"  Com dízimo vinculado: {relatorio['entradas_banco_com_dizimo']}"
            )
        )
        self.stdout.write(
            f"  Sem dízimo: {relatorio['entradas_banco_sem_dizimo']}"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"  Taxa: {relatorio['taxa_banco']}"
            )
        )

        # CAIXA
        self.stdout.write(self.style.WARNING('\n🏪 ENTRADAS DE CAIXA:'))
        self.stdout.write(f"  Total: {relatorio['caixas_total']}")
        self.stdout.write(
            self.style.SUCCESS(
                f"  Com dízimo vinculado: {relatorio['caixas_com_dizimo']}"
            )
        )
        self.stdout.write(
            f"  Sem dízimo: {relatorio['caixas_sem_dizimo']}"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"  Taxa: {relatorio['taxa_caixa']}"
            )
        )

    def desvincular_dizimo_cmd(self, dizimo_id):
        """Desvincula um dízimo de banco"""
        if desvincular_dizimo(dizimo_id):
            self.stdout.write(
                self.style.SUCCESS(f'✅ Dízimo {dizimo_id} desvinculado do banco!')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao desvincular dízimo {dizimo_id}')
            )

    def desvincular_dizimo_caixa_cmd(self, dizimo_id):
        """Desvincula um dízimo de caixa"""
        if desvincular_dizimo_caixa(dizimo_id):
            self.stdout.write(
                self.style.SUCCESS(f'✅ Dízimo {dizimo_id} desvinculado da caixa!')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao desvincular dízimo {dizimo_id}')
            )
