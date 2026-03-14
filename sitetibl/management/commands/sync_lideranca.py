"""
Sincroniza os campos Departamento.lider_departamento e vice_lider_departamento
a partir dos Mandatos activos. O Mandato é a fonte única de verdade.
"""
from django.core.management.base import BaseCommand

from sitetibl.models import Departamento, Mandato


class Command(BaseCommand):
    help = 'Sincroniza lideranca dos departamentos com base nos mandatos'

    def handle(self, *args, **options):
        corrigidos = 0
        for dept in Departamento.objects.all():
            updates = {}

            lider_mandato = (
                Mandato.objects.filter(departamento=dept, funcao='lider')
                .select_related('irmao')
                .first()
            )
            vice_mandato = (
                Mandato.objects.filter(departamento=dept, funcao='vice_lider')
                .select_related('irmao')
                .first()
            )

            lider_esperado = lider_mandato.irmao if lider_mandato else None
            vice_esperado = vice_mandato.irmao if vice_mandato else None

            if dept.lider_departamento != lider_esperado:
                old = dept.lider_departamento
                updates['lider_departamento'] = lider_esperado
                self.stdout.write(
                    f'  [{dept.designacao}] lider: {old} -> {lider_esperado}'
                )

            if dept.vice_lider_departamento != vice_esperado:
                old = dept.vice_lider_departamento
                updates['vice_lider_departamento'] = vice_esperado
                self.stdout.write(
                    f'  [{dept.designacao}] vice: {old} -> {vice_esperado}'
                )

            if updates:
                Departamento.objects.filter(pk=dept.pk).update(**updates)
                corrigidos += 1

        if corrigidos:
            self.stdout.write(self.style.SUCCESS(
                f'{corrigidos} departamento(s) corrigido(s).'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                'Todos os departamentos estao sincronizados.'
            ))
