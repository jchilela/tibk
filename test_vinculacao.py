#!/usr/bin/env python
# test_vinculacao.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from sitetibl.models import Dizimooferta, Entradabanco
from sitetibl.dizimo_utils import relatorio_vinculacao

print("=" * 60)
print("📊 DIAGNÓSTICO DE VINCULAÇÃO DE DÍZIMOS")
print("=" * 60)

print("\n=== DÍZIMOS EXISTENTES ===")
dizimos = Dizimooferta.objects.all()
print(f"Total: {dizimos.count()}")
for d in dizimos:
    status = "🔗" if d.entradabanco else "❌"
    print(f"{status} ID:{d.id} | {d.irmao.nome} | {d.valor} {d.moeda} | {d.datacorrespondente}")

print("\n=== ENTRADAS BANCÁRIAS EXISTENTES ===")
entradas = Entradabanco.objects.all()
print(f"Total: {entradas.count()}")
for e in entradas:
    print(f"ID:{e.id} | {e.valor} {e.moeda} | {e.data}")

print("\n=== RELATÓRIO GERAL ===")
rel = relatorio_vinculacao()
for chave, valor in rel.items():
    print(f"{chave}: {valor}")
