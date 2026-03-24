# ðŸ”— VinculaÃ§Ã£o AutomÃ¡tica de DÃ­zimos com Entradas BancÃ¡rias e de Caixa

## ðŸ“‹ DescriÃ§Ã£o

Este mÃ³dulo implementa a vinculaÃ§Ã£o **automÃ¡tica** de registros de dÃ­zimos/ofertas com entradas bancÃ¡rias (`Entradabanco`) e **entradas de caixa** (`Entradacaixa`). O sistema tenta vincular registros com base em critÃ©rios de correspondÃªncia:

- **Data correspondente**: A data do dÃ­zimo deve corresponder Ã  data da entrada (bancÃ¡ria ou caixa)
- **Valor**: O valor do dÃ­zimo deve ser igual ao valor da entrada (ou prÃ³ximo, com tolerÃ¢ncia)
- **Moeda**: Ambos devem estar na mesma moeda

## ðŸš€ Como Funciona

### 1. **Auto-vinculaÃ§Ã£o em Tempo Real** (Signals)

Quando um novo dÃ­zimo ou entrada bancÃ¡ria Ã© criado, o sistema automaticamente tenta encontrar e vincular um registro correspondente:

```python
# Exemplo: Quando vocÃª cria um dÃ­zimo
dizimo = Dizimooferta(
    irmao=irmao,
    valor=500.00,
    moeda="AKZ",
    datacorrespondente="2025-03-05",
    tipooferta=tipo_oferta
)
dizimo.save()
# âœ… Sistema tenta vincular automaticamente com uma entrada bancÃ¡ria

# Exemplo: Quando vocÃª cria uma entrada bancÃ¡ria
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
# âœ… Sistema tenta vincular automaticamente com um dÃ­zimo
```

### 2. **VinculaÃ§Ã£o em Lote** (Management Command)

Para vincular dÃ­zimos e entradas **jÃ¡ existentes** que nÃ£o foram vinculados:

```bash
# Vincular TUDO (banco + caixa)
python manage.py vincular_dizimos

# Vincular apenas com BANCO
python manage.py vincular_dizimos --banco

# Vincular apenas com CAIXA
python manage.py vincular_dizimos --caixa

# Vincular apenas moeda especÃ­fica
python manage.py vincular_dizimos --moeda AKZ

# Permitir re-vinculaÃ§Ã£o de registros jÃ¡ vinculados
python manage.py vincular_dizimos --force

# Ver relatÃ³rio COMPLETO (banco + caixa)
python manage.py vincular_dizimos --relatorio

# Desvincular um dÃ­zimo do BANCO
python manage.py vincular_dizimos --desvincular 123

# Desvincular um dÃ­zimo da CAIXA
python manage.py vincular_dizimos --desvincular-caixa 123

# Combinar opÃ§Ãµes
python manage.py vincular_dizimos --caixa --dias-tolerancia 2 --moeda AKZ
```

### 3. **TolerÃ¢ncia de Datas**

Por padrÃ£o, o sistema procura correspondÃªncias exatas na data. VocÃª pode aumentar a tolerÃ¢ncia:

```bash
# Aceitar diferenÃ§as de atÃ© 2 dias
python manage.py vincular_dizimos --dias-tolerancia 2
```

## ðŸ“¦ Arquivos Modificados/Criados

### Novos Arquivos:

1. **`sitetibl/dizimo_utils.py`**
   - FunÃ§Ãµes utilitÃ¡rias para vinculaÃ§Ã£o
   - LÃ³gica de busca e correspondÃªncia
   - RelatÃ³rios de vinculaÃ§Ã£o

2. **`sitetibl/management/commands/vincular_dizimos.py`**
   - Management command para vinculaÃ§Ã£o em lote
   - CLI para operaÃ§Ãµes de vinculaÃ§Ã£o/desvinculaÃ§Ã£o

### Arquivos Modificados:

1. **`sitetibl/signals.py`**
   - Adicionadas importaÃ§Ãµes: `Dizimooferta`, `Entradabanco`
   - Novos signals:
     - `auto_vincular_dizimo_com_banco()`: Dispara quando dÃ­zimo Ã© criado
     - `auto_vincular_banco_com_dizimos()`: Dispara quando entrada Ã© criada

## ðŸ“Š Exemplo de Uso PrÃ¡tico

### CenÃ¡rio 1: Auto-vinculaÃ§Ã£o em Tempo Real

1. IrmÃ£o deposita R$ 500 no banco em 05/03/2025
2. VocÃª cria um registro de entrada bancÃ¡ria:
   ```
   Valor: 500.00 AKZ
   Data: 05/03/2025
   ```
3. Sistema procura dÃ­zimos nÃ£o vinculados com:
   ```
   Valor: 500.00 AKZ
   Data: 05/03/2025
   ```
4. âœ… Se encontrar, vincula automaticamente!

### CenÃ¡rio 2: Vincular Registros HistÃ³ricos

```bash
# Ver situaÃ§Ã£o atual
python manage.py vincular_dizimos --relatorio

# Vincular todos os nÃ£o vinculados
python manage.py vincular_dizimos

# Ver nova situaÃ§Ã£o
python manage.py vincular_dizimos --relatorio
```

## ðŸ”§ FunÃ§Ãµes DisponÃ­veis (Para Uso em Code)

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
    force=True   # Re-vincular jÃ¡ vinculados
)
```

### `relatorio_vinculacao()`

```python
from sitetibl.dizimo_utils import relatorio_vinculacao

rel = relatorio_vinculacao()
print(f"Taxa de vinculaÃ§Ã£o: {rel['taxa_vinculacao_dizimos']}")
```

### `desvincular_dizimo()`

```python
from sitetibl.dizimo_utils import desvincular_dizimo

sucesso = desvincular_dizimo(dizimo_id=123)
```

## âš™ï¸ ConfiguraÃ§Ãµes

Nenhuma configuraÃ§Ã£o adicional Ã© necessÃ¡ria. O sistema funciona automaticamente com as models jÃ¡ existentes:

- âœ… `Dizimooferta.entradabanco` (ForeignKey existente)
- âœ… `Entradabanco` (Model existente)

## ðŸŽ¯ CritÃ©rios de CorrespondÃªncia

A vinculaÃ§Ã£o automÃ¡tica usa os seguintes critÃ©rios:

| Campo | ObrigatÃ³rio | Exato | TolerÃ¢ncia |
| ------- | ------------- | ------- | ----------- |
| **Data** | âœ… Sim | âœ… Sim | OpÃ§Ã£o `--dias-tolerancia` |
| **Valor** | âœ… Sim | âœ… Sim | - |
| **Moeda** | âœ… Sim | âœ… Sim | - |
| **IrmÃ£o/ResponsÃ¡vel** | âŒ NÃ£o | - | - |
| **Tipo de Entrada** | âœ… Banco ou Caixa | âœ… Um por vez | - |
| **Status VinculaÃ§Ã£o** | âœ… Sim | âœ… NÃ£o vinculado | OpÃ§Ã£o `--force` |

## ðŸ“ˆ BenefÃ­cios

1. **AutomaÃ§Ã£o**: Reduz trabalho manual de vinculaÃ§Ã£o
2. **PrecisÃ£o**: Evita erros de vinculaÃ§Ã£o manual
3. **Rastreabilidade**: Todos os dÃ­zimos ficam vinculados a entradas no banco
4. **Auditoria**: Facilita reconciliaÃ§Ã£o e auditoria financeira
5. **Flexibilidade**: Suporta mÃºltiplas moedas e tolerÃ¢ncias

## âš ï¸ ObservaÃ§Ãµes Importantes

1. **Registros com mesmo valor e data**: Se houver mÃºltiplos dÃ­zimos/entradas com mesmos dados, apenas o primeiro serÃ¡ vinculado
2. **DesvinculaÃ§Ã£o**: VocÃª pode desvincular manualmente quando necessÃ¡rio
3. **Re-vinculaÃ§Ã£o**: Use `--force` para vincular novamente registros jÃ¡ vinculados
4. **Performance**: Em bases de dados grandes, considere executar o comando fora de horÃ¡rio de pico

## ðŸ› Troubleshooting

### Problema: DÃ­zimos nÃ£o estÃ£o sendo vinculados

**PossÃ­veis causas:**
- Data nÃ£o corresponde (use `--dias-tolerancia`)
- Valor nÃ£o Ã© exato (verifique casas decimais)
- Moeda diferente
- Entrada jÃ¡ vinculada com outro dÃ­zimo

**SoluÃ§Ã£o:**
```bash
# Verificar situaÃ§Ã£o
python manage.py vincular_dizimos --relatorio

# Tentar com tolerÃ¢ncia de 1 dia
python manage.py vincular_dizimos --dias-tolerancia 1

# ForÃ§ar re-vinculaÃ§Ã£o
python manage.py vincular_dizimos --force
```

### Problema: Desvincular manualmente

```bash
# Desvincular um dÃ­zimo especÃ­fico
python manage.py vincular_dizimos --desvincular 123
```

## ðŸ“ Logs e Monitoramento

O sistema exibe mensagens de progresso:

```
âœ… DÃ­zimo 42 vinculado com Entrada BancÃ¡ria 101
âœ… Entrada BancÃ¡ria 102 vinculada com DÃ­zimo 43
âŒ Entrada 104 - Sem correspondÃªncia de dÃ­zimo
```

## ðŸš€ PrÃ³ximos Passos Sugeridos

1. **API Endpoint**: Criar endpoint para vincular/desvincular via web
2. **Dashboard**: Adicionar dashboard mostrando taxa de vinculaÃ§Ã£o
3. **Alertas**: Notificar quando hÃ¡ discrepÃ¢ncias
4. **ReconciliaÃ§Ã£o**: Automatizar reconciliaÃ§Ã£o mensal

---

**Desenvolvido com â¤ï¸ para melhorar a gestÃ£o financeira da TIBL**
