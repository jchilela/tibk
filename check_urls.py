#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from django.urls import get_resolver

resolver = get_resolver()

# Find patterns with 'api' or 'protocolo'
print("URL patterns matching 'api' or 'protocolo':")
for pattern in resolver.url_patterns:
    pattern_str = str(pattern)
    if 'api' in pattern_str or 'protocolo' in pattern_str:
        print(f'  {pattern_str}')
