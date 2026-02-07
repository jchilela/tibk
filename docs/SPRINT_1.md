# Sprint 1 - Lançamento do Módulo Financeiro

**Data de Início**: 10 de Fevereiro de 2026 (Segunda-feira)  
**Data de Término**: 21 de Fevereiro de 2026 (Sexta-feira) - 10 dias úteis  
**Departamento-Alvo**: Departamento de Finanças  
**Objectivo**: Lançar o sistema de gestão financeira completo para uso do departamento de finanças da TIBL

---

## 🎯 Objectivo da Sprint

Entregar um sistema financeiro completo e funcional que permita ao departamento de finanças da igreja gerir todas as operações financeiras de forma centralizada, segura e eficiente.

---

## 📦 Módulos Financeiros a Concluir

### 1. Gestão de Bancos e Contas Bancárias

#### 1.1 Bancos
**Status**: ✅ Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [x] Cadastro de bancos (designação, abreviação, gestor, contactos)
- [ ] Listagem de bancos com filtros
- [ ] Edição de dados bancários
- [ ] Eliminação de bancos (com validação de dependências)
- [ ] Página de detalhes do banco

**Critérios de Aceitação**:
- Gestor financeiro consegue cadastrar novos bancos
- Sistema valida campos obrigatórios
- Não permite eliminação de bancos com contas activas

#### 1.2 Contas Bancárias
**Status**: ✅ Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [x] Cadastro de contas bancárias (banco, número, IBAN, tipo de moeda)
- [ ] Listagem de contas com filtros por banco/moeda
- [ ] Visualização de saldo actual
- [ ] Edição de dados da conta
- [ ] Inactivação de contas (não eliminação física)
- [ ] Página de detalhes com histórico de movimentações

**Critérios de Aceitação**:
- IBAN e número de conta são únicos no sistema
- Saldo é calculado automaticamente com base nas transacções
- Validação de formato IBAN
- Sistema impede valores negativos sem autorização

---

### 2. Movimentações de Caixa

#### 2.1 Entradas de Caixa
**Status**: 🔨 Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Registo de entradas em caixa
- [ ] Vinculação com rubrica de entrada
- [ ] Registo de responsável pela entrada
- [ ] Campo de observações
- [ ] Listagem com filtros (data, rubrica, valor)
- [ ] Página de detalhes da entrada
- [ ] Edição (com auditoria)
- [ ] Cancelamento (não eliminação física)

**Critérios de Aceitação**:
- Todas as entradas têm rubrica e responsável
- Data e hora são registadas automaticamente
- Valores são sempre positivos
- Sistema mantém histórico de alterações (auditoria)

#### 2.2 Saídas de Caixa
**Status**: 🔨 Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Registo de saídas de caixa
- [ ] Vinculação com rubrica de saída
- [ ] Registo de responsável
- [ ] Campo de observações
- [ ] Data de controlo automática
- [ ] Listagem com filtros (data, rubrica, valor)
- [ ] Página de detalhes da saída
- [ ] Edição (com auditoria)
- [ ] Cancelamento com justificação

**Critérios de Aceitação**:
- Saídas requerem aprovação (workflow)
- Sistema valida saldo disponível antes de aprovar
- Mantém log de todas as alterações
- Valores são sempre positivos

---

### 3. Movimentações Bancárias

#### 3.1 Entradas Bancárias
**Status**: 🔨 Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Registo de entradas bancárias
- [ ] Selecção da conta a ser creditada
- [ ] Definição de via (depósito, transferência, multicaixa)
- [ ] Vinculação com rubrica
- [ ] Conta de origem (se transferência)
- [ ] Registo de responsável
- [ ] Actualização automática de saldo
- [ ] Listagem com filtros avançados
- [ ] Página de detalhes
- [ ] Edição (com auditoria)

**Critérios de Aceitação**:
- Via de entrada é obrigatória
- Para transferências, conta origem é obrigatória
- Saldo actualiza automaticamente e em tempo real
- Histórico de transacções é imutável

#### 3.2 Saídas Bancárias
**Status**: 🔨 Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Registo de saídas bancárias
- [ ] Selecção da conta de débito
- [ ] Definição de rubrica
- [ ] Conta destino (se transferência)
- [ ] Registo de responsável
- [ ] Actualização automática de saldo
- [ ] Validação de saldo disponível
- [ ] Listagem com filtros
- [ ] Página de detalhes
- [ ] Cancelamento com autorização

**Critérios de Aceitação**:
- Sistema não permite saída sem saldo suficiente
- Transferências entre contas são atómicas
- Saldo actualiza instantaneamente
- Requer aprovação para valores acima de X

---

### 4. Dízimos e Ofertas

#### 4.1 Gestão de Dízimos e Ofertas
**Status**: 🔨 Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Registo de dízimos e ofertas
- [ ] Selecção do tipo de oferta
- [ ] Vinculação com membro dizimista
- [ ] Associação com actividade (culto, célula, etc.)
- [ ] Vinculação automática com entrada bancária ou caixa
- [ ] Emissão de recibo (PDF)
- [ ] Listagem com filtros (membro, tipo, data, actividade)
- [ ] Relatórios de dízimos por membro
- [ ] Relatórios de ofertas por tipo
- [ ] Dashboard de arrecadação

**Critérios de Aceitação**:
- Dízimo deve estar vinculado a um membro
- Ofertas podem ser anónimas
- Sistema gera recibo automaticamente
- Vinculação com entrada (banco/caixa) é obrigatória
- Dashboard mostra tendências de arrecadação

---

### 5. Orçamento Departamental

#### 5.1 Gestão de Orçamento
**Status**: 🔨 Para concluir  
**Prioridade**: Média

**Funcionalidades**:
- [ ] Cadastro de orçamento anual por departamento
- [ ] Visualização de orçamento vs. realizado
- [ ] Alertas quando ultrapassar 80% do orçamento
- [ ] Listagem de orçamentos por ano
- [ ] Edição de valores (com aprovação)
- [ ] Relatório de execução orçamentária
- [ ] Dashboard de consumo por departamento

**Critérios de Aceitação**:
- Cada departamento tem orçamento único por ano
- Sistema calcula automaticamente o realizado
- Alertas são enviados aos gestores
- Relatórios exportáveis em PDF/Excel

#### 5.2 Pedidos de Saída
**Status**: 🔨 Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Criação de pedidos de saída
- [ ] Workflow de aprovação (solicitação → aprovação → execução)
- [ ] Vinculação com departamento e projecto
- [ ] Definição de centro de custo
- [ ] Upload de documentos comprovativos
- [ ] Validação contra orçamento disponível
- [ ] IBAN de destino
- [ ] Listagem com filtros (status, departamento, valor)
- [ ] Dashboard de pedidos pendentes
- [ ] Notificações por email

**Critérios de Aceitação**:
- Pedidos requerem justificação obrigatória
- Sistema valida orçamento disponível
- Workflow de aprovação é configurável
- Aprovador recebe notificação automática
- Após aprovação, gera saída automaticamente
- Histórico completo de aprovações

---

### 6. Rubricas Financeiras

#### 6.1 Rubricas de Entrada e Saída
**Status**: ✅ Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Cadastro de rubricas de entrada
- [ ] Cadastro de rubricas de saída
- [ ] Organização hierárquica (categorias)
- [ ] Listagem de rubricas activas
- [ ] Inactivação de rubricas não utilizadas
- [ ] Relatório de movimentações por rubrica

**Critérios de Aceitação**:
- Cada movimentação tem uma rubrica
- Rubricas podem ser categorizadas
- Não permite eliminação de rubricas com transacções
- Sistema sugere rubricas mais utilizadas

---

### 7. Relatórios Financeiros

#### 7.1 Relatórios Gerenciais
**Status**: 🔨 Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Relatório de fluxo de caixa (PDF/Excel)
- [ ] Relatório de movimentações bancárias (PDF/Excel)
- [ ] Relatório de dízimos e ofertas (PDF/Excel)
- [ ] Relatório de execução orçamentária (PDF/Excel)
- [ ] Relatório de pedidos de saída (PDF/Excel)
- [ ] DRE simplificado (Demonstrativo de Resultado)
- [ ] Balancete mensal
- [ ] Conciliação bancária

**Critérios de Aceitação**:
- Relatórios com filtros de período
- Exportação em PDF e Excel
- Gráficos visuais claros
- Totalizadores e subtotais correctos
- Assinatura digital nos PDFs

#### 7.2 Dashboard Financeiro
**Status**: 🔨 Para concluir  
**Prioridade**: Média

**Funcionalidades**:
- [ ] Total em caixa (saldo actual)
- [ ] Total em bancos (soma de todas as contas)
- [ ] Dízimos e ofertas do mês
- [ ] Gráfico de entrada vs. saída (mensal)
- [ ] Top 5 rubricas de entrada
- [ ] Top 5 rubricas de saída
- [ ] Execução orçamentária por departamento
- [ ] Pedidos pendentes de aprovação
- [ ] Alertas financeiros

**Critérios de Aceitação**:
- Dashboard actualiza em tempo real
- Gráficos interactivos
- Período personalizável
- Exportação de dados

---

## 🔐 Requisitos de Segurança

### Controlo de Acesso
- [ ] Apenas utilizadores do grupo "Finanças" acedem aos módulos financeiros
- [ ] Permissões diferenciadas (visualização, edição, aprovação, eliminação)
- [ ] Auditoria completa de todas as acções financeiras
- [ ] Logs de acesso e modificações

### Validações
- [ ] Validação de saldo antes de qualquer saída
- [ ] Validação de IBAN e dados bancários
- [ ] Campos monetários sempre positivos
- [ ] Bloqueio de edição após período de fecho contabilístico

### Backup e Recuperação
- [ ] Backup automático diário
- [ ] Backup antes de operações críticas
- [ ] Procedimento de recuperação documentado
- [ ] Testes de recuperação mensais

---

## 📊 Indicadores de Sucesso

### Métricas Técnicas
- [ ] 100% das funcionalidades financeiras implementadas
- [ ] 0 bugs críticos em produção
- [ ] Tempo de resposta < 2s para consultas
- [ ] Cobertura de testes > 80%

### Métricas de Negócio
- [ ] 100% do departamento de finanças treinado
- [ ] Redução de 50% no tempo de fecho mensal
- [ ] 90% de satisfação dos utilizadores
- [ ] 0 inconsistências nos relatórios

---

## 🧪 Testes e Validação

### Testes Unitários
- [ ] Models (validações, cálculos)
- [ ] Views (lógica de negócio)
- [ ] Forms (validações)
- [ ] Signals (actualizações automáticas)

### Testes de Integração
- [ ] Fluxo completo de entrada/saída
- [ ] Transferências entre contas
- [ ] Workflow de aprovação de pedidos
- [ ] Geração de relatórios

### Testes de Aceitação do Utilizador (UAT)
- [ ] Cenário 1: Registo de dízimo em culto
- [ ] Cenário 2: Pedido e aprovação de saída
- [ ] Cenário 3: Transferência entre contas
- [ ] Cenário 4: Fecho e relatórios mensais
- [ ] Cenário 5: Conciliação bancária

---

## 📚 Documentação

### Documentação Técnica
- [ ] Actualizar DOCUMENTACAO_TECNICA.md com módulos financeiros
- [ ] Documentar APIs REST (se houver)
- [ ] Diagramas de fluxo de trabalho
- [ ] Modelo de dados actualizado

### Documentação de Utilizador
- [ ] Manual do utilizador - Módulo Financeiro
- [ ] Vídeos tutoriais (screencast)
- [ ] FAQ - Perguntas frequentes
- [ ] Glossário financeiro

### Treinamento
- [ ] Sessão 1: Visão geral do sistema
- [ ] Sessão 2: Cadastros básicos (bancos, contas, rubricas)
- [ ] Sessão 3: Movimentações (entradas e saídas)
- [ ] Sessão 4: Dízimos e ofertas
- [ ] Sessão 5: Orçamento e pedidos de saída
- [ ] Sessão 6: Relatórios e fecho mensal

---

## 🚀 Plano de Deploy

### Pré-Produção (Semana 1: 10/02 - 14/02)
- [ ] Deploy em ambiente de homologação (Quarta-feira, 12/02)
- [ ] Migração de dados históricos se houver (Quinta-feira, 13/02)
- [ ] Testes de carga e performance (Quinta-feira, 13/02)
- [ ] Treinamento da equipa de TI (Sexta-feira, 14/02)
- [ ] Validação com gestor financeiro (Sexta-feira, 14/02)

### Produção (Semana 2: 17/02 - 21/02)
- [ ] Backup completo do sistema actual (Quinta-feira, 20/02 - 18:00)
- [ ] Deploy em produção (Sexta-feira, 21/02 - 08:00)
- [ ] Verificação de integridade dos dados (Sexta-feira, 21/02 - 09:00)
- [ ] Treinamento final da equipa (Sexta-feira, 21/02 - 10:00)
- [ ] Monitoramento activo durante o dia (Sexta-feira, 21/02)
- [ ] Suporte prioritário na semana seguinte (24/02 - 28/02)

### Contingência
- [ ] Plano de rollback documentado
- [ ] Sistema antigo mantido em standby por 30 dias
- [ ] Equipa de suporte disponível durante horário comercial
- [ ] Linha directa exclusiva para departamento financeiro

---

## 👥 Equipa e Responsabilidades

### Desenvolvimento
- **Tech Lead**: Responsável pela arquitectura e revisão de código
- **Dev Backend**: Implementação dos models, views e lógica de negócio
- **Dev Frontend**: Templates, formulários e dashboard
- **QA**: Testes e validação

### Negócio
- **Gestor Financeiro**: Validação de requisitos e UAT
- **Tesoureiro**: Testes e feedback
- **Pastor/Líder**: Aprovação final

---

## 📅 Cronograma Detalhado

### Semana 1 (10/02 - 14/02) - Segunda a Sexta

**Segunda-feira (10/02)**:
- Reunião de kick-off da sprint
- Setup do ambiente de desenvolvimento
- Revisão e refinamento dos models financeiros
- Levantamento de dúvidas com o gestor financeiro

**Terça-feira (11/02)**:
- Criação/actualização de forms e validações
- Implementação de views para bancos e contas bancárias
- Testes unitários dos models

**Quarta-feira (12/02)**:
- Implementação de views para entradas de caixa
- Implementação de views para saídas de caixa
- Criação de templates para movimentações de caixa

**Quinta-feira (13/02)**:
- Implementação de views para entradas bancárias
- Implementação de views para saídas bancárias
- Criação de templates para movimentações bancárias
- Testes unitários

**Sexta-feira (14/02)**:
- Implementação de dízimos e ofertas
- Vinculação com entradas bancárias/caixa
- Code review da semana
- Ajustes e correcções

### Semana 2 (17/02 - 21/02) - Segunda a Sexta

**Segunda-feira (17/02)**:
- Implementação de orçamento departamental
- Implementação de pedidos de saída
- Workflow de aprovação

**Terça-feira (18/02)**:
- Implementação de relatórios financeiros
- Geração de PDFs (fluxo de caixa, movimentações)
- Dashboard financeiro (gráficos)

**Quarta-feira (19/02)**:
- Testes de integração completos
- Correcção de bugs identificados
- Documentação técnica
- Preparação do manual do utilizador

**Quinta-feira (20/02)**:
- UAT (User Acceptance Testing) com departamento de finanças
- Ajustes finais baseados no feedback
- Deploy em ambiente de homologação
- Treinamento da equipa de finanças

**Sexta-feira (21/02)**:
- Deploy em produção (manhã)
- Verificação de integridade dos dados
- Treinamento final e entrega
- Monitoramento activo durante o dia
- Reunião de encerramento da sprint

---

## 🐛 Riscos e Mitigação

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Inconsistência de dados na migração | Média | Alto | Validação rigorosa, scripts de verificação, backup completo |
| Bugs em produção | Média | Alto | Testes extensivos, período de homologação, rollback preparado |
| Resistência dos utilizadores | Baixa | Médio | Treinamento adequado, suporte dedicado, interface intuitiva |
| Performance inadequada | Baixa | Médio | Testes de carga, optimização de queries, índices adequados |
| Falha de segurança | Baixa | Crítico | Code review, testes de segurança, permissões rigorosas |

---

## 📋 Checklist Final de Lançamento

### Técnico
- [ ] Todos os testes passando (unitários e integração)
- [ ] Code review completo
- [ ] Documentação técnica actualizada
- [ ] Logs configurados
- [ ] Monitoramento activo
- [ ] Backup automático funcionando
- [ ] SSL/HTTPS configurado
- [ ] Performance validada

### Funcional
- [ ] Todas as funcionalidades testadas
- [ ] UAT aprovado
- [ ] Relatórios conferidos
- [ ] Dashboard validado
- [ ] Fluxos de aprovação testados

### Operacional
- [ ] Manual do utilizador entregue
- [ ] Treinamento concluído
- [ ] Suporte escalado
- [ ] Plano de contingência preparado
- [ ] Comunicação aos utilizadores feita

---

## 📞 Contactos de Suporte

**Suporte Técnico**: [email/telefone]  
**Gestor do Projecto**: [email/telefone]  
**Emergências**: [telefone horário comercial]

---

## 📝 Notas Adicionais

Este documento será actualizado conforme o progresso da sprint. Todas as alterações devem ser comunicadas à equipa.

**Última actualização**: 07 de Fevereiro de 2026 (Sábado - Reunião de Planeamento)



*"Cada um contribua segundo propôs no seu coração, não com tristeza ou por necessidade; porque Deus ama ao que dá com alegria." - 2 Coríntios 9:7*
