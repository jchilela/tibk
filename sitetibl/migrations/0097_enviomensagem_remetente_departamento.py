from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sitetibl', '0096_add_secretario_geral_funcao'),
    ]

    operations = [
        # Limpar valores existentes que apontavam para Irmao (IDs inválidos para Departamento)
        migrations.RunSQL(
            sql='UPDATE sitetibl_enviomensagem SET quemenviou_id = NULL;',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='enviomensagem',
            name='quemenviou',
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='sitetibl.departamento',
                verbose_name='Departamento remetente',
            ),
        ),
    ]
