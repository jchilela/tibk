## Descrição
<!-- Breve descrição das alterações implementadas -->

## Tipo de Mudança
<!-- Marque as opções relevantes -->
- [ ] 🎉 Nova funcionalidade (feature)
- [ ] 🐛 Correção de bug (fix)
- [ ] 🔨 Refatoração (refactor)
- [ ] 📚 Documentação (docs)
- [ ] ✅ Testes (test)
- [ ] 🔧 Manutenção (chore)
- [ ] ⚡ Performance (perf)
- [ ] 🔥 Hotfix

## Motivação e Contexto
<!-- Por que essa mudança é necessária? Qual problema resolve? -->

Refs: #issue-number <!-- Se aplicável -->

## Como foi testado?
<!-- Descreva os testes realizados -->

- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Testes manuais
- [ ] Testado em ambiente de desenvolvimento
- [ ] Testado em ambiente de staging

### Cenários testados:
1. 
2. 
3. 

## Screenshots / GIFs
<!-- Cole screenshots ou GIFs das mudanças visuais (se aplicável) -->

## Checklist de Código
<!-- Marque todos os itens que foram realizados -->

- [ ] Código segue os padrões do projeto
- [ ] Comentários foram adicionados em código complexo
- [ ] Documentação foi atualizada (README, REQUISITOS, etc.)
- [ ] Não há warnings ou erros de lint
- [ ] Testes foram adicionados/atualizados
- [ ] Todos os testes estão passando
- [ ] Migrações foram criadas e testadas (se aplicável)
- [ ] requirements.txt foi atualizado (se novas dependências)
- [ ] Arquivos de configuração atualizados (se necessário)

## Checklist de Review
<!-- Para o revisor marcar -->

- [ ] Código revisado e aprovado
- [ ] Lógica está correta
- [ ] Não há problemas de segurança
- [ ] Performance está adequada
- [ ] Testes são suficientes
- [ ] Documentação está clara

## Impacto e Considerações

- [ ] ⚠️ Breaking change (mudança que quebra compatibilidade)
- [ ] 🗃️ Requer migração de dados
- [ ] 📖 Requer atualização de documentação
- [ ] 🚀 Requer deploy especial
- [ ] 🔐 Mudanças relacionadas à segurança
- [ ] 📊 Impacto em performance

### Notas sobre o impacto:
<!-- Descreva qualquer impacto especial ou considerações de deploy -->

## Dependências
<!-- Esta PR depende de outras PRs? Liste aqui -->

- Depende de: #PR_NUMBER

## Checklist de Deploy
<!-- Se aplicável, lista de passos para deploy -->

- [ ] Executar migrações: `python manage.py migrate`
- [ ] Atualizar dependências: `pip install -r requirements.txt`
- [ ] Coletar estáticos: `python manage.py collectstatic`
- [ ] Reiniciar Celery workers
- [ ] Reiniciar servidor web
- [ ] Verificar logs após deploy

## Informações Adicionais
<!-- Qualquer outra informação relevante para os revisores -->

---

### Para o Autor:
- Certifique-se de que todos os checkboxes relevantes foram marcados
- Responda todos os comentários dos revisores
- Mantenha a branch atualizada com `main`

### Para o Revisor:
- Faça checkout da branch localmente para testar
- Verifique se os testes passam
- Deixe comentários construtivos
- Aprove ou solicite mudanças
