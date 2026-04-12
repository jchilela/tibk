"""
Migração manual: substitui cargo (FK→Cargo) por funcao (CharField choices) no Mandato.

Fases:
  1. Adicionar campo funcao com default 'membro'
  2. RunPython: copiar designação do cargo antigo → valor de funcao
  3. Remover FK cargo
  4. Actualizar unique_together
"""

from django.db import migrations, models


CARGO_MAP = {
    'lider': 'lider',
    'líder': 'lider',
    'vice-lider': 'vice_lider',
    'vice-líder': 'vice_lider',
    'vice lider': 'vice_lider',
    'vice líder': 'vice_lider',
    'secretario': 'secretario',
    'secretária': 'secretario',
    'secretário': 'secretario',
    'secretario(a)': 'secretario',
    'secretária(o)': 'secretario',
    'tesoureiro': 'tesoureiro',
    'tesoureira': 'tesoureiro',
    'tesoureiro(a)': 'tesoureiro',
    'coordenador': 'coordenador',
    'coordenadora': 'coordenador',
    'coordenador(a)': 'coordenador',
    'membro': 'membro',
}


def forwards(apps, schema_editor):
    Mandato = apps.get_model('sitetibl', 'Mandato')
    for m in Mandato.objects.select_related('cargo').all():
        designacao = m.cargo.designacao.strip().lower() if m.cargo else ''
        m.funcao = CARGO_MAP.get(designacao, 'membro')
        m.save(update_fields=['funcao'])


def backwards(apps, schema_editor):
    Cargo = apps.get_model('sitetibl', 'Cargo')
    Mandato = apps.get_model('sitetibl', 'Mandato')

    REVERSE_MAP = {
        'membro': 'Membro',
        'lider': 'Lider',
        'vice_lider': 'Vice-Lider',
        'secretario': 'Secretario',
        'tesoureiro': 'Tesoureiro',
        'coordenador': 'Coordenador',
    }
    cache = {}
    for m in Mandato.objects.all():
        nome = REVERSE_MAP.get(m.funcao, 'Membro')
        if nome not in cache:
            obj, _ = Cargo.objects.get_or_create(designacao=nome)
            cache[nome] = obj
        m.cargo = cache[nome]
        m.save(update_fields=['cargo'])


class Migration(migrations.Migration):

    dependencies = [
        ('sitetibl', '0080_ajuste_fk_final'),
    ]

    operations = [
        # 1. Adicionar funcao (CharField) com default
        migrations.AddField(
            model_name='mandato',
            name='funcao',
            field=models.CharField(
                'Função',
                max_length=20,
                choices=[
                    ('membro', 'Membro'),
                    ('lider', 'Líder'),
                    ('vice_lider', 'Vice-Líder'),
                    ('secretario', 'Secretário(a)'),
                    ('tesoureiro', 'Tesoureiro(a)'),
                    ('coordenador', 'Coordenador(a)'),
                ],
                default='membro',
            ),
        ),

        # 2. Copiar dados do cargo antigo
        migrations.RunPython(forwards, backwards),

        # 3. Remover unique_together antigo (que inclui cargo)
        migrations.AlterUniqueTogether(
            name='mandato',
            unique_together=set(),
        ),

        # 4. Remover FK cargo
        migrations.RemoveField(
            model_name='mandato',
            name='cargo',
        ),

        # 5. Definir novo unique_together
        migrations.AlterUniqueTogether(
            name='mandato',
            unique_together={('irmao', 'departamento')},
        ),
    ]
