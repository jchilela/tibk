# GitHub Flow - Sistema TIBL

## 1. Visão Geral do Workflow

Este documento descreve o fluxo de trabalho GitHub Flow que será utilizado para todas as contribuições no projeto TIBL (Terceira Igreja Baptista de Luanda). O GitHub Flow é um modelo de branching leve, baseado em branches e pull requests.

## 2. Princípios do GitHub Flow

1. **Branch `main` **: A branch principal deve estar sempre em estado estável e pronta para produção
2. **Branches descritivas**: Criar branches com nomes claros que descrevem a funcionalidade
3. **Commits frequentes**: Fazer commits pequenos e frequentes com mensagens descritivas
4. **Pull Requests para colaboração**: Usar PRs para discussão e revisão de código
5. **Deploy após merge**: Código mergeado na `main` deve ser enviado para produção

## 3. Estrutura de Branches

### 3.1 Branch Principal

- **`main`**: Branch de produção
  - Sempre estável e testada
  - Código deployado em produção vem desta branch
  - Protegida contra pushes diretos
  - Requer aprovação de PR antes de merge

### 3.2 Branches de Desenvolvimento

Todas as branches de desenvolvimento seguem o padrão: `tipo/descrição-curta`

#### Tipos de Branch:

- **`feature/`**: Nova funcionalidade
  - Exemplo: `feature/relatorio-presenca`
  - Exemplo: `feature/portal-membro`

- **`fix/`**: Correção de bug
  - Exemplo: `fix/validacao-telefone`
  - Exemplo: `fix/calculo-dizimo`

- **`hotfix/`**: Correção urgente em produção
  - Exemplo: `hotfix/erro-login`
  - Exemplo: `hotfix/quebra-relatorio-pdf`

- **`refactor/`**: Refatoração de código
  - Exemplo: `refactor/views-genericas`
  - Exemplo: `refactor/models-financeiro`

- **`docs/`**: Documentação
  - Exemplo: `docs/api-endpoints`
  - Exemplo: `docs/guia-instalacao`

- **`test/`**: Adição ou correção de testes
  - Exemplo: `test/models-irmao`
  - Exemplo: `test/integracao-celery`

- **`chore/`**: Tarefas de manutenção
  - Exemplo: `chore/atualizar-dependencias`
  - Exemplo: `chore/configurar-ci`

## 4. Workflow Detalhado

### 4.1 Início de Nova Funcionalidade

```bash
# 1. Garantir que está na branch main atualizada
git checkout main
git pull origin main

# 2. Criar nova branch a partir da main
git checkout -b feature/nome-da-funcionalidade

# Exemplos:
git checkout -b feature/gestao-presenca
git checkout -b fix/erro-upload-foto
git checkout -b refactor/otimizar-queries
```

### 4.2 Desenvolvimento

```bash
# 3. Fazer alterações no código
# ... editar arquivos ...

# 4. Adicionar arquivos modificados
git add .
# OU adicionar arquivos específicos
git add sitetibl/models.py sitetibl/views.py

# 5. Fazer commit com mensagem descritiva
git commit -m "feat: adiciona modelo de presença em atividades"

# 6. Fazer commits frequentes durante o desenvolvimento
git commit -m "feat: adiciona form de presença"
git commit -m "feat: adiciona view de registro de presença"
git commit -m "test: adiciona testes para presença"
```

### 4.3 Padrão de Mensagens de Commit

Seguir o padrão **Conventional Commits**:

```
tipo(escopo opcional): descrição curta

Descrição detalhada (opcional)

Refs: #issue-number (opcional)
```

#### Tipos de Commit:

- **feat**: Nova funcionalidade
  ```
  feat: adiciona relatório de presença em PDF
  feat(dashboard): adiciona gráfico de crescimento anual
  ```

- **fix**: Correção de bug
  ```
  fix: corrige validação de telefone para aceitar +244
  fix(celery): corrige envio duplicado de notificações
  ```

- **docs**: Documentação
  ```
  docs: atualiza README com instruções de instalação
  docs(api): documenta endpoints de dashboard
  ```

- **style**: Formatação (sem mudança de lógica)
  ```
  style: formata código com black
  style: corrige indentação em views.py
  ```

- **refactor**: Refatoração
  ```
  refactor: extrai lógica de relatórios para classe separada
  refactor(models): simplifica relacionamentos de financeiro
  ```

- **test**: Testes
  ```
  test: adiciona testes unitários para modelo Irmao
  test(views): adiciona testes de integração para CRUD
  ```

- **chore**: Manutenção
  ```
  chore: atualiza Django para 4.2.10
  chore: adiciona pré-commit hooks
  ```

- **perf**: Performance
  ```
  perf: adiciona índices em tabelas de movimentação
  perf: otimiza query de dashboard com select_related
  ```

### 4.4 Push para Repositório Remoto

```bash
# 7. Enviar branch para o GitHub
git push origin feature/nome-da-funcionalidade

# Primeira vez (criar branch remota)
git push -u origin feature/nome-da-funcionalidade

# Pushes subsequentes
git push
```

### 4.5 Criar Pull Request

1. **No GitHub**:
   - Acesse o repositório
   - Clique em "Compare & pull request" (aparece automaticamente após push)
   - OU vá em "Pull requests" → "New pull request"

2. **Preencher o PR Template**:

```markdown
## Descrição
Breve descrição das alterações implementadas.

## Tipo de Mudança
- [ ] Nova funcionalidade (feature)
- [ ] Correção de bug (fix)
- [ ] Refatoração (refactor)
- [ ] Documentação (docs)
- [ ] Outro (descrever)

## Motivação e Contexto
Por que essa mudança é necessária? Qual problema resolve?

Refs: #issue-number (se aplicável)

## Como foi testado?
Descreva os testes realizados:
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Testes manuais
- [ ] Testado em ambiente de desenvolvimento

## Screenshots (se aplicável)
Cole screenshots ou GIFs das mudanças visuais.

## Checklist
- [ ] Código segue os padrões do projeto
- [ ] Comentários foram adicionados em código complexo
- [ ] Documentação foi atualizada
- [ ] Não há warnings ou erros de lint
- [ ] Testes foram adicionados/atualizados
- [ ] Todas as dependências foram atualizadas em requirements.txt
- [ ] Migrações foram criadas (se aplicável)
- [ ] README foi atualizado (se necessário)

## Impacto
- [ ] Breaking change (mudança que quebra compatibilidade)
- [ ] Requer migração de dados
- [ ] Requer atualização de documentação
```

### 4.6 Revisão de Código

#### Para o Revisor:

1. **Verificar funcionalidade**:
   - O código faz o que deveria?
   - Há casos edge não tratados?

2. **Verificar qualidade**:
   - Código é legível e mantível?
   - Segue os padrões do projeto?
   - Há duplicação desnecessária?

3. **Verificar segurança**:
   - Há vulnerabilidades?
   - Dados sensíveis estão protegidos?
   - Inputs são validados?

4. **Verificar performance**:
   - Queries estão otimizadas?
   - Há N+1 queries?
   - Cache está sendo usado adequadamente?

5. **Verificar testes**:
   - Há testes suficientes?
   - Casos críticos estão cobertos?

6. **Deixar comentários**:
   ```
   Comentário geral: "Ótimo trabalho! Apenas algumas sugestões."
   
   Comentário inline: "Considere usar select_related aqui para otimizar."
   
   Bloqueante: "Esta validação está faltando, precisa ser adicionada."
   ```

7. **Aprovar ou Solicitar Mudanças**:
   - **Approve**: Se tudo está OK
   - **Request Changes**: Se há problemas que precisam ser resolvidos
   - **Comment**: Se tem sugestões mas não bloqueia o merge

#### Para o Autor:

1. **Responder comentários**:
   - Agradecer feedback
   - Explicar decisões de design
   - Fazer as correções solicitadas

2. **Fazer alterações**:
   ```bash
   # Fazer correções
   git add .
   git commit -m "fix: corrige validação conforme revisão"
   git push
   ```

3. **Resolver conversas**:
   - Marcar conversas como resolvidas após implementar mudanças

### 4.7 Merge do Pull Request

Após aprovação:

1. **Verificar Checklist**:
   - [ ] PR aprovado por pelo menos 1 revisor
   - [ ] Todos os checks CI/CD passaram
   - [ ] Não há conflitos com a branch main
   - [ ] Documentação atualizada
   - [ ] Testes passando

2. **Escolher Estratégia de Merge**:

   - **Squash and Merge** (Recomendado para features):
     - Combina todos os commits em um único commit limpo
     - Mantém histórico da main limpo e linear
     ```
     feat: adiciona gestão de presença (#42)
     ```

   - **Rebase and Merge**:
     - Mantém commits individuais mas reaplica sobre main
     - Use quando histórico de commits é importante

   - **Merge Commit** (Evitar):
     - Cria commit de merge adicional
     - Pode poluir histórico

3. **Executar Merge**:
   - Clicar em "Squash and merge" no GitHub
   - Editar mensagem de commit se necessário
   - Confirmar merge

4. **Deletar Branch**:
   - GitHub oferece opção automática após merge
   - Manter repositório limpo

### 4.8 Pós-Merge

```bash
# 8. Atualizar branch local main
git checkout main
git pull origin main

# 9. Deletar branch local (se ainda não deletada)
git branch -d feature/nome-da-funcionalidade

# 10. Se necessário, deployar para produção
# (seguir procedimentos de deploy do projeto)
```

## 5. Workflow para Hotfixes

Hotfixes são correções urgentes que precisam ir para produção rapidamente.

```bash
# 1. Criar branch de hotfix a partir da main
git checkout main
git pull origin main
git checkout -b hotfix/descricao-problema

# 2. Fazer correção
# ... editar código ...

# 3. Testar localmente
python manage.py test

# 4. Commit e push
git add .
git commit -m "hotfix: corrige erro crítico em login"
git push -u origin hotfix/descricao-problema

# 5. Criar PR com label "hotfix" e "priority: high"

# 6. Revisão expedita (pode ser mais rápida)

# 7. Merge imediato após aprovação

# 8. Deploy imediato para produção
```

## 6. Sincronização com Main

Manter branch atualizada com main durante desenvolvimento:

```bash
# Opção 1: Merge (mais simples)
git checkout feature/minha-branch
git merge main

# Opção 2: Rebase (histórico mais limpo)
git checkout feature/minha-branch
git rebase main

# Se houver conflitos, resolver e continuar
git add .
git rebase --continue

# Forçar push se já tinha feito push anterior
git push --force-with-lease
```

## 7. Resolução de Conflitos

```bash
# 1. Atualizar main
git checkout main
git pull origin main

# 2. Voltar para sua branch
git checkout feature/minha-branch

# 3. Merge ou rebase com main
git merge main
# OU
git rebase main

# 4. Resolver conflitos nos arquivos
# Git marca conflitos assim:
<<<<<<< HEAD
Seu código
=======
Código da main
>>>>>>> main

# 5. Após resolver, adicionar arquivos
git add arquivo-resolvido.py

# 6. Continuar merge/rebase
git merge --continue
# OU
git rebase --continue

# 7. Push das mudanças
git push
# OU (se usou rebase)
git push --force-with-lease
```

## 8. Boas Práticas

### 8.1 Branches

- ✅ Criar branch para cada funcionalidade/correção
- ✅ Usar nomes descritivos (feature/gestao-presenca)
- ✅ Manter branches curtas e focadas
- ✅ Deletar branches após merge
- ❌ Não fazer push direto para main
- ❌ Não manter branches por muito tempo sem merge
- ❌ Não trabalhar em múltiplas features na mesma branch

### 8.2 Commits

- ✅ Commits pequenos e frequentes
- ✅ Mensagens claras e descritivas
- ✅ Usar Conventional Commits
- ✅ Um commit = uma mudança lógica
- ❌ Não fazer commits gigantes
- ❌ Não usar mensagens vagas ("fix", "update")
- ❌ Não commitar código comentado ou debugs

### 8.3 Pull Requests

- ✅ PR deve ser focado em uma feature/correção
- ✅ Descrição detalhada do que foi feito
- ✅ Incluir screenshots se houver mudanças visuais
- ✅ Referenciar issues relacionadas
- ✅ Marcar revisores apropriados
- ✅ Responder todos os comentários
- ❌ Não criar PRs enormes (500+ linhas)
- ❌ Não fazer merge sem aprovação
- ❌ Não ignorar comentários de revisão

### 8.4 Code Review

- ✅ Revisar código cuidadosamente
- ✅ Ser construtivo nos comentários
- ✅ Sugerir melhorias, não apenas criticar
- ✅ Aprovar rapidamente se tudo está OK
- ✅ Testar localmente se possível
- ❌ Não ser excessivamente crítico
- ❌ Não aprovar sem realmente revisar
- ❌ Não demorar dias para revisar

## 9. Configurações do Repositório

### 9.1 Proteção da Branch Main

Configurar no GitHub (Settings → Branches → Branch protection rules):

- [x] Require pull request reviews before merging
  - [x] Required approving reviews: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
- [x] Require status checks to pass before merging
  - [x] Require branches to be up to date before merging
- [x] Require conversation resolution before merging
- [x] Include administrators
- [x] Restrict who can push to matching branches

### 9.2 Labels para PRs e Issues

Criar labels no GitHub (Settings → Labels):

**Tipo:**
- `feature` (🎉 verde) - Nova funcionalidade
- `bug` (🐛 vermelho) - Algo não está funcionando
- `hotfix` (🔥 laranja) - Correção urgente
- `refactor` (🔨 azul claro) - Refatoração de código
- `docs` (📚 azul) - Documentação
- `test` (🧪 roxo) - Testes

**Prioridade:**
- `priority: high` (⚠️ vermelho) - Alta prioridade
- `priority: medium` (⚡ amarelo) - Média prioridade
- `priority: low` (🔽 verde claro) - Baixa prioridade

**Status:**
- `in progress` (🔄 amarelo) - Em desenvolvimento
- `ready for review` (👀 verde) - Pronto para revisão
- `changes requested` (🔧 laranja) - Mudanças solicitadas
- `approved` (✅ verde escuro) - Aprovado

**Área:**
- `frontend` - Interface do usuário
- `backend` - Lógica do servidor
- `database` - Banco de dados
- `api` - Endpoints API
- `security` - Segurança
- `performance` - Performance

### 9.3 Templates

Criar templates no repositório:

**`.github/pull_request_template.md`**: (já incluído na seção 4.5)

**`.github/ISSUE_TEMPLATE/bug_report.md`**:
```markdown
---
name: Bug Report
about: Reportar um problema
title: '[BUG] '
labels: bug
assignees: ''
---

## Descrição do Bug
Descrição clara do problema.

## Passos para Reproduzir
1. Vá para '...'
2. Clique em '...'
3. Role até '...'
4. Veja o erro

## Comportamento Esperado
O que deveria acontecer.

## Comportamento Atual
O que está acontecendo.

## Screenshots
Se aplicável, adicione screenshots.

## Ambiente
- OS: [ex: macOS 12.0]
- Browser: [ex: Chrome 98]
- Versão Django: [ex: 4.2.5]

## Informações Adicionais
Qualquer outra informação relevante.
```

**`.github/ISSUE_TEMPLATE/feature_request.md`**:
```markdown
---
name: Feature Request
about: Sugerir nova funcionalidade
title: '[FEATURE] '
labels: feature
assignees: ''
---

## Descrição da Funcionalidade
Descrição clara da funcionalidade desejada.

## Problema que Resolve
Qual problema esta funcionalidade resolve?

## Solução Proposta
Descrição detalhada de como deveria funcionar.

## Alternativas Consideradas
Outras soluções que foram consideradas.

## Contexto Adicional
Screenshots, mockups, referências, etc.
```

## 10. CI/CD (Integração Contínua)

### 10.1 GitHub Actions Workflow

Criar `.github/workflows/django.yml`:

```yaml
name: Django CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: tibldb_test
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: --health-cmd="redis-cli ping" --health-interval=10s --health-timeout=5s --health-retries=3
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run migrations
      env:
        DB_HOST: 127.0.0.1
        DB_PORT: 3306
        DB_NAME: tibldb_test
        DB_USER: root
        DB_PASSWORD: root
      run: |
        python manage.py migrate
    
    - name: Run tests
      env:
        DB_HOST: 127.0.0.1
        DB_PORT: 3306
        DB_NAME: tibldb_test
        DB_USER: root
        DB_PASSWORD: root
      run: |
        python manage.py test
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## 11. Comandos Git Úteis

```bash
# Ver status atual
git status

# Ver histórico de commits
git log --oneline --graph --all

# Ver diferenças não commitadas
git diff

# Ver diferenças de arquivo específico
git diff sitetibl/models.py

# Desfazer mudanças locais (não commitadas)
git checkout -- arquivo.py

# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Desfazer último commit (descarta mudanças)
git reset --hard HEAD~1

# Stash (guardar mudanças temporariamente)
git stash
git stash pop

# Ver branches remotas
git branch -r

# Limpar branches locais deletadas remotamente
git fetch --prune

# Ver quem modificou cada linha
git blame arquivo.py

# Buscar por texto nos commits
git log --grep="termo de busca"
```

## 12. Fluxo Completo - Exemplo Prático

```bash
# EXEMPLO: Adicionar funcionalidade de gestão de presença

# 1. Atualizar main
git checkout main
git pull origin main

# 2. Criar branch
git checkout -b feature/gestao-presenca

# 3. Criar modelo
# Editar: sitetibl/models.py
# Adicionar classe Presenca

# 4. Commit do modelo
git add sitetibl/models.py
git commit -m "feat(models): adiciona modelo Presenca"

# 5. Criar migração
python manage.py makemigrations
git add sitetibl/migrations/
git commit -m "chore: adiciona migração para modelo Presenca"

# 6. Criar form
# Editar: sitetibl/forms.py
git add sitetibl/forms.py
git commit -m "feat(forms): adiciona PresencaForm"

# 7. Criar view
# Editar: sitetibl/views.py
git add sitetibl/views.py
git commit -m "feat(views): adiciona views para gestão de presença"

# 8. Criar template
# Criar: templates/presencas
git add templates/presencas
git commit -m "feat(templates): adiciona templates de presença"

# 9. Adicionar URL
# Editar: tibl/urls.py
git add tibl/urls.py
git commit -m "feat(urls): adiciona rotas de presença"

# 10. Adicionar testes
# Editar: sitetibl/tests.py
git add sitetibl/tests.py
git commit -m "test: adiciona testes para modelo Presenca"

# 11. Atualizar documentação
# Editar: REQUISITOS.md
git add REQUISITOS.md
git commit -m "docs: atualiza requisitos com gestão de presença"

# 12. Push da branch
git push -u origin feature/gestao-presenca

# 13. Criar PR no GitHub
# - Adicionar descrição detalhada
# - Adicionar screenshots
# - Marcar revisores
# - Adicionar labels: feature, backend

# 14. Aguardar revisão e fazer correções se necessário

# 15. Após aprovação e merge, limpar
git checkout main
git pull origin main
git branch -d feature/gestao-presenca
```

## 13. Checklist de Contribuição

Antes de criar PR, verificar:

- [ ] Branch criada a partir da main atualizada
- [ ] Nome da branch segue padrão (tipo/descrição)
- [ ] Commits seguem Conventional Commits
- [ ] Código testado localmente
- [ ] Testes unitários adicionados/atualizados
- [ ] Testes passando (`python manage.py test`)
- [ ] Sem erros de lint/formatação
- [ ] Migrações criadas (se houver mudanças em models)
- [ ] Documentação atualizada (se necessário)
- [ ] requirements.txt atualizado (se novas dependências)
- [ ] Código comentado onde necessário
- [ ] Sem código comentado/debug no commit
- [ ] Sem arquivos desnecessários (*.pyc, __pycache__, etc)

---

## Contatos e Suporte

- **Dúvidas sobre o workflow**: Abrir issue com label `question`
- **Problemas com Git**: Consultar colega ou documentação oficial
- **Revisão de código**: Marcar @reviewers no PR

---

**Última atualização**: Fevereiro 2026
