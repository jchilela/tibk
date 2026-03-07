# 🏪 Extensão: Vinculação com Entradas de Caixa

## 📝 Resumo das Mudanças

Foi expandido o sistema de vinculação automática para incluir também **entradas de caixa** (`Entradacaixa`), além das entradas bancárias que já existiam.

## ✨ O que foi adicionado

### 1. **Auto-vinculação em Tempo Real com Caixa**
Quando você cria uma entrada de caixa com valores correspondentes a um dízimo, o sistema vincula automaticamente:

```python
# Criar um dízimo
dizimo = Dizimooferta.objects.create(
    irmao=irmao,
    valor=500.00,
    moeda="AKZ",
    datacorrespondente="2026-03-20",
    tipooferta=tipo_oferta
)

# Criar uma entrada de caixa - se corresponder, vincula automaticamente!
caixa = Entradacaixa.objects.create(
    valor=500.00,
    moeda="AKZ",
    data="2026-03-20",
    hora="10:30",
    rubrica=rubrica,
    responsavel=irmao
)
# ✅ Dízimo vinculado automaticamente com caixa!
```

### 2. **Funções Utilitárias em `sitetibl/dizimo_utils.py`**

#### Novas funções adicionadas:
- `vincular_dizimos_com_caixa()` - Vincular dízimos com entradas de caixa
- `vincular_caixas_existentes()` - Vincular entradas de caixa com dízimos
- `buscar_entrada_caixa_correspondente()` - Buscar caixa que corresponda
- `buscar_dizimos_para_caixa()` - Buscar dízimos para uma caixa
- `desvincular_dizimo_caixa()` - Desvincular um dízimo de caixa
- `relatorio_vinculacao_completa()` - Relatório com banco + caixa

#### Funções melhoradas:
- Imports atualizados para incluir `Entradacaixa`

### 3. **Signals Novos em `sitetibl/signals.py`**

Dois novos receivers foram adicionados:

```python
@receiver(post_save, sender=Dizimooferta)
def auto_vincular_dizimo_com_caixa()
    # Tenta vincular dízimo com caixa

@receiver(post_save, sender=Entradacaixa)  
def auto_vincular_caixa_com_dizimos()
    # Tenta vincular caixa com dízimos
```

### 4. **Management Command Expandido**

O comando `vincular_dizimos` agora suporta:

```bash
# Vincular apenas com CAIXA
python manage.py vincular_dizimos --caixa

# Desvincular de CAIXA
python manage.py vincular_dizimos --desvincular-caixa <ID>

# Relatório agora mostra BANCO + CAIXA
python manage.py vincular_dizimos --relatorio
```

## 📊 Estrutura do Relatório Completo

O novo relatório mostra informações separadas para banco e caixa:

```
📊 RELATÓRIO COMPLETO DE VINCULAÇÃO

📌 DÍZIMOS:
  Total: 5
  ✅ Vinculados (total): 2
     └─ Com Banco: 1
     └─ Com Caixa: 1
  Não vinculados: 3
  Taxa geral: 40.00%

🏦 ENTRADAS BANCÁRIAS:
  Total: 3
  Com dízimo vinculado: 1
  Sem dízimo: 2
  Taxa: 33.33%

🏪 ENTRADAS DE CAIXA:
  Total: 4
  Com dízimo vinculado: 1
  Sem dízimo: 3
  Taxa: 25.00%
```

## 🧪 Testes Realizados

### ✅ Teste 1: Auto-vinculação com Caixa
**Resultado**: ✅ SUCESSO

Quando uma entrada de caixa foi criada com valores correspondentes a um dízimo, o sistema automaticamente vinculou.

**Log de execução:**
```
✅ Entrada Caixa ID 4 vinculada com Dízimo ID 5
```

**Estatísticas:**
- Antes: 0% taxa de dízimos vinculados com caixa
- Depois: 25% taxa de caixa

### ✅ Teste 2: Management Command Caixa
**Resultado**: ✅ SUCESSO

Command executou com sucesso mostrando:
```
🏪 Processando entradas de caixa...
  [Caixa → Dízimos] Total processados: 4
```

### ✅ Teste 3: Relatório Completo
**Resultado**: ✅ SUCESSO

Relatório mostrando Banco + Caixa em tempo real:
```
📌 DÍZIMOS:
  ✅ Vinculados (total): 2
     └─ Com Banco: 1
     └─ Com Caixa: 1
```

## 🔄 Como Funciona a Prioridade

Um dízimo pode ser vinculado com **banco OU caixa**, mas não com ambos simultaneamente por padrão.

Se você tiver um dízimo que corresponde tanto a um banco quanto a uma caixa:

1. **Primeiro criado** vincula primeiro
2. Use `--force` para re-vincular a outro

```bash
# Desvincular de caixa e re-vincular com banco
python manage.py vincular_dizimos --desvincular-caixa <ID>
python manage.py vincular_dizimos --banco --force
```

## 💡 Casos de Uso

### Cenário 1: Dízimo em Caixa
```
1. Irmão dá dízimo pessoalmente na celula (caixa)
2. Sistema vincula automaticamente
3. Depois transferem para banco
4. Podem desvincular de caixa e vincular com bank entry
```

### Cenário 2: Dízimo Direto no Banco
```
1. Irmão transfere para conta bancária
2. Sistema vincula automaticamente com bank entry
3. Pronto!
```

### Cenário 3: Fundo Único
```
1. Entrada caixa é depois depositada no banco
2. Criar saída de caixa = entrada de banco
3. Ambas ficam vinculadas ao mesmo dízimo? Não.
4. Apenas uma pode estar vinculada por vez
```

## 🚀 Benefícios Adicionados

✅ **Cobertura Completa**: Agora todas as entradas de dízimo (banco + caixa) são rastreadas
✅ **Flexibilidade**: Pode usar banco ou caixa conforme necessário
✅ **Auditoria**: Ambos os canais têm rastreamento automático
✅ **Relatórios**: Visão clara de onde estão vindo os dízimos

## ⚠️ Notas Importantes

1. **Não há limite técnico** em vincular dízimo com múltiplas entradas
   - Mas a interface atual suporta apenas uma por tipo (banco OU caixa)
   - Para vincular com ambas, seria necessário campo de Many-to-Many

2. **Ordenação**:
   - Se houver múltiplas entradas de caixa com mesmo valor/data, apenas a primeira vincula
   - Use dates + horas únicas para evitar conflitos

3. **Desvincular**:
   - Sempre reversível
   - Não afeta o registro original, apenas remove o link

## 📚 Documentação Atualizada

Todos os arquivos de documentação foram atualizados:
- `docs/VINCULACAO_DIZIMOS.md` - Guia completo
- `docs/GUIA_RAPIDO_VINCULACAO.md` - Referência rápida
- `docs/IMPLEMENTACAO_VINCULACAO.md` - Detalhes técnicos

## 🔮 Próximas Melhorias Sugeridas

1. **Dashboard**: Mostrar gráfico de dízimos por canal (banco vs caixa)
2. **Reconciliação**: Verificar se caixa foi transferida para banco
3. **Alertas**: Notificar se há discrepâncias entre canais
4. **Bulk Operations**: Permitir vincular múltiplos dízimos de uma vez
5. **Many-to-Many**: Permitir vincular com banco E caixa simultaneamente

---

**Status**: ✅ Completo e Testado
**Versão**: 2.0 (Com suporte a Caixa)
