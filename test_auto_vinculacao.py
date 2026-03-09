#!/usr/bin/env python
# test_auto_vinculacao.py
"""
Script para testar a vinculação automática de dízimos com entradas bancárias.
Cria registros de teste com dados correspondentes.
"""
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tibl.settings')
django.setup()

from sitetibl.models import (
    Dizimooferta, Entradabanco, Irmao, TipoOferta,
    Contabancaria, Rubricaentrada
)

print("=" * 70)
print("🧪 TESTE DE VINCULAÇÃO AUTOMÁTICA DE DÍZIMOS")
print("=" * 70)

# Pega os primeiros irmãos e estruturas necessárias
irmao = Irmao.objects.first()
tipo_oferta = TipoOferta.objects.first()
conta_bancaria = Contabancaria.objects.first()
rubrica = Rubricaentrada.objects.first()

if not all([irmao, tipo_oferta, conta_bancaria, rubrica]):
    print("❌ Erro: Não há dados mínimos necessários (Irmão, TipoOferta, Conta, Rubrica)")
    exit(1)

print(f"\n✅ Usando Irmão: {irmao}")
print(f"✅ Usando TipoOferta: {tipo_oferta}")
print(f"✅ Usando Conta Bancária: {conta_bancaria}")
print(f"✅ Usando Rubrica: {rubrica}")

# Dados para teste com correspondência
data_teste = date(2026, 3, 15)
valor_teste = 5000.00
moeda_teste = "AKZ"

print(f"\n📋 DADOS DE TESTE:")
print(f"   Data: {data_teste}")
print(f"   Valor: {valor_teste}")
print(f"   Moeda: {moeda_teste}")

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
print(f"   Entrada vinculada: {dizimo.entradabanco}")

# 2. Criar uma entrada bancária com dados correspondentes
print(f"\n2️⃣ Criando uma entrada bancária correspondente...")
entrada = Entradabanco.objects.create(
    contaaacreditar=conta_bancaria,
    valor=valor_teste,
    moeda=moeda_teste,
    data=data_teste,
    via="1",  # Depósito
    rubrica=rubrica,
    responsavel=irmao
)
print(f"   ✅ Entrada bancária criada: ID {entrada.id}")

# 3. Verificar se vinculação aconteceu automaticamente
print(f"\n3️⃣ Verificando vinculação automática...")
dizimo.refresh_from_db()
print(f"   Dízimo {dizimo.id} vinculado com Entrada: {dizimo.entradabanco_id}")

if dizimo.entradabanco_id == entrada.id:
    print(f"   ✅ SUCESSO! Vinculação automática funcionou!")
elif dizimo.entradabanco_id is None:
    print(f"   ⚠️ Nenhuma vinculação automática ocorreu.")
    print(f"   💡 Você pode vincular manualmente com:")
    print(f"      python manage.py vincular_dizimos")
else:
    print(f"   ⚠️ Vinculado com entrada diferente: {dizimo.entradabanco_id}")

# 4. Mostrar status final
print(f"\n4️⃣ Status Final:")
print(f"   Dízimo ID: {dizimo.id}")
print(f"   Entrada Bancária ID: {entrada.id}")
print(f"   Vinculação: {dizimo.entradabanco_id}")

from sitetibl.dizimo_utils import relatorio_vinculacao
rel = relatorio_vinculacao()
print(f"\n📊 RELATÓRIO ATUALIZADO:")
print(f"   Taxa de vinculação de dízimos: {rel['taxa_vinculacao_dizimos']}")
print(f"   Taxa de vinculação de entradas: {rel['taxa_vinculacao_entradas']}")

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70)
