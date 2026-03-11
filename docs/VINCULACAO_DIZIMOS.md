# 🔗 Vinculação Automática de Dízimos com Entradas Bancárias e de Caixa

## 📋 Descrição

Este módulo implementa a vinculação **automática** de registros de dízimos/ofertas com entradas bancárias (`Entradabanco`) e **entradas de caixa** (`Entradacaixa`). O sistema tenta vincular registros com base em critérios de correspondência:

- **Data correspondente**: A data do dízimo deve corresponder à data da entrada (bancária ou caixa)
- **Valor**: O valor do dízimo deve ser igual ao valor da entrada (ou próximo, com tolerância)
- **Moeda**: Ambos devem estar na mesma moeda

## 🚀 Como Funciona

### 1. **Auto-vinculação em Tempo Real** (Signals)

Quando um novo dízimo ou entrada bancária é criado, o sistema automaticamente tenta encontrar e vincular um registro correspondente:

```python
# Exemplo: Quando você cria um dízimo
dizimo = Dizimooferta(
    irmao=irmao,
    valor=500.00,
    moeda="AKZ",
    datacorrespondente="2025-03-05",
    tipooferta=tipo_oferta
)
dizimo.save()
# ✅ Sistema tenta vincular automaticamente com uma entrada bancária

# Exemplo: Quando você cria uma entrada bancária
entrada = Entradabanco(
    contaaacreditar=conta,
    valor=500.00,
    moeda="AKZ",
    data="2025-03-05",
    rubrica=rubrica,
    responsavel=irmao,
    via="1"
)
entrada.save()
# ✅ Sistema tenta vincular automaticamente com um dízimo
```

### 2. **Vinculação em Lote** (Management Command)

Para vincular dízimos e entradas **já existentes** que não foram vinculados:

```bash
# Vincular TUDO (banco + caixa)
python manage.py vincular_dizimos

# Vincular apenas com BANCO
python manage.py vincular_dizimos --banco

# Vincular apenas com CAIXA
python manage.py vincular_dizimos --caixa

# Vincular apenas moeda específica
python manage.py vincular_dizimos --moeda AKZ

# Permitir re-vinculação de registros já vinculados
python manage.py vincular_dizimos --force

# Ver relatório COMPLETO (banco + caixa)
python manage.py vincular_dizimos --relatorio

# Desvincular um dízimo do BANCO
python manage.py vincular_dizimos --desvincular 123

# Desvincular um dízimo da CAIXA
python manage.py vincular_dizimos --desvincular-caixa 123

# Combinar opções
python manage.py vincular_dizimos --caixa --dias-tolerancia 2 --moeda AKZ
```

### 3. **Tolerância de Datas**

Por padrão, o sistema procura correspondências exatas na data. Você pode aumentar a tolerância:

```bash
# Aceitar diferenças de até 2 dias
python manage.py vincular_dizimos --dias-tolerancia 2
```

## 📦 Arquivos Modificados/Criados

### Novos Arquivos:

1. **`sitetibl/dizimo_utils.py`**
   - Funções utilitárias para vinculação
   - Lógica de busca e correspondência
   - Relatórios de vinculação

2. **`sitetibl/management/commands/vincular_dizimos.py`**
   - Management command para vinculação em lote
   - CLI para operações de vinculação/desvinculação

### Arquivos Modificados:

1. **`sitetibl/signals.py`**
   - Adicionadas importações: `Dizimooferta`, `Entradabanco`
   - Novos signals:
     - `auto_vincular_dizimo_com_banco()`: Dispara quando dízimo é criado
     - `auto_vincular_banco_com_dizimos()`: Dispara quando entrada é criada

## 📊 Exemplo de Uso Prático

### Cenário 1: Auto-vinculação em Tempo Real

1. Irmão deposita R$ 500 no banco em 05/03/2025
2. Você cria um registro de entrada bancária:
   ```
   Valor: 500.00 AKZ
   Data: 05/03/2025
   ```
3. Sistema procura dízimos não vinculados com:
   ```
   Valor: 500.00 AKZ
   Data: 05/03/2025
   ```
4. ✅ Se encontrar, vincula automaticamente!

### Cenário 2: Vincular Registros Históricos

```bash
# Ver situação atual
python manage.py vincular_dizimos --relatorio

# Vincular todos os não vinculados
python manage.py vincular_dizimos

# Ver nova situação
python manage.py vincular_dizimos --relatorio
```

## 🔧 Funções Disponíveis (Para Uso em Code)

### `vincular_dizimos_existentes()`

```python
from sitetibl.dizimo_utils import vincular_dizimos_existentes

stats = vincular_dizimos_existentes(
    dias_tolerancia=0,
    moeda="AKZ",
    force=False
)
print(f"Vinculados: {stats['sucesso']}")
```

### `vincular_entradas_bancarias_existentes()`

```python
from sitetibl.dizimo_utils import vincular_entradas_bancarias_existentes

stats = vincular_entradas_bancarias_existentes(
    dias_tolerancia=2,
    moeda=None,  # Todas as moedas
    force=True   # Re-vincular já vinculados
)
```

### `relatorio_vinculacao()`

```python
from sitetibl.dizimo_utils import relatorio_vinculacao

rel = relatorio_vinculacao()
print(f"Taxa de vinculação: {rel['taxa_vinculacao_dizimos']}")
```

### `desvincular_dizimo()`

```python
from sitetibl.dizimo_utils import desvincular_dizimo

sucesso = desvincular_dizimo(dizimo_id=123)
```

## ⚙️ Configurações

Nenhuma configuração adicional é necessária. O sistema funciona automaticamente com as models já existentes:

- ✅ `Dizimooferta.entradabanco` (ForeignKey existente)
- ✅ `Entradabanco` (Model existente)

## 🎯 Critérios de Correspondência

A vinculação automática usa os seguintes critérios:

| Campo | Obrigatório | Exato | Tolerância |
|-------|-------------|-------|-----------|
| **Data** | ✅ Sim | ✅ Sim | Opção `--dias-tolerancia` |
| **Valor** | ✅ Sim | ✅ Sim | - |
| **Moeda** | ✅ Sim | ✅ Sim | - |
| **Irmão/Responsável** | ❌ Não | - | - |
| **Tipo de Entrada** | ✅ Banco ou Caixa | ✅ Um por vez | - |
| **Status Vinculação** | ✅ Sim | ✅ Não vinculado | Opção `--force` |

## 📈 Benefícios

1. **Automação**: Reduz trabalho manual de vinculação
2. **Precisão**: Evita erros de vinculação manual
3. **Rastreabilidade**: Todos os dízimos ficam vinculados a entradas no banco
4. **Auditoria**: Facilita reconciliação e auditoria financeira
5. **Flexibilidade**: Suporta múltiplas moedas e tolerâncias

## ⚠️ Observações Importantes

1. **Registros com mesmo valor e data**: Se houver múltiplos dízimos/entradas com mesmos dados, apenas o primeiro será vinculado
2. **Desvinculação**: Você pode desvincular manualmente quando necessário
3. **Re-vinculação**: Use `--force` para vincular novamente registros já vinculados
4. **Performance**: Em bases de dados grandes, considere executar o comando fora de horário de pico

## 🐛 Troubleshooting

### Problema: Dízimos não estão sendo vinculados

**Possíveis causas:**
- Data não corresponde (use `--dias-tolerancia`)
- Valor não é exato (verifique casas decimais)
- Moeda diferente
- Entrada já vinculada com outro dízimo

**Solução:**
```bash
# Verificar situação
python manage.py vincular_dizimos --relatorio

# Tentar com tolerância de 1 dia
python manage.py vincular_dizimos --dias-tolerancia 1

# Forçar re-vinculação
python manage.py vincular_dizimos --force
```

### Problema: Desvincular manualmente

```bash
# Desvincular um dízimo específico
python manage.py vincular_dizimos --desvincular 123
```

## 📝 Logs e Monitoramento

O sistema exibe mensagens de progresso:

```
✅ Dízimo 42 vinculado com Entrada Bancária 101
✅ Entrada Bancária 102 vinculada com Dízimo 43
❌ Entrada 104 - Sem correspondência de dízimo
```

## 🚀 Próximos Passos Sugeridos

1. **API Endpoint**: Criar endpoint para vincular/desvincular via web
2. **Dashboard**: Adicionar dashboard mostrando taxa de vinculação
3. **Alertas**: Notificar quando há discrepâncias
4. **Reconciliação**: Automatizar reconciliação mensal

---

**Desenvolvido com ❤️ para melhorar a gestão financeira da TIBL**
