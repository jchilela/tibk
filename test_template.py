#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from django.template.loader import get_template

try:
    t = get_template('protocolo.html')
    print('✓ Template protocolo.html loaded successfully')
    print(f'✓ Template has {len(t.template.nodelist)} top-level nodes')
except Exception as e:
    print(f'✗ Error loading template: {e}')
