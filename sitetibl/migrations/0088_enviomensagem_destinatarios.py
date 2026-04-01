from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitetibl', '0087_ajuda_campo_texto'),
    ]

    operations = [
        migrations.AddField(
            model_name='enviomensagem',
            name='destinatarios',
            field=models.ManyToManyField(
                blank=True,
                related_name='mensagens_recebidas',
                to='sitetibl.irmao',
                verbose_name='Destinatários',
            ),
        ),
    ]
