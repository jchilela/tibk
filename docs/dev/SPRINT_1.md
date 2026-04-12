# Sprint 1 - LanÃ§amento do MÃ³dulo Financeiro

**Data de InÃ­cio**: 10 de Fevereiro de 2026 (Segunda-feira)  
**Data de TÃ©rmino**: 21 de Fevereiro de 2026 (Sexta-feira) - 10 dias Ãºteis  
**Departamento-Alvo**: Departamento de FinanÃ§as  
**Objectivo**: LanÃ§ar o sistema de gestÃ£o financeira completo para uso do departamento de finanÃ§as da TIBL

---

## ðŸŽ¯ Objectivo da Sprint

Entregar um sistema financeiro completo e funcional que permita ao departamento de finanÃ§as da igreja gerir todas as operaÃ§Ãµes financeiras de forma centralizada, segura e eficiente.

---

## ðŸ“¦ MÃ³dulos Financeiros a Concluir

### 1. GestÃ£o de Bancos e Contas BancÃ¡rias

#### 1.1 Bancos
**Status**: âœ… Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [x] Cadastro de bancos (designaÃ§Ã£o, abreviaÃ§Ã£o, gestor, contactos)
- [ ] Listagem de bancos com filtros
- [ ] EdiÃ§Ã£o de dados bancÃ¡rios
- [ ] EliminaÃ§Ã£o de bancos (com validaÃ§Ã£o de dependÃªncias)
- [ ] PÃ¡gina de detalhes do banco

**CritÃ©rios de AceitaÃ§Ã£o**:
- Gestor financeiro consegue cadastrar novos bancos
- Sistema valida campos obrigatÃ³rios
- NÃ£o permite eliminaÃ§Ã£o de bancos com contas activas

#### 1.2 Contas BancÃ¡rias
**Status**: âœ… Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [x] Cadastro de contas bancÃ¡rias (banco, nÃºmero, IBAN, tipo de moeda)
- [ ] Listagem de contas com filtros por banco/moeda
- [ ] VisualizaÃ§Ã£o de saldo actual
- [ ] EdiÃ§Ã£o de dados da conta
- [ ] InactivaÃ§Ã£o de contas (nÃ£o eliminaÃ§Ã£o fÃ­sica)
- [ ] PÃ¡gina de detalhes com histÃ³rico de movimentaÃ§Ãµes

**CritÃ©rios de AceitaÃ§Ã£o**:
- IBAN e nÃºmero de conta sÃ£o Ãºnicos no sistema
- Saldo Ã© calculado automaticamente com base nas transacÃ§Ãµes
- ValidaÃ§Ã£o de formato IBAN
- Sistema impede valores negativos sem autorizaÃ§Ã£o

---

### 2. MovimentaÃ§Ãµes de Caixa

#### 2.1 Entradas de Caixa
**Status**: ðŸ”¨ Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Registo de entradas em caixa
- [ ] VinculaÃ§Ã£o com rubrica de entrada
- [ ] Registo de responsÃ¡vel pela entrada
- [ ] Campo de observaÃ§Ãµes
- [ ] Listagem com filtros (data, rubrica, valor)
- [ ] PÃ¡gina de detalhes da entrada
- [ ] EdiÃ§Ã£o (com auditoria)
- [ ] Cancelamento (nÃ£o eliminaÃ§Ã£o fÃ­sica)

**CritÃ©rios de AceitaÃ§Ã£o**:
- Todas as entradas tÃªm rubrica e responsÃ¡vel
- Data e hora sÃ£o registadas automaticamente
- Valores sÃ£o sempre positivos
- Sistema mantÃ©m histÃ³rico de alteraÃ§Ãµes (auditoria)

#### 2.2 SaÃ­das de Caixa
**Status**: ðŸ”¨ Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Registo de saÃ­das de caixa
- [ ] VinculaÃ§Ã£o com rubrica de saÃ­da
- [ ] Registo de responsÃ¡vel
- [ ] Campo de observaÃ§Ãµes
- [ ] Data de controlo automÃ¡tica
- [ ] Listagem com filtros (data, rubrica, valor)
- [ ] PÃ¡gina de detalhes da saÃ­da
- [ ] EdiÃ§Ã£o (com auditoria)
- [ ] Cancelamento com justificaÃ§Ã£o

**CritÃ©rios de AceitaÃ§Ã£o**:
- SaÃ­das requerem aprovaÃ§Ã£o (workflow)
- Sistema valida saldo disponÃ­vel antes de aprovar
- MantÃ©m log de todas as alteraÃ§Ãµes
- Valores sÃ£o sempre positivos

---

### 3. MovimentaÃ§Ãµes BancÃ¡rias

#### 3.1 Entradas BancÃ¡rias
**Status**: ðŸ”¨ Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Registo de entradas bancÃ¡rias
- [ ] SelecÃ§Ã£o da conta a ser creditada
- [ ] DefiniÃ§Ã£o de via (depÃ³sito, transferÃªncia, multicaixa)
- [ ] VinculaÃ§Ã£o com rubrica
- [ ] Conta de origem (se transferÃªncia)
- [ ] Registo de responsÃ¡vel
- [ ] ActualizaÃ§Ã£o automÃ¡tica de saldo
- [ ] Listagem com filtros avanÃ§ados
- [ ] PÃ¡gina de detalhes
- [ ] EdiÃ§Ã£o (com auditoria)

**CritÃ©rios de AceitaÃ§Ã£o**:
- Via de entrada Ã© obrigatÃ³ria
- Para transferÃªncias, conta origem Ã© obrigatÃ³ria
- Saldo actualiza automaticamente e em tempo real
- HistÃ³rico de transacÃ§Ãµes Ã© imutÃ¡vel

#### 3.2 SaÃ­das BancÃ¡rias
**Status**: ðŸ”¨ Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Registo de saÃ­das bancÃ¡rias
- [ ] SelecÃ§Ã£o da conta de dÃ©bito
- [ ] DefiniÃ§Ã£o de rubrica
- [ ] Conta destino (se transferÃªncia)
- [ ] Registo de responsÃ¡vel
- [ ] ActualizaÃ§Ã£o automÃ¡tica de saldo
- [ ] ValidaÃ§Ã£o de saldo disponÃ­vel
- [ ] Listagem com filtros
- [ ] PÃ¡gina de detalhes
- [ ] Cancelamento com autorizaÃ§Ã£o

**CritÃ©rios de AceitaÃ§Ã£o**:
- Sistema nÃ£o permite saÃ­da sem saldo suficiente
- TransferÃªncias entre contas sÃ£o atÃ³micas
- Saldo actualiza instantaneamente
- Requer aprovaÃ§Ã£o para valores acima de X

---

### 4. DÃ­zimos e Ofertas

#### 4.1 GestÃ£o de DÃ­zimos e Ofertas
**Status**: ðŸ”¨ Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Registo de dÃ­zimos e ofertas
- [ ] SelecÃ§Ã£o do tipo de oferta
- [ ] VinculaÃ§Ã£o com membro dizimista
- [ ] AssociaÃ§Ã£o com actividade (culto, cÃ©lula, etc.)
- [ ] VinculaÃ§Ã£o automÃ¡tica com entrada bancÃ¡ria ou caixa
- [ ] EmissÃ£o de recibo (PDF)
- [ ] Listagem com filtros (membro, tipo, data, actividade)
- [ ] RelatÃ³rios de dÃ­zimos por membro
- [ ] RelatÃ³rios de ofertas por tipo
- [ ] Dashboard de arrecadaÃ§Ã£o

**CritÃ©rios de AceitaÃ§Ã£o**:
- DÃ­zimo deve estar vinculado a um membro
- Ofertas podem ser anÃ³nimas
- Sistema gera recibo automaticamente
- VinculaÃ§Ã£o com entrada (banco/caixa) Ã© obrigatÃ³ria
- Dashboard mostra tendÃªncias de arrecadaÃ§Ã£o

---

### 5. OrÃ§amento Departamental

#### 5.1 GestÃ£o de OrÃ§amento
**Status**: ðŸ”¨ Para concluir  
**Prioridade**: MÃ©dia

**Funcionalidades**:
- [ ] Cadastro de orÃ§amento anual por departamento
- [ ] VisualizaÃ§Ã£o de orÃ§amento vs. realizado
- [ ] Alertas quando ultrapassar 80% do orÃ§amento
- [ ] Listagem de orÃ§amentos por ano
- [ ] EdiÃ§Ã£o de valores (com aprovaÃ§Ã£o)
- [ ] RelatÃ³rio de execuÃ§Ã£o orÃ§amentÃ¡ria
- [ ] Dashboard de consumo por departamento

**CritÃ©rios de AceitaÃ§Ã£o**:
- Cada departamento tem orÃ§amento Ãºnico por ano
- Sistema calcula automaticamente o realizado
- Alertas sÃ£o enviados aos gestores
- RelatÃ³rios exportÃ¡veis em PDF/Excel

#### 5.2 Pedidos de SaÃ­da
**Status**: ðŸ”¨ Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] CriaÃ§Ã£o de pedidos de saÃ­da
- [ ] Workflow de aprovaÃ§Ã£o (solicitaÃ§Ã£o â†’ aprovaÃ§Ã£o â†’ execuÃ§Ã£o)
- [ ] VinculaÃ§Ã£o com departamento e projecto
- [ ] DefiniÃ§Ã£o de centro de custo
- [ ] Upload de documentos comprovativos
- [ ] ValidaÃ§Ã£o contra orÃ§amento disponÃ­vel
- [ ] IBAN de destino
- [ ] Listagem com filtros (status, departamento, valor)
- [ ] Dashboard de pedidos pendentes
- [ ] NotificaÃ§Ãµes por email

**CritÃ©rios de AceitaÃ§Ã£o**:
- Pedidos requerem justificaÃ§Ã£o obrigatÃ³ria
- Sistema valida orÃ§amento disponÃ­vel
- Workflow de aprovaÃ§Ã£o Ã© configurÃ¡vel
- Aprovador recebe notificaÃ§Ã£o automÃ¡tica
- ApÃ³s aprovaÃ§Ã£o, gera saÃ­da automaticamente
- HistÃ³rico completo de aprovaÃ§Ãµes

---

### 6. Rubricas Financeiras

#### 6.1 Rubricas de Entrada e SaÃ­da
**Status**: âœ… Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] Cadastro de rubricas de entrada
- [ ] Cadastro de rubricas de saÃ­da
- [ ] OrganizaÃ§Ã£o hierÃ¡rquica (categorias)
- [ ] Listagem de rubricas activas
- [ ] InactivaÃ§Ã£o de rubricas nÃ£o utilizadas
- [ ] RelatÃ³rio de movimentaÃ§Ãµes por rubrica

**CritÃ©rios de AceitaÃ§Ã£o**:
- Cada movimentaÃ§Ã£o tem uma rubrica
- Rubricas podem ser categorizadas
- NÃ£o permite eliminaÃ§Ã£o de rubricas com transacÃ§Ãµes
- Sistema sugere rubricas mais utilizadas

---

### 7. RelatÃ³rios Financeiros

#### 7.1 RelatÃ³rios Gerenciais
**Status**: ðŸ”¨ Para concluir  
**Prioridade**: Alta

**Funcionalidades**:
- [ ] RelatÃ³rio de fluxo de caixa (PDF/Excel)
- [ ] RelatÃ³rio de movimentaÃ§Ãµes bancÃ¡rias (PDF/Excel)
- [ ] RelatÃ³rio de dÃ­zimos e ofertas (PDF/Excel)
- [ ] RelatÃ³rio de execuÃ§Ã£o orÃ§amentÃ¡ria (PDF/Excel)
- [ ] RelatÃ³rio de pedidos de saÃ­da (PDF/Excel)
- [ ] DRE simplificado (Demonstrativo de Resultado)
- [ ] Balancete mensal
- [ ] ConciliaÃ§Ã£o bancÃ¡ria

**CritÃ©rios de AceitaÃ§Ã£o**:
- RelatÃ³rios com filtros de perÃ­odo
- ExportaÃ§Ã£o em PDF e Excel
- GrÃ¡ficos visuais claros
- Totalizadores e subtotais correctos
- Assinatura digital nos PDFs

#### 7.2 Dashboard Financeiro
**Status**: ðŸ”¨ Para concluir  
**Prioridade**: MÃ©dia

**Funcionalidades**:
- [ ] Total em caixa (saldo actual)
- [ ] Total em bancos (soma de todas as contas)
- [ ] DÃ­zimos e ofertas do mÃªs
- [ ] GrÃ¡fico de entrada vs. saÃ­da (mensal)
- [ ] Top 5 rubricas de entrada
- [ ] Top 5 rubricas de saÃ­da
- [ ] ExecuÃ§Ã£o orÃ§amentÃ¡ria por departamento
- [ ] Pedidos pendentes de aprovaÃ§Ã£o
- [ ] Alertas financeiros

**CritÃ©rios de AceitaÃ§Ã£o**:
- Dashboard actualiza em tempo real
- GrÃ¡ficos interactivos
- PerÃ­odo personalizÃ¡vel
- ExportaÃ§Ã£o de dados

---

## ðŸ” Requisitos de SeguranÃ§a

### Controlo de Acesso
- [ ] Apenas utilizadores do grupo "FinanÃ§as" acedem aos mÃ³dulos financeiros
- [ ] PermissÃµes diferenciadas (visualizaÃ§Ã£o, ediÃ§Ã£o, aprovaÃ§Ã£o, eliminaÃ§Ã£o)
- [ ] Auditoria completa de todas as acÃ§Ãµes financeiras
- [ ] Logs de acesso e modificaÃ§Ãµes

### ValidaÃ§Ãµes
- [ ] ValidaÃ§Ã£o de saldo antes de qualquer saÃ­da
- [ ] ValidaÃ§Ã£o de IBAN e dados bancÃ¡rios
- [ ] Campos monetÃ¡rios sempre positivos
- [ ] Bloqueio de ediÃ§Ã£o apÃ³s perÃ­odo de fecho contabilÃ­stico

### Backup e RecuperaÃ§Ã£o
- [ ] Backup automÃ¡tico diÃ¡rio
- [ ] Backup antes de operaÃ§Ãµes crÃ­ticas
- [ ] Procedimento de recuperaÃ§Ã£o documentado
- [ ] Testes de recuperaÃ§Ã£o mensais

---

## ðŸ“Š Indicadores de Sucesso

### MÃ©tricas TÃ©cnicas
- [ ] 100% das funcionalidades financeiras implementadas
- [ ] 0 bugs crÃ­ticos em produÃ§Ã£o
- [ ] Tempo de resposta < 2s para consultas
- [ ] Cobertura de testes > 80%

### MÃ©tricas de NegÃ³cio
- [ ] 100% do departamento de finanÃ§as treinado
- [ ] ReduÃ§Ã£o de 50% no tempo de fecho mensal
- [ ] 90% de satisfaÃ§Ã£o dos utilizadores
- [ ] 0 inconsistÃªncias nos relatÃ³rios

---

## ðŸ§ª Testes e ValidaÃ§Ã£o

### Testes UnitÃ¡rios
- [ ] Models (validaÃ§Ãµes, cÃ¡lculos)
- [ ] Views (lÃ³gica de negÃ³cio)
- [ ] Forms (validaÃ§Ãµes)
- [ ] Signals (actualizaÃ§Ãµes automÃ¡ticas)

### Testes de IntegraÃ§Ã£o
- [ ] Fluxo completo de entrada/saÃ­da
- [ ] TransferÃªncias entre contas
- [ ] Workflow de aprovaÃ§Ã£o de pedidos
- [ ] GeraÃ§Ã£o de relatÃ³rios

### Testes de AceitaÃ§Ã£o do Utilizador (UAT)
- [ ] CenÃ¡rio 1: Registo de dÃ­zimo em culto
- [ ] CenÃ¡rio 2: Pedido e aprovaÃ§Ã£o de saÃ­da
- [ ] CenÃ¡rio 3: TransferÃªncia entre contas
- [ ] CenÃ¡rio 4: Fecho e relatÃ³rios mensais
- [ ] CenÃ¡rio 5: ConciliaÃ§Ã£o bancÃ¡ria

---

## ðŸ“š DocumentaÃ§Ã£o

### DocumentaÃ§Ã£o TÃ©cnica
- [ ] Actualizar DOCUMENTACAO_TECNICA.md com mÃ³dulos financeiros
- [ ] Documentar APIs REST (se houver)
- [ ] Diagramas de fluxo de trabalho
- [ ] Modelo de dados actualizado

### DocumentaÃ§Ã£o de Utilizador
- [ ] Manual do utilizador - MÃ³dulo Financeiro
- [ ] VÃ­deos tutoriais (screencast)
- [ ] FAQ - Perguntas frequentes
- [ ] GlossÃ¡rio financeiro

### Treinamento
- [ ] SessÃ£o 1: VisÃ£o geral do sistema
- [ ] SessÃ£o 2: Cadastros bÃ¡sicos (bancos, contas, rubricas)
- [ ] SessÃ£o 3: MovimentaÃ§Ãµes (entradas e saÃ­das)
- [ ] SessÃ£o 4: DÃ­zimos e ofertas
- [ ] SessÃ£o 5: OrÃ§amento e pedidos de saÃ­da
- [ ] SessÃ£o 6: RelatÃ³rios e fecho mensal

---

## ðŸš€ Plano de Deploy

### PrÃ©-ProduÃ§Ã£o (Semana 1: 10/02 - 14/02)
- [ ] Deploy em ambiente de homologaÃ§Ã£o (Quarta-feira, 12/02)
- [ ] MigraÃ§Ã£o de dados histÃ³ricos se houver (Quinta-feira, 13/02)
- [ ] Testes de carga e performance (Quinta-feira, 13/02)
- [ ] Treinamento da equipa de TI (Sexta-feira, 14/02)
- [ ] ValidaÃ§Ã£o com gestor financeiro (Sexta-feira, 14/02)

### ProduÃ§Ã£o (Semana 2: 17/02 - 21/02)
- [ ] Backup completo do sistema actual (Quinta-feira, 20/02 - 18:00)
- [ ] Deploy em produÃ§Ã£o (Sexta-feira, 21/02 - 08:00)
- [ ] VerificaÃ§Ã£o de integridade dos dados (Sexta-feira, 21/02 - 09:00)
- [ ] Treinamento final da equipa (Sexta-feira, 21/02 - 10:00)
- [ ] Monitoramento activo durante o dia (Sexta-feira, 21/02)
- [ ] Suporte prioritÃ¡rio na semana seguinte (24/02 - 28/02)

### ContingÃªncia
- [ ] Plano de rollback documentado
- [ ] Sistema antigo mantido em standby por 30 dias
- [ ] Equipa de suporte disponÃ­vel durante horÃ¡rio comercial
- [ ] Linha directa exclusiva para departamento financeiro

---

## ðŸ‘¥ Equipa e Responsabilidades

### Desenvolvimento
- **Tech Lead**: ResponsÃ¡vel pela arquitectura e revisÃ£o de cÃ³digo
- **Dev Backend**: ImplementaÃ§Ã£o dos models, views e lÃ³gica de negÃ³cio
- **Dev Frontend**: Templates, formulÃ¡rios e dashboard
- **QA**: Testes e validaÃ§Ã£o

### NegÃ³cio
- **Gestor Financeiro**: ValidaÃ§Ã£o de requisitos e UAT
- **Tesoureiro**: Testes e feedback
- **Pastor/LÃ­der**: AprovaÃ§Ã£o final

---

## ðŸ“… Cronograma Detalhado

### Semana 1 (10/02 - 14/02) - Segunda a Sexta

**Segunda-feira (10/02)**:
- ReuniÃ£o de kick-off da sprint
- Setup do ambiente de desenvolvimento
- RevisÃ£o e refinamento dos models financeiros
- Levantamento de dÃºvidas com o gestor financeiro

**TerÃ§a-feira (11/02)**:
- CriaÃ§Ã£o/actualizaÃ§Ã£o de forms e validaÃ§Ãµes
- ImplementaÃ§Ã£o de views para bancos e contas bancÃ¡rias
- Testes unitÃ¡rios dos models

**Quarta-feira (12/02)**:
- ImplementaÃ§Ã£o de views para entradas de caixa
- ImplementaÃ§Ã£o de views para saÃ­das de caixa
- CriaÃ§Ã£o de templates para movimentaÃ§Ãµes de caixa

**Quinta-feira (13/02)**:
- ImplementaÃ§Ã£o de views para entradas bancÃ¡rias
- ImplementaÃ§Ã£o de views para saÃ­das bancÃ¡rias
- CriaÃ§Ã£o de templates para movimentaÃ§Ãµes bancÃ¡rias
- Testes unitÃ¡rios

**Sexta-feira (14/02)**:
- ImplementaÃ§Ã£o de dÃ­zimos e ofertas
- VinculaÃ§Ã£o com entradas bancÃ¡rias/caixa
- Code review da semana
- Ajustes e correcÃ§Ãµes

### Semana 2 (17/02 - 21/02) - Segunda a Sexta

**Segunda-feira (17/02)**:
- ImplementaÃ§Ã£o de orÃ§amento departamental
- ImplementaÃ§Ã£o de pedidos de saÃ­da
- Workflow de aprovaÃ§Ã£o

**TerÃ§a-feira (18/02)**:
- ImplementaÃ§Ã£o de relatÃ³rios financeiros
- GeraÃ§Ã£o de PDFs (fluxo de caixa, movimentaÃ§Ãµes)
- Dashboard financeiro (grÃ¡ficos)

**Quarta-feira (19/02)**:
- Testes de integraÃ§Ã£o completos
- CorrecÃ§Ã£o de bugs identificados
- DocumentaÃ§Ã£o tÃ©cnica
- PreparaÃ§Ã£o do manual do utilizador

**Quinta-feira (20/02)**:
- UAT (User Acceptance Testing) com departamento de finanÃ§as
- Ajustes finais baseados no feedback
- Deploy em ambiente de homologaÃ§Ã£o
- Treinamento da equipa de finanÃ§as

**Sexta-feira (21/02)**:
- Deploy em produÃ§Ã£o (manhÃ£)
- VerificaÃ§Ã£o de integridade dos dados
- Treinamento final e entrega
- Monitoramento activo durante o dia
- ReuniÃ£o de encerramento da sprint

---

## ðŸ› Riscos e MitigaÃ§Ã£o

| Risco | Probabilidade | Impacto | MitigaÃ§Ã£o |
| ------- | --------------- | --------- | ----------- |
| InconsistÃªncia de dados na migraÃ§Ã£o | MÃ©dia | Alto | ValidaÃ§Ã£o rigorosa, scripts de verificaÃ§Ã£o, backup completo |
| Bugs em produÃ§Ã£o | MÃ©dia | Alto | Testes extensivos, perÃ­odo de homologaÃ§Ã£o, rollback preparado |
| ResistÃªncia dos utilizadores | Baixa | MÃ©dio | Treinamento adequado, suporte dedicado, interface intuitiva |
| Performance inadequada | Baixa | MÃ©dio | Testes de carga, optimizaÃ§Ã£o de queries, Ã­ndices adequados |
| Falha de seguranÃ§a | Baixa | CrÃ­tico | Code review, testes de seguranÃ§a, permissÃµes rigorosas |

---

## ðŸ“‹ Checklist Final de LanÃ§amento

### TÃ©cnico
- [ ] Todos os testes passando (unitÃ¡rios e integraÃ§Ã£o)
- [ ] Code review completo
- [ ] DocumentaÃ§Ã£o tÃ©cnica actualizada
- [ ] Logs configurados
- [ ] Monitoramento activo
- [ ] Backup automÃ¡tico funcionando
- [ ] SSL/HTTPS configurado
- [ ] Performance validada

### Funcional
- [ ] Todas as funcionalidades testadas
- [ ] UAT aprovado
- [ ] RelatÃ³rios conferidos
- [ ] Dashboard validado
- [ ] Fluxos de aprovaÃ§Ã£o testados

### Operacional
- [ ] Manual do utilizador entregue
- [ ] Treinamento concluÃ­do
- [ ] Suporte escalado
- [ ] Plano de contingÃªncia preparado
- [ ] ComunicaÃ§Ã£o aos utilizadores feita

---

## ðŸ“ž Contactos de Suporte

**Suporte TÃ©cnico**: [email/telefone]  
**Gestor do Projecto**: [email/telefone]  
**EmergÃªncias**: [telefone horÃ¡rio comercial]

---

## ðŸ“ Notas Adicionais

Este documento serÃ¡ actualizado conforme o progresso da sprint. Todas as alteraÃ§Ãµes devem ser comunicadas Ã  equipa.

**Ãšltima actualizaÃ§Ã£o**: 07 de Fevereiro de 2026 (SÃ¡bado - ReuniÃ£o de Planeamento)



*"Cada um contribua segundo propÃ´s no seu coraÃ§Ã£o, nÃ£o com tristeza ou por necessidade; porque Deus ama ao que dÃ¡ com alegria." - 2 CorÃ­ntios 9:7*
