#!/usr/bin/env python
# test_caixa_vinculacao.py
"""
Script para testar a vinculação automática de dízimos com entradas de caixa.
"""
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from sitetibl.models import (
    Dizimooferta, Entradacaixa, Irmao, TipoOferta, Rubricaentrada
)
from datetime import time

print("=" * 70)
print("🧪 TESTE DE VINCULAÇÃO AUTOMÁTICA COM CAIXA")
print("=" * 70)

# Pega os primeiros irmãos e estruturas necessárias
irmao = Irmao.objects.first()
tipo_oferta = TipoOferta.objects.first()
rubrica = Rubricaentrada.objects.first()

if not all([irmao, tipo_oferta, rubrica]):
    print("❌ Erro: Não há dados mínimos necessários")
    exit(1)

print(f"\n✅ Usando Irmão: {irmao}")
print(f"✅ Usando TipoOferta: {tipo_oferta}")
print(f"✅ Usando Rubrica: {rubrica}")

# Dados para teste com correspondência
data_teste = date(2026, 3, 20)
valor_teste = 7500.00
moeda_teste = "AKZ"
hora_teste = time(10, 30, 0)

print(f"\n📋 DADOS DE TESTE:")
print(f"   Data: {data_teste}")
print(f"   Valor: {valor_teste}")
print(f"   Moeda: {moeda_teste}")
print(f"   Hora: {hora_teste}")

# 1. Criar um dízimo
print(f"\n1️⃣ Criando um novo dízimo...")
dizimo = Dizimooferta.objects.create(
    irmao=irmao,
    valor=valor_teste,
    moeda=moeda_teste,
    tipooferta=tipo_oferta,
    datacorrespondente=data_teste
)
print(f"   ✅ Dízimo criado: ID {dizimo.id}")
print(f"   Caixa vinculada: {dizimo.entradacaixa}")

# 2. Criar uma entrada de caixa com dados correspondentes
print(f"\n2️⃣ Criando uma entrada de caixa correspondente...")
caixa = Entradacaixa.objects.create(
    valor=valor_teste,
    moeda=moeda_teste,
    data=data_teste,
    hora=hora_teste,
    rubrica=rubrica,
    responsavel=irmao
)
print(f"   ✅ Entrada de caixa criada: ID {caixa.id}")

# 3. Verificar se vinculação aconteceu automaticamente
print(f"\n3️⃣ Verificando vinculação automática...")
dizimo.refresh_from_db()
print(f"   Dízimo {dizimo.id} vinculado com Caixa: {dizimo.entradacaixa_id}")

if dizimo.entradacaixa_id == caixa.id:
    print(f"   ✅ SUCESSO! Vinculação automática com caixa funcionou!")
elif dizimo.entradacaixa_id is None:
    print(f"   ⚠️ Nenhuma vinculação automática ocorreu.")
    print(f"   💡 Você pode testar o comando:")
    print(f"      python manage.py vincular_dizimos --caixa")
else:
    print(f"   ⚠️ Vinculado com caixa diferente: {dizimo.entradacaixa_id}")

# 4. Mostrar status final
print(f"\n4️⃣ Status Final:")
print(f"   Dízimo ID: {dizimo.id}")
print(f"   Entrada de Caixa ID: {caixa.id}")
print(f"   Vinculação: {dizimo.entradacaixa_id}")

from sitetibl.dizimo_utils import relatorio_vinculacao_completa
rel = relatorio_vinculacao_completa()
print(f"\n📊 RELATÓRIO ATUALIZADO:")
print(f"   Dízimos vinculados (total): {rel['dizimos_vinculados_total']}")
print(f"   - Com Banco: {rel['dizimos_vinculados_banco']}")
print(f"   - Com Caixa: {rel['dizimos_vinculados_caixa']}")
print(f"   Taxa de caixa: {rel['taxa_caixa']}")

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70)
