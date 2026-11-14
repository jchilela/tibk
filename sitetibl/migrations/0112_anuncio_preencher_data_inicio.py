from django.db import migrations
from django.db.models import F


def preencher_data_inicio(apps, schema_editor):
    Anuncio = apps.get_model('sitetibl', 'Anuncio')
    Anuncio.objects.filter(data_inicio__isnull=True).update(data_inicio=F('data'))


class Migration(migrations.Migration):

    dependencies = [
        ('sitetibl', '0111_anuncio_boletim'),
    ]

    operations = [
        migrations.RunPython(preencher_data_inicio, migrations.RunPython.noop),
    ]
