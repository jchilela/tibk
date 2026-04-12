"""
Migração em 3 fases para converter provincia/municipio de CharField para FK.

Fase 1: Criar tabelas Provincia e Municipio
Fase 2: RunPython — popular províncias e mapear dados existentes
Fase 3: Alterar campos de CharField para FK
"""
from django.db import migrations, models
import django.db.models.deletion


# Dados antigos PROVINCIAS → novos objectos
PROVINCIAS_MAP = {
    'BNG': 'Bengo', 'BGL': 'Benguela', 'BIE': 'Bié', 'CAB': 'Cabinda',
    'CNE': 'Cunene', 'HMB': 'Huambo', 'HLA': 'Huíla',
    'KKG': 'Kuando Kubango', 'KZN': 'Cuanza Norte', 'KZS': 'Cuanza Sul',
    'LDA': 'Luanda', 'LDN': 'Lunda Norte', 'LDS': 'Lunda Sul',
    'MLG': 'Malange', 'MXC': 'Moxico', 'NMB': 'Namibe',
    'UGE': 'Uíge', 'ZAR': 'Zaire',
}

# Municípios antigos (MUNICIPIOO) → província Luanda
MUNICIPIOS_LDA = {
    'BE': 'Belas', 'CZ': 'Cazenga', 'KK': 'Kilamba Kiaxi',
    'LU': 'Luanda', 'CA': 'Cacuaco', 'IC': 'Ícolo e Bengo',
    'TT': 'Talatona', 'VI': 'Viana', 'QU': 'Quissama',
}


def seed_e_converter(apps, schema_editor):
    """Fase 2: popular províncias/municípios e converter dados existentes."""
    Provincia = apps.get_model('sitetibl', 'Provincia')
    Municipio = apps.get_model('sitetibl', 'Municipio')

    # Criar províncias
    prov_objs = {}
    for codigo, nome in PROVINCIAS_MAP.items():
        obj, _ = Provincia.objects.get_or_create(codigo=codigo, defaults={'nome': nome})
        prov_objs[codigo] = obj

    # Criar municípios de Luanda (os que existiam como choices MUNICIPIOO)
    mun_code_objs = {}   # código choice → Municipio obj
    mun_name_lower = {}  # nome.lower() → Municipio obj (para Sitio que usava texto)
    luanda = prov_objs.get('LDA')
    if luanda:
        for codigo, nome in MUNICIPIOS_LDA.items():
            obj, _ = Municipio.objects.get_or_create(
                nome=nome, provincia=luanda,
            )
            mun_code_objs[codigo] = obj
            mun_name_lower[nome.lower()] = obj

    # Converter Sitio: provincia (CharField código) + municipio (texto livre)
    Sitio = apps.get_model('sitetibl', 'Sitio')
    for sitio in Sitio.objects.all():
        changed = False
        old_prov = (sitio.provincia or '').strip()
        if old_prov and old_prov in prov_objs:
            sitio.provincia_nova = prov_objs[old_prov]
            changed = True
        # Sitio.municipio era CharField livre — match por nome
        old_mun = (sitio.municipio or '').strip()
        if old_mun:
            mun = mun_name_lower.get(old_mun.lower())
            if mun:
                sitio.municipio_novo = mun
                changed = True
        if changed:
            sitio.save()

    # Converter Pessoa: provincia (código) + municipio (código choice)
    Pessoa = apps.get_model('sitetibl', 'Pessoa')
    for pessoa in Pessoa.objects.all():
        changed = False
        old_prov = (pessoa.provincia or '').strip()
        if old_prov and old_prov in prov_objs:
            pessoa.provincia_nova = prov_objs[old_prov]
            changed = True
        old_mun = (pessoa.municipio or '').strip()
        if old_mun:
            # Tentar primeiro por código choice (MUNICIPIOO)
            mun = mun_code_objs.get(old_mun)
            if not mun:
                # Senão, tentar por nome (caso alguém tenha escrito o nome)
                mun = mun_name_lower.get(old_mun.lower())
            if mun:
                pessoa.municipio_novo = mun
                changed = True
        if changed:
            pessoa.save()


def noop(apps, schema_editor):
    """Reverso: nada a fazer (dados ficam nos campos antigos)."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sitetibl', '0078_profissao_fk_para_charfield'),
    ]

    operations = [
        # ── Fase 1: Criar tabelas ──
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('codigo', models.CharField(max_length=3, unique=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Província',
                'verbose_name_plural': 'Províncias',
            },
        ),
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('provincia', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='municipios',
                    to='sitetibl.provincia',
                )),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Município',
                'verbose_name_plural': 'Municípios',
                'unique_together': {('nome', 'provincia')},
            },
        ),

        # ── Adicionar campos FK temporários (para não colidir com os CharField) ──
        migrations.AddField(
            model_name='sitio',
            name='provincia_nova',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='sitetibl.provincia',
                verbose_name='Província',
                related_name='+',
            ),
        ),
        migrations.AddField(
            model_name='sitio',
            name='municipio_novo',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='sitetibl.municipio',
                verbose_name='Município',
                related_name='+',
            ),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='provincia_nova',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='sitetibl.provincia',
                verbose_name='Província',
                related_name='+',
            ),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='municipio_novo',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='sitetibl.municipio',
                verbose_name='Município',
                related_name='+',
            ),
        ),

        # ── Fase 2: Popular províncias e converter dados ──
        migrations.RunPython(seed_e_converter, noop),

        # ── Fase 3: Remover campos antigos, renomear novos ──
        migrations.RemoveField(model_name='sitio', name='provincia'),
        migrations.RemoveField(model_name='sitio', name='municipio'),
        migrations.RenameField(model_name='sitio', old_name='provincia_nova', new_name='provincia'),
        migrations.RenameField(model_name='sitio', old_name='municipio_novo', new_name='municipio'),

        migrations.RemoveField(model_name='pessoa', name='provincia'),
        migrations.RemoveField(model_name='pessoa', name='municipio'),
        migrations.RenameField(model_name='pessoa', old_name='provincia_nova', new_name='provincia'),
        migrations.RenameField(model_name='pessoa', old_name='municipio_novo', new_name='municipio'),
    ]
