from datetime import date, time, timedelta

from django.core.management.base import BaseCommand

from sitetibl.models import Actividade, Funcao, Listaactividades, Sitio


class Command(BaseCommand):
    help = 'Cria uma actividade de teste para validar o fluxo de escalas e protocolo.'

    def handle(self, *args, **options):
        # Listaactividades ─────────────────────────────────────────────────────
        lista, created = Listaactividades.objects.get_or_create(
            designacao='Culto Dominical (TESTE)',
            defaults={'descricao': 'Actividade criada automaticamente para testes.'},
        )
        if created:
            self.stdout.write(f'  Listaactividades criada: {lista}')
        else:
            self.stdout.write(f'  Listaactividades já existe: {lista}')

        # Sitio ────────────────────────────────────────────────────────────────
        sitio, created = Sitio.objects.get_or_create(
            designacao='Sede (TESTE)',
            defaults={
                'tipo': '1',
                'descricao': 'Local criado automaticamente para testes.',
            },
        )
        if created:
            self.stdout.write(f'  Sítio criado: {sitio}')
        else:
            self.stdout.write(f'  Sítio já existe: {sitio}')

        # Funcoes de escala ────────────────────────────────────────────────────
        funcoes_nomes = ['Diácono', 'Recepção', 'Som', 'Multimédia']
        funcoes = []
        for nome in funcoes_nomes:
            f, created = Funcao.objects.get_or_create(designacao=nome)
            funcoes.append(f)
            if created:
                self.stdout.write(f'  Função criada: {nome}')

        # Actividade ───────────────────────────────────────────────────────────
        data_teste = date.today() + timedelta(days=7)

        actividade, created = Actividade.objects.get_or_create(
            designacao=lista,
            data=data_teste,
            defaults={
                'inicio': time(9, 0),
                'fim': time(12, 0),
                'tema': 'Tema de teste — fé e perseverança',
                'localactividade': sitio,
                'versosbiblicos': 'Filipenses 4:13',
                'hinos': 'Selecção de louvor',
                'totalpresentes': 0,
                'observacao': 'Actividade criada pelo seed de testes.',
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'\nActividade de teste criada com sucesso!'
                f'\n  ID : {actividade.id}'
                f'\n  Nome: {actividade.designacao}'
                f'\n  Data: {actividade.data}'
                f'\n  URL Detalhe : /tibl/actividades/detalhe/{actividade.id}/'
                f'\n  URL Escala  : /tibl/escalas/criar/'
                f'\n  URL Acta    : /tibl/actividade/{actividade.id}/acta/'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'\nActividade já existia (ID={actividade.id}, data={actividade.data}). '
                f'Nada foi alterado.'
            ))
