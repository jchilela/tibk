# Guia de Treinamento — Módulo Financeiro TIBL

**Terceira Igreja Baptista de Luanda**
**Sistema TIBL — Departamento Financeiro**

---

## 1. Acesso ao Sistema

1. Abrir o navegador em: `http://localhost:8000`
2. Iniciar sessão com o teu utilizador e palavra-passe
3. No menu lateral, seleccionar **Financeiro**

> **Importante:** Só tens acesso às funcionalidades atribuídas ao teu grupo (Financeiro, Pastor, Administrador, etc.).

---

## 2. Entradas e Saídas

### 2.1 Registar uma Entrada

1. Menu → **Financeiro → Entradas**
2. Clicar em **Nova Entrada**
3. Preencher os campos:

| Campo | Descrição |
|---|---|
| **Tipo** | Escolher **Caixa** ou **Banco** |
| **Valor** | Montante da entrada (formato: 0,00) |
| **Moeda** | AKZ, USD ou EUR |
| **Conta a creditar** | *Aparece só se Tipo = Banco* — conta que recebe o valor |
| **Via** | *Aparece só se Tipo = Banco* — método (transferência, depósito, etc.) |
| **Conta origem** | *Aparece só se Tipo = Banco* — conta de onde vem o dinheiro (transferência) |
| **Data** | Data da entrada |
| **Hora** | Hora da entrada |
| **Rubrica** | Categoria da entrada (dízimo, oferta, doação, etc.) |
| **Responsável** | Pessoa que registou a entrada |
| **Observação** | Notas adicionais (opcional) |

> **Nota:** Quando selecionas **Caixa**, os campos de conta bancária, via e conta origem **desaparecem automaticamente** — não precisas de os preencher.

4. Clicar em **Finalizar Registro**

### 2.2 Registar uma Saída

1. Menu → **Financeiro → Saídas**
2. Clicar em **Nova Saída**
3. O processo é igual ao das entradas, mas com:
   - **Conta a debitar** — conta de onde sai o dinheiro (só se Tipo = Banco)
   - **Conta a creditar (transferência)** — conta que recebe (só se Tipo = Banco)

> O sistema **bloqueia saídas** se o saldo da conta for insuficiente.

### 2.3 Procurar Entradas/Saídas

- Na listagem, usar os filtros no topo da página
- Os filtros **actualizam automaticamente** ao digitar ou seleccionar — não precisas de clicar em nenhum botão
- Para limpar filtros, basta apagar o texto ou seleccionar "Todas"

---

## 3. Contas Bancárias

### 3.1 Procurar Contas

1. Menu → **Financeiro → Contas Bancárias**
2. Filtros disponíveis:
   - **Entidade Eclesiástica** — nome da instituição (ex: TIBL)
   - **Banco** — nome do banco (ex: BFA)
   - **Número da Conta**
   - **Moeda**
3. Os filtros actualizam automaticamente

### 3.2 Criar Nova Conta

1. Clicar em **Nova Conta**
2. Preencher por esta ordem:

| Campo | Descrição |
|---|---|
| **Banco** | Instituição bancária |
| **Entidade Eclesiástica** | Seleccionar a instituição a que a conta pertence |
| **Está activa** | Marcar se a conta está activa |
| **Número da Conta** | Número da conta bancária |
| **IBAN** | IBAN completo |
| **Moeda** | AKZ, USD ou EUR |
| **Saldo** | Saldo inicial |

3. Clicar em **Finalizar Registro**

---

## 4. Balanço Financeiro

### 4.1 Consultar o Balanço

1. Menu → **Financeiro → Balanço Financeiro**
2. Usar os filtros:
   - **Periodicidade** — Semanal, Mensal, Trimestral ou Anual
   - **Ano** — Ano específico ou "Todos"
   - **Moeda** — AKZ, USD, EUR ou Todas
3. Os resultados actualizam automaticamente

### 4.2 O que se vê no Balanço

- **Saldo Transitado** — saldo acumulado de períodos anteriores
- **Total de Entradas** — soma de todas as entradas no período
- **Total de Saídas** — soma de todas as saídas no período
- **Movimento Líquido** — entradas menos saídas
- **Saldo Final** — saldo acumulado actual
- **Tabela por período** — detalhe mês a mês (ou semana/trimestre)

### 4.3 Exportar para Excel

1. No topo do Balanço Financeiro, clicar em **Exportar Excel**
2. O ficheiro é descarregado automaticamente
3. O Excel contém:

   **Sheet 1 — Resumo Executivo:**
   - Logo e nome da igreja
   - KPIs em destaque (saldo, entradas, saídas, saldo final)
   - Tabela de indicadores detalhada

   **Sheet 2 — Detalhe por Período:**
   - Tabela completa com todos os períodos
   - Gráfico de barras: Entradas vs Saídas
   - Gráfico de linha: Evolução do Saldo Acumulado
   - Linha de totais

> O ficheiro é formatado para impressão (paisagem, ajustado à largura da página).

---

## 5. Dízimos e Ofertas

1. Menu → **Financeiro → Dízimos e Ofertas**
2. Para registar: clicar em **Novo Dízimo/Oferta**
3. Para procurar: usar os filtros (membro, tipo, data) — actualizam automaticamente
4. Para análise: clicar em **Análise** no menu para ver gráficos e estatísticas

---

## 6. Pedidos de Saída

1. Menu → **Financeiro → Pedidos de Saída**
2. Criar pedido com: valor, rubrica, descrição e documento justificativo
3. O pedido passa por aprovação (Pastor ou Financeiro conforme permissões)
4. Filtros actualizam automaticamente

---

## 7. Orçamentos de Departamento

1. Menu → **Financeiro → Orçamentos**
2. Cada departamento pode ter um orçamento anual
3. Consultar saldo disponível e gastos por rubrica

---

## 8. Dicas Rápidas

- **Filtros automáticos:** Todos os filtros do módulo financeiro actualizam sozinhos — não há botão "Procurar"
- **Caixa vs Banco:** Ao escolher "Caixa", os campos de conta bancária desaparecem
- **Saldo insuficiente:** O sistema avisa se tentares registar uma saída sem saldo suficiente
- **Excel profissional:** O balanço exportado vem com logo, gráficos e formatação institucional
- **Moeda:** Presta atenção à moeda seleccionada — os valores são filtrados por moeda

---

## 9. Problemas Comuns

| Problema | Solução |
|---|---|
| "Saldo insuficiente" ao registar saída | Verificar o saldo da conta no módulo de Contas Bancárias |
| Campos de conta não aparecem | Verificar se o Tipo está em "Banco" e não "Caixa" |
| Não consigo ver o módulo financeiro | Contactar o administrador para verificar permissões |
| Filtro não mostra resultados | Limpar os campos e tentar novamente |

---

**Dúvidas?** Contactar o administrador do sistema.

*Sistema TIBL — Terceira Igreja Baptista de Luanda*
*Departamento Financeiro*
