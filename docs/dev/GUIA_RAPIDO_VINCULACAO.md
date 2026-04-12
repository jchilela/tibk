# 🚀 Guia Rápido: Vinculação de Dízimos

## ⚡ Começar Agora

### 1. Vincular Todos (Banco + Caixa)
```bash
python manage.py vincular_dizimos
```

### 2. Vincular Apenas BANCO
```bash
python manage.py vincular_dizimos --banco
```

### 3. Vincular Apenas CAIXA
```bash
python manage.py vincular_dizimos --caixa
```

### 4. Ver Relatório Completo
```bash
python manage.py vincular_dizimos --relatorio
```

### 5. Desvincular
```bash
# Do banco
python manage.py vincular_dizimos --desvincular <ID>

# Da caixa
python manage.py vincular_dizimos --desvincular-caixa <ID>
```

## 📋 Opções Comuns

```bash
# Aceitar diferenças de até 2 dias
python manage.py vincular_dizimos --dias-tolerancia 2

# Vincular apenas moeda específica
python manage.py vincular_dizimos --moeda AKZ

# Re-vincular registros já vinculados
python manage.py vincular_dizimos --force

# Combinar opções
python manage.py vincular_dizimos --caixa --dias-tolerancia 1 --moeda AKZ
```

## 🔧 Usar em Python Code

```python
from sitetibl.dizimo_utils import (
    vincular_dizimos_com_caixa,
    vincular_caixas_existentes,
    relatorio_vinculacao_completa
)

# Vincular dízimos com caixa
stats = vincular_dizimos_com_caixa(dias_tolerancia=1, moeda="AKZ")
print(f"Vinculados: {stats['sucesso']}")

# Ver relatório completo
rel = relatorio_vinculacao_completa()
print(f"Taxa de caixa: {rel['taxa_caixa']}")
```

## 📞 Ajuda

```bash
python manage.py vincular_dizimos --help
```

---

Mais detalhes em: [docs/VINCULACAO_DIZIMOS.md](./VINCULACAO_DIZIMOS.md)
