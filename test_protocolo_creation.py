#!/usr/bin/env python
"""Test script to diagnose Protocolo creation issues"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from sitetibl.models import Protocolo, Irmao
from sitetibl.forms import ProtocoloForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

print("=" * 80)
print("TESTING PROTOCOLO CREATION")
print("=" * 80)

# Test 1: Check if Protocolo model has required fields
print("\n[TEST 1] Checking Protocolo model fields...")
from django.db import models
protocolo_fields = Protocolo._meta.get_fields()
print(f"Total fields: {len(protocolo_fields)}")

required_fields = {}
for field in protocolo_fields:
    if isinstance(field, models.Field) and not field.null and field.blank == False and field.default == models.NOT_PROVIDED:
        required_fields[field.name] = field
        print(f"  REQUIRED: {field.name} ({field.__class__.__name__}) - no default, not nullable")

print(f"\nTotal required fields with no defaults: {len(required_fields)}")

# Test 2: Check ProtocoloForm fields
print("\n[TEST 2] Checking ProtocoloForm fields...")
form = ProtocoloForm()
print(f"Form fields: {list(form.fields.keys())}")
print(f"Form Meta fields: {list(form._meta.fields)}")

# Test 3: Try to create a Protocolo without setting tipo and assunto
print("\n[TEST 3] Creating Protocolo object without tipo and assunto...")
try:
    proto = Protocolo.objects.create(
        numero='TEST-001',
        descricao='Test description'
    )
    print(f"  SUCCESS: Created {proto.id}")
    proto.delete()
except ValidationError as e:
    print(f"  VALIDATION ERROR: {e}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

# Test 4: Try to create a Protocolo with all required fields
print("\n[TEST 4] Creating Protocolo object WITH tipo and assunto...")
try:
    proto = Protocolo.objects.create(
        numero='TEST-002',
        tipo='interno',
        assunto='Test Subject',
        descricao='Test description'
    )
    print(f"  SUCCESS: Created {proto.id}")
    proto.delete()
except ValidationError as e:
    print(f"  VALIDATION ERROR: {e}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

# Test 5: Test ModelForm submission flow
print("\n[TEST 5] Testing ModelForm submission flow...")
form_data = {
    'numero': 'TEST-003',
    'descricao': 'Test',
    'responsavel': '',
    'prioridade': 'normal'
}
form = ProtocoloForm(data=form_data)
if form.is_valid():
    print(f"  Form is VALID")
    print(f"  Cleaned data: {form.cleaned_data}")
    try:
        obj = form.save(commit=False)
        print(f"  Created unsaved object: {obj}")
        print(f"  Object tipo: {obj.tipo if hasattr(obj, 'tipo') else 'NOT SET'}")
        print(f"  Object assunto: {obj.assunto if hasattr(obj, 'assunto') else 'NOT SET'}")
        
        # Simulate view's manual setting
        obj.tipo = 'interno'
        obj.assunto = 'Protocolo'
        print(f"  After manual setting:")
        print(f"    tipo: {obj.tipo}")
        print(f"    assunto: {obj.assunto}")
        
        # Try to save
        obj.save()
        print(f"  SUCCESS: Saved {obj.id}")
        obj.delete()
    except ValidationError as e:
        print(f"  VALIDATION ERROR on save: {e}")
    except Exception as e:
        print(f"  ERROR on save: {type(e).__name__}: {e}")
else:
    print(f"  Form is INVALID")
    print(f"  Errors: {form.errors}")

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
