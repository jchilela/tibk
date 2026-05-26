from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitetibl', '0097_enviomensagem_remetente_departamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='enviomensagem',
            name='sms_enviado',
            field=models.BooleanField(default=False, verbose_name='SMS enviado com sucesso'),
        ),
        migrations.AddField(
            model_name='enviomensagem',
            name='email_enviado',
            field=models.BooleanField(default=False, verbose_name='Email enviado com sucesso'),
        ),
    ]
