# Guia de Contribuição - Sistema TIBL

Obrigado por considerar contribuir para o Sistema TIBL! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Posso Contribuir?](#como-posso-contribuir)
- [Workflow de Desenvolvimento](#workflow-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Padrões de Commit](#padrões-de-commit)
- [Processo de Pull Request](#processo-de-pull-request)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Melhorias](#sugerindo-melhorias)

## 📜 Código de Conduta

### Nossa Promessa

No interesse de promover um ambiente aberto e acolhedor, nós, como contribuidores e mantenedores, nos comprometemos a tornar a participação em nosso projeto e em nossa comunidade uma experiência livre de assédio para todos.

### Nossos Padrões

Exemplos de comportamento que contribuem para criar um ambiente positivo incluem:

- ✅ Usar linguagem acolhedora e inclusiva
- ✅ Respeitar pontos de vista e experiências diferentes
- ✅ Aceitar críticas construtivas com elegância
- ✅ Focar no que é melhor para a comunidade
- ✅ Mostrar empatia com outros membros da comunidade

Exemplos de comportamento inaceitável incluem:

- ❌ Uso de linguagem ou imagens sexualizadas
- ❌ Comentários insultuosos/depreciativos e ataques pessoais ou políticos
- ❌ Assédio público ou privado
- ❌ Publicar informações privadas de outros sem permissão explícita
- ❌ Outras condutas que possam ser consideradas inadequadas em ambiente profissional

## 🤝 Como Posso Contribuir?

### Tipos de Contribuição

1. **Reportar Bugs** 🐛
   - Use o template de bug report
   - Forneça informações detalhadas
   - Inclua passos para reproduzir

2. **Sugerir Funcionalidades** 💡
   - Use o template de feature request
   - Explique o problema que resolve
   - Descreva a solução proposta

3. **Corrigir Bugs** 🔧
   - Procure issues com label `bug`
   - Comente na issue antes de começar
   - Siga o workflow de desenvolvimento

4. **Implementar Funcionalidades** ✨
   - Procure issues com label `feature`
   - Discuta a implementação antes de começar
   - Siga os padrões do projeto

5. **Melhorar Documentação** 📚
   - Corrigir erros de digitação
   - Adicionar exemplos
   - Esclarecer informações confusas

6. **Escrever Testes** 🧪
   - Aumentar cobertura de testes
   - Adicionar testes para casos edge
   - Melhorar testes existentes

## 🔄 Workflow de Desenvolvimento

Para detalhes completos, consulte [GITHUB_FLOW.md](GITHUB_FLOW.md)

### Resumo Rápido:

```bash
# 1. Fork e clone o repositório
git clone https://github.com/seu-usuario/tibk.git
cd tibk

# 2. Configure o ambiente
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Crie uma branch
git checkout -b tipo/descricao-curta

# 4. Faça suas alterações
# ... editar código ...

# 5. Execute os testes
python manage.py test

# 6. Commit suas mudanças
git add .
git commit -m "tipo: descrição da mudança"

# 7. Push para seu fork
git push origin tipo/descricao-curta

# 8. Abra um Pull Request
```

## 💻 Padrões de Código

### Python/Django

- **PEP 8**: Seguir guia de estilo Python
- **Linha máxima**: 100 caracteres
- **Imports**: Organizados e ordenados
  ```python
  # 1. Imports padrão do Python
  import os
  import sys
  
  # 2. Imports de terceiros
  from django.db import models
  from django.shortcuts import render
  
  # 3. Imports do projeto
  from sitetibl.models import Irmao
  ```

- **Docstrings**: Para funções e classes complexas
  ```python
  def funcao_complexa(param1, param2):
      """
      Descrição breve da função.
      
      Args:
          param1 (tipo): Descrição do parâmetro
          param2 (tipo): Descrição do parâmetro
          
      Returns:
          tipo: Descrição do retorno
      """
      pass
  ```

- **Nomes descritivos**:
  ```python
  # ✅ Bom
  total_dizimos = calcular_total_dizimos(mes, ano)
  
  # ❌ Ruim
  t = calc(m, a)
  ```

### Django Específico

- **Models**: Nome no singular, CamelCase
  ```python
  class Irmao(models.Model):
      pass
  ```

- **Views**: Nome descritivo, snake_case
  ```python
  def mostra_detalhe_irmao(request, id):
      pass
  ```

- **Templates**: Nome descritivo, snake_case
  ```
  irmaos_listagem.html
  irmao_detalhado.html
  ```

- **URLs**: Kebab-case
  ```python
  path('irmaos/detalhe/<int:id>/', mostra_detalhe_irmao)
  ```

### Formatação

Use `black` para formatação automática:

```bash
pip install black
black sitetibl/
```

Use `flake8` para linting:

```bash
pip install flake8
flake8 sitetibl/
```

## 📝 Padrões de Commit

Seguimos **Conventional Commits**:

### Formato:

```
tipo(escopo opcional): descrição curta

Descrição detalhada (opcional)

Refs: #issue-number (opcional)
```

### Tipos:

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat: adiciona relatório de presença` |
| `fix` | Correção de bug | `fix: corrige validação de telefone` |
| `docs` | Documentação | `docs: atualiza README com instalação` |
| `style` | Formatação | `style: formata código com black` |
| `refactor` | Refatoração | `refactor: simplifica query de dashboard` |
| `test` | Testes | `test: adiciona testes para modelo Irmao` |
| `chore` | Manutenção | `chore: atualiza dependências` |
| `perf` | Performance | `perf: otimiza query com select_related` |

### Exemplos:

```bash
# Feature simples
git commit -m "feat: adiciona filtro de busca por célula"

# Fix com escopo
git commit -m "fix(auth): corrige redirecionamento após login"

# Com descrição detalhada
git commit -m "refactor: extrai lógica de relatórios

Extrai a geração de PDFs para classes separadas
para melhorar reusabilidade e testabilidade.

Refs: #123"
```

### Regras:

- ✅ Use verbo no presente: "adiciona" não "adicionado"
- ✅ Primeira letra minúscula
- ✅ Sem ponto final na descrição curta
- ✅ Descrição curta com no máximo 72 caracteres
- ✅ Descrição detalhada separada por linha em branco

## 🔍 Processo de Pull Request

### Antes de Criar o PR:

- [ ] Código testado localmente
- [ ] Testes unitários passando
- [ ] Sem erros de lint
- [ ] Documentação atualizada
- [ ] Branch atualizada com `main`
- [ ] Commits bem organizados

### Criando o PR:

1. **Use o template**: Preencha todas as seções
2. **Título descritivo**: Use formato de commit
3. **Descrição clara**: Explique o que, por que e como
4. **Screenshots**: Inclua se houver mudanças visuais
5. **Marque labels**: bug, feature, docs, etc.
6. **Link issues**: Refs #issue-number
7. **Marque revisores**: @username

### Durante a Revisão:

- ✅ Responda comentários prontamente
- ✅ Seja receptivo a feedback
- ✅ Faça alterações solicitadas
- ✅ Marque conversas como resolvidas
- ✅ Mantenha PR atualizado com `main`

### Após Aprovação:

- ✅ Squash and merge (recomendado)
- ✅ Delete a branch
- ✅ Feche issues relacionadas

## 🐛 Reportando Bugs

### Antes de Reportar:

- [ ] Verifique se já não existe issue similar
- [ ] Teste na última versão disponível
- [ ] Tente reproduzir em ambiente limpo
- [ ] Colete logs e informações relevantes

### Ao Reportar:

Use o [template de bug report](../.github/ISSUE_TEMPLATE/bug_report.md) e inclua:

1. **Descrição clara** do problema
2. **Passos para reproduzir** detalhados
3. **Comportamento esperado** vs atual
4. **Screenshots** se aplicável
5. **Ambiente** (OS, browser, versões)
6. **Logs de erro** relevantes

### Prioridade:

- 🔥 **Crítico**: Sistema não funciona
- ⚠️ **Alto**: Funcionalidade principal quebrada
- 🔶 **Médio**: Funcionalidade secundária afetada
- 🟡 **Baixo**: Problema cosmético

## 💡 Sugerindo Melhorias

### Antes de Sugerir:

- [ ] Verifique se já não existe issue similar
- [ ] Considere se alinha com objetivos do projeto
- [ ] Pense em alternativas
- [ ] Avalie impacto e complexidade

### Ao Sugerir:

Use o [template de feature request](../.github/ISSUE_TEMPLATE/feature_request.md) e inclua:

1. **Descrição clara** da funcionalidade
2. **Problema que resolve**
3. **Solução proposta** detalhada
4. **Alternativas consideradas**
5. **Mockups/referências** se aplicável
6. **Contexto adicional**

## 📊 Métricas de Qualidade

### Code Coverage

Mantemos cobertura mínima de **80%** para:
- Models
- Forms
- Views principais
- Lógica de negócio

### Performance

- Queries: Máximo de 50ms
- Views: Máximo de 500ms
- APIs: Máximo de 200ms

### Documentação

- Toda feature deve ter documentação
- Toda API deve ter especificação
- Todo modelo complexo deve ter docstring

## 🎓 Recursos para Aprendizado

### Django
- [Documentação oficial Django](https://docs.djangoproject.com/)
- [Django Tutorial](https://docs.djangoproject.com/en/4.2/intro/tutorial01/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)

### Git/GitHub
- [Pro Git Book](https://git-scm.com/book/pt-br/v2)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Python
- [PEP 8](https://pep8.org/)
- [Python Guide](https://docs.python-guide.org/)
- [Real Python](https://realpython.com/)

## 🏆 Reconhecimento

Contribuidores que fazem contribuições significativas serão:

- Listados no README
- Mencionados em releases
- Reconhecidos publicamente
- Adicionados ao CONTRIBUTORS.md

## ❓ Dúvidas?

- **GitHub Issues**: Para dúvidas técnicas
- **Email**: tiblbaptista7@gmail.com
- **Pull Request**: Para discussões de código

## 📜 Checklist de Contribuição

Antes de submeter sua contribuição:

### Código
- [ ] Código segue PEP 8 e padrões do projeto
- [ ] Código foi formatado com `black`
- [ ] Nenhum warning de `flake8`
- [ ] Nomes são descritivos e claros
- [ ] Comentários adicionados onde necessário
- [ ] Sem código comentado ou debug prints

### Testes
- [ ] Testes unitários adicionados/atualizados
- [ ] Todos os testes passam
- [ ] Cobertura mantida ou melhorada
- [ ] Casos edge foram considerados

### Documentação
- [ ] README atualizado (se necessário)
- [ ] REQUISITOS.md atualizado (se nova feature)
- [ ] DOCUMENTACAO_TECNICA.md atualizada (se mudança arquitetural)
- [ ] Docstrings adicionadas para código complexo
- [ ] Comentários inline onde necessário

### Django Específico
- [ ] Migrations criadas e testadas
- [ ] Models seguem convenções
- [ ] Views são eficientes (select_related/prefetch_related)
- [ ] Templates não têm lógica complexa
- [ ] Forms têm validações adequadas
- [ ] URLs seguem padrões do projeto

### Segurança
- [ ] Inputs são validados
- [ ] Queries são parametrizadas (ORM)
- [ ] Não há dados sensíveis hardcoded
- [ ] CSRF protection mantida
- [ ] Permissões verificadas

### Git
- [ ] Commits seguem Conventional Commits
- [ ] Branch tem nome descritivo
- [ ] Branch está atualizada com `main`
- [ ] Sem conflitos

### Pull Request
- [ ] Template preenchido completamente
- [ ] Título é descritivo
- [ ] Screenshots incluídos (se aplicável)
- [ ] Issues relacionadas linkadas
- [ ] Revisores marcados
- [ ] Labels apropriadas adicionadas

---

**Obrigado por contribuir com o Sistema TIBL!** 🙏

Suas contribuições ajudam a melhorar a gestão da Terceira Igreja Baptista de Luanda e servir melhor a comunidade.
