from django.db import migrations, models


def migrar_categoria_a_partir_batizado(apps, schema_editor):
    Irmao = apps.get_model('sitetibl', 'Irmao')
    Irmao.objects.filter(batizado=True).update(categoria='membro_batizado')
    Irmao.objects.filter(batizado=False).update(categoria='assistente')


class Migration(migrations.Migration):

    dependencies = [
        ('sitetibl', '0098_enviomensagem_status_envio'),
    ]

    operations = [
        migrations.AddField(
            model_name='irmao',
            name='categoria',
            field=models.CharField(
                choices=[
                    ('membro_batizado', 'Membro (Batizado)'),
                    ('crianca', 'Criança'),
                    ('assistente', 'Assistente (Não batizado)'),
                ],
                default='assistente',
                max_length=20,
                verbose_name='Categoria',
            ),
        ),
        migrations.RunPython(migrar_categoria_a_partir_batizado, migrations.RunPython.noop),
    ]
