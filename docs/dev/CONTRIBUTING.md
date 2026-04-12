# Guia de ContribuiÃ§Ã£o - Sistema TIBL

Obrigado por considerar contribuir para o Sistema TIBL! Este documento fornece diretrizes para contribuir com o projeto.

## ðŸ“‹ Ãndice

- [CÃ³digo de Conduta](#cÃ³digo-de-conduta)
- [Como Posso Contribuir?](#como-posso-contribuir)
- [Workflow de Desenvolvimento](#workflow-de-desenvolvimento)
- [PadrÃµes de CÃ³digo](#padrÃµes-de-cÃ³digo)
- [PadrÃµes de Commit](#padrÃµes-de-commit)
- [Processo de Pull Request](#processo-de-pull-request)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Melhorias](#sugerindo-melhorias)

## ðŸ“œ CÃ³digo de Conduta

### Nossa Promessa

No interesse de promover um ambiente aberto e acolhedor, nÃ³s, como contribuidores e mantenedores, nos comprometemos a tornar a participaÃ§Ã£o em nosso projeto e em nossa comunidade uma experiÃªncia livre de assÃ©dio para todos.

### Nossos PadrÃµes

Exemplos de comportamento que contribuem para criar um ambiente positivo incluem:

- âœ… Usar linguagem acolhedora e inclusiva
- âœ… Respeitar pontos de vista e experiÃªncias diferentes
- âœ… Aceitar crÃ­ticas construtivas com elegÃ¢ncia
- âœ… Focar no que Ã© melhor para a comunidade
- âœ… Mostrar empatia com outros membros da comunidade

Exemplos de comportamento inaceitÃ¡vel incluem:

- âŒ Uso de linguagem ou imagens sexualizadas
- âŒ ComentÃ¡rios insultuosos/depreciativos e ataques pessoais ou polÃ­ticos
- âŒ AssÃ©dio pÃºblico ou privado
- âŒ Publicar informaÃ§Ãµes privadas de outros sem permissÃ£o explÃ­cita
- âŒ Outras condutas que possam ser consideradas inadequadas em ambiente profissional

## ðŸ¤ Como Posso Contribuir?

### Tipos de ContribuiÃ§Ã£o

1. **Reportar Bugs** ðŸ›
   - Use o template de bug report
   - ForneÃ§a informaÃ§Ãµes detalhadas
   - Inclua passos para reproduzir

2. **Sugerir Funcionalidades** ðŸ’¡
   - Use o template de feature request
   - Explique o problema que resolve
   - Descreva a soluÃ§Ã£o proposta

3. **Corrigir Bugs** ðŸ”§
   - Procure issues com label `bug`
   - Comente na issue antes de comeÃ§ar
   - Siga o workflow de desenvolvimento

4. **Implementar Funcionalidades** âœ¨
   - Procure issues com label `feature`
   - Discuta a implementaÃ§Ã£o antes de comeÃ§ar
   - Siga os padrÃµes do projeto

5. **Melhorar DocumentaÃ§Ã£o** ðŸ“š
   - Corrigir erros de digitaÃ§Ã£o
   - Adicionar exemplos
   - Esclarecer informaÃ§Ãµes confusas

6. **Escrever Testes** ðŸ§ª
   - Aumentar cobertura de testes
   - Adicionar testes para casos edge
   - Melhorar testes existentes

## ðŸ”„ Workflow de Desenvolvimento

Para detalhes completos, consulte [GITHUB_FLOW.md](GITHUB_FLOW.md)

### Resumo RÃ¡pido:

```bash
# 1. Fork e clone o repositÃ³rio
git clone https://github.com/seu-usuario/tibk.git
cd tibk

# 2. Configure o ambiente
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Crie uma branch
git checkout -b tipo/descricao-curta

# 4. FaÃ§a suas alteraÃ§Ãµes
# ... editar cÃ³digo ...

# 5. Execute os testes
python manage.py test

# 6. Commit suas mudanÃ§as
git add .
git commit -m "tipo: descriÃ§Ã£o da mudanÃ§a"

# 7. Push para seu fork
git push origin tipo/descricao-curta

# 8. Abra um Pull Request
```

## ðŸ’» PadrÃµes de CÃ³digo

### Python/Django

- **PEP 8**: Seguir guia de estilo Python
- **Linha mÃ¡xima**: 100 caracteres
- **Imports**: Organizados e ordenados
  ```python
  # 1. Imports padrÃ£o do Python
  import os
  import sys
  
  # 2. Imports de terceiros
  from django.db import models
  from django.shortcuts import render
  
  # 3. Imports do projeto
  from sitetibl.models import Irmao
  ```

- **Docstrings**: Para funÃ§Ãµes e classes complexas
  ```python
  def funcao_complexa(param1, param2):
      """
      DescriÃ§Ã£o breve da funÃ§Ã£o.
      
      Args:
          param1 (tipo): DescriÃ§Ã£o do parÃ¢metro
          param2 (tipo): DescriÃ§Ã£o do parÃ¢metro
          
      Returns:
          tipo: DescriÃ§Ã£o do retorno
      """
      pass
  ```

- **Nomes descritivos**:
  ```python
  # âœ… Bom
  total_dizimos = calcular_total_dizimos(mes, ano)
  
  # âŒ Ruim
  t = calc(m, a)
  ```

### Django EspecÃ­fico

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

### FormataÃ§Ã£o

Use `black` para formataÃ§Ã£o automÃ¡tica:

```bash
pip install black
black sitetibl/
```

Use `flake8` para linting:

```bash
pip install flake8
flake8 sitetibl/
```

## ðŸ“ PadrÃµes de Commit

Seguimos **Conventional Commits**:

### Formato:

```
tipo(escopo opcional): descriÃ§Ã£o curta

DescriÃ§Ã£o detalhada (opcional)

Refs: #issue-number (opcional)
```

### Tipos:

| Tipo | DescriÃ§Ã£o | Exemplo |
| ------ | ----------- | --------- |
| `feat` | Nova funcionalidade | `feat: adiciona relatÃ³rio de presenÃ§a` |
| `fix` | CorreÃ§Ã£o de bug | `fix: corrige validaÃ§Ã£o de telefone` |
| `docs` | DocumentaÃ§Ã£o | `docs: atualiza README com instalaÃ§Ã£o` |
| `style` | FormataÃ§Ã£o | `style: formata cÃ³digo com black` |
| `refactor` | RefatoraÃ§Ã£o | `refactor: simplifica query de dashboard` |
| `test` | Testes | `test: adiciona testes para modelo Irmao` |
| `chore` | ManutenÃ§Ã£o | `chore: atualiza dependÃªncias` |
| `perf` | Performance | `perf: otimiza query com select_related` |

### Exemplos:

```bash
# Feature simples
git commit -m "feat: adiciona filtro de busca por cÃ©lula"

# Fix com escopo
git commit -m "fix(auth): corrige redirecionamento apÃ³s login"

# Com descriÃ§Ã£o detalhada
git commit -m "refactor: extrai lÃ³gica de relatÃ³rios

Extrai a geraÃ§Ã£o de PDFs para classes separadas
para melhorar reusabilidade e testabilidade.

Refs: #123"
```

### Regras:

- âœ… Use verbo no presente: "adiciona" nÃ£o "adicionado"
- âœ… Primeira letra minÃºscula
- âœ… Sem ponto final na descriÃ§Ã£o curta
- âœ… DescriÃ§Ã£o curta com no mÃ¡ximo 72 caracteres
- âœ… DescriÃ§Ã£o detalhada separada por linha em branco

## ðŸ” Processo de Pull Request

### Antes de Criar o PR:

- [ ] CÃ³digo testado localmente
- [ ] Testes unitÃ¡rios passando
- [ ] Sem erros de lint
- [ ] DocumentaÃ§Ã£o atualizada
- [ ] Branch atualizada com `main`
- [ ] Commits bem organizados

### Criando o PR:

1. **Use o template**: Preencha todas as seÃ§Ãµes
2. **TÃ­tulo descritivo**: Use formato de commit
3. **DescriÃ§Ã£o clara**: Explique o que, por que e como
4. **Screenshots**: Inclua se houver mudanÃ§as visuais
5. **Marque labels**: bug, feature, docs, etc.
6. **Link issues**: Refs #issue-number
7. **Marque revisores**: @username

### Durante a RevisÃ£o:

- âœ… Responda comentÃ¡rios prontamente
- âœ… Seja receptivo a feedback
- âœ… FaÃ§a alteraÃ§Ãµes solicitadas
- âœ… Marque conversas como resolvidas
- âœ… Mantenha PR atualizado com `main`

### ApÃ³s AprovaÃ§Ã£o:

- âœ… Squash and merge (recomendado)
- âœ… Delete a branch
- âœ… Feche issues relacionadas

## ðŸ› Reportando Bugs

### Antes de Reportar:

- [ ] Verifique se jÃ¡ nÃ£o existe issue similar
- [ ] Teste na Ãºltima versÃ£o disponÃ­vel
- [ ] Tente reproduzir em ambiente limpo
- [ ] Colete logs e informaÃ§Ãµes relevantes

### Ao Reportar:

Use o [template de bug report](../.github/ISSUE_TEMPLATE/bug_report.md) e inclua:

1. **DescriÃ§Ã£o clara** do problema
2. **Passos para reproduzir** detalhados
3. **Comportamento esperado** vs atual
4. **Screenshots** se aplicÃ¡vel
5. **Ambiente** (OS, browser, versÃµes)
6. **Logs de erro** relevantes

### Prioridade:

- ðŸ”¥ **CrÃ­tico**: Sistema nÃ£o funciona
- âš ï¸ **Alto**: Funcionalidade principal quebrada
- ðŸ”¶ **MÃ©dio**: Funcionalidade secundÃ¡ria afetada
- ðŸŸ¡ **Baixo**: Problema cosmÃ©tico

## ðŸ’¡ Sugerindo Melhorias

### Antes de Sugerir:

- [ ] Verifique se jÃ¡ nÃ£o existe issue similar
- [ ] Considere se alinha com objetivos do projeto
- [ ] Pense em alternativas
- [ ] Avalie impacto e complexidade

### Ao Sugerir:

Use o [template de feature request](../.github/ISSUE_TEMPLATE/feature_request.md) e inclua:

1. **DescriÃ§Ã£o clara** da funcionalidade
2. **Problema que resolve**
3. **SoluÃ§Ã£o proposta** detalhada
4. **Alternativas consideradas**
5. **Mockups/referÃªncias** se aplicÃ¡vel
6. **Contexto adicional**

## ðŸ“Š MÃ©tricas de Qualidade

### Code Coverage

Mantemos cobertura mÃ­nima de **80%** para:
- Models
- Forms
- Views principais
- LÃ³gica de negÃ³cio

### Performance

- Queries: MÃ¡ximo de 50ms
- Views: MÃ¡ximo de 500ms
- APIs: MÃ¡ximo de 200ms

### DocumentaÃ§Ã£o

- Toda feature deve ter documentaÃ§Ã£o
- Toda API deve ter especificaÃ§Ã£o
- Todo modelo complexo deve ter docstring

## ðŸŽ“ Recursos para Aprendizado

### Django
- [DocumentaÃ§Ã£o oficial Django](https://docs.djangoproject.com/)
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

## ðŸ† Reconhecimento

Contribuidores que fazem contribuiÃ§Ãµes significativas serÃ£o:

- Listados no README
- Mencionados em releases
- Reconhecidos publicamente
- Adicionados ao CONTRIBUTORS.md

## â“ DÃºvidas?

- **GitHub Issues**: Para dÃºvidas tÃ©cnicas
- **Email**: tiblbaptista7@gmail.com
- **Pull Request**: Para discussÃµes de cÃ³digo

## ðŸ“œ Checklist de ContribuiÃ§Ã£o

Antes de submeter sua contribuiÃ§Ã£o:

### CÃ³digo
- [ ] CÃ³digo segue PEP 8 e padrÃµes do projeto
- [ ] CÃ³digo foi formatado com `black`
- [ ] Nenhum warning de `flake8`
- [ ] Nomes sÃ£o descritivos e claros
- [ ] ComentÃ¡rios adicionados onde necessÃ¡rio
- [ ] Sem cÃ³digo comentado ou debug prints

### Testes
- [ ] Testes unitÃ¡rios adicionados/atualizados
- [ ] Todos os testes passam
- [ ] Cobertura mantida ou melhorada
- [ ] Casos edge foram considerados

### DocumentaÃ§Ã£o
- [ ] README atualizado (se necessÃ¡rio)
- [ ] REQUISITOS.md atualizado (se nova feature)
- [ ] DOCUMENTACAO_TECNICA.md atualizada (se mudanÃ§a arquitetural)
- [ ] Docstrings adicionadas para cÃ³digo complexo
- [ ] ComentÃ¡rios inline onde necessÃ¡rio

### Django EspecÃ­fico
- [ ] Migrations criadas e testadas
- [ ] Models seguem convenÃ§Ãµes
- [ ] Views sÃ£o eficientes (select_related/prefetch_related)
- [ ] Templates nÃ£o tÃªm lÃ³gica complexa
- [ ] Forms tÃªm validaÃ§Ãµes adequadas
- [ ] URLs seguem padrÃµes do projeto

### SeguranÃ§a
- [ ] Inputs sÃ£o validados
- [ ] Queries sÃ£o parametrizadas (ORM)
- [ ] NÃ£o hÃ¡ dados sensÃ­veis hardcoded
- [ ] CSRF protection mantida
- [ ] PermissÃµes verificadas

### Git
- [ ] Commits seguem Conventional Commits
- [ ] Branch tem nome descritivo
- [ ] Branch estÃ¡ atualizada com `main`
- [ ] Sem conflitos

### Pull Request
- [ ] Template preenchido completamente
- [ ] TÃ­tulo Ã© descritivo
- [ ] Screenshots incluÃ­dos (se aplicÃ¡vel)
- [ ] Issues relacionadas linkadas
- [ ] Revisores marcados
- [ ] Labels apropriadas adicionadas

---

**Obrigado por contribuir com o Sistema TIBL!** ðŸ™

Suas contribuiÃ§Ãµes ajudam a melhorar a gestÃ£o da Terceira Igreja Baptista de Luanda e servir melhor a comunidade.
