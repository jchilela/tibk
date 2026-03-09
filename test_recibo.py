#!/usr/bin/env python
# test_recibo.py
"""
Script para testar a geração de recibo em PDF.
"""
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from sitetibl.models import Dizimooferta
from sitetibl.views import numero_por_extenso

print("=" * 70)
print("🧾 TESTE DE GERAÇÃO DE RECIBO")
print("=" * 70)

# Testa a função de conversão por extenso
print("\n1️⃣ Testando conversão de número por extenso:")
valores_teste = [100, 250.50, 1500, 5000, 10500.75, 50000]
for valor in valores_teste:
    extenso = numero_por_extenso(valor)
    print(f"   {valor:,.2f} → {extenso}")

# Lista os dízimos existentes
print("\n2️⃣ Dízimos disponíveis para gerar recibo:")
dizimos = Dizimooferta.objects.all()[:5]
if dizimos.count() == 0:
    print("   ❌ Nenhum dízimo encontrado no banco de dados")
else:
    for d in dizimos:
        print(f"   ID: {d.id} | {d.irmao.nome} | {d.valor} {d.moeda} | {d.datacorrespondente}")
    
    print(f"\n3️⃣ Para gerar um recibo, acesse:")
    for d in dizimos[:3]:
        print(f"   http://localhost:8000/dizimos/recibo/{d.id}/")

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70)
print("\n💡 Dica: Você também pode gerar recibos através do admin ou views.")
