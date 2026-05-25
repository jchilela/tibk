#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from django.urls import get_resolver
from django.urls.exceptions import Resolver404

resolver = get_resolver()
urls_to_check = [
    'api_irmaos',
    'api_actividades',
    'api_funcoes',
    'protocolo_add_escalas',
]

print("Checking URL patterns...")
for url_name in urls_to_check:
    try:
        url = resolver.reverse(url_name)
        print(f'✓ {url_name}: {url}')
    except Resolver404:
        print(f'✗ {url_name}: NOT FOUND')
