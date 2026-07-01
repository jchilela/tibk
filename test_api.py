#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from sitetibl.models import Actividade

print("=== Tipos de designacao ===")
actividades = Actividade.objects.all().values('designacao').distinct().order_by('designacao')
for i, a in enumerate(actividades):
    count = Actividade.objects.filter(designacao=a['designacao']).count()
    print(f"{i+1}. '{a['designacao']}' - {count} actividades")
