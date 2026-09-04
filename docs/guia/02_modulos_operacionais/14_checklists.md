# Checklists de Actividades

As checklists permitem gerir tarefas de preparacao por departamento para cada actividade. Cada departamento pode ter a sua propria checklist com tarefas, responsaveis e prazos.

## Aceder ao dashboard de checklists

1. No menu lateral, na seccao **Actividades**, clique em **Checklists**.
2. O dashboard mostra, por departamento:
   - Actividades associadas
   - Total de tarefas, concluidas e pendentes
   - Tarefas atrasadas
   - Progresso de cada checklist (barra percentual)

> Nota: Os administradores veem todos os departamentos. Os lideres de departamento veem apenas os seus.

## Consultar uma checklist de actividade

1. Na pagina de detalhe de uma actividade, clique em **Checklist**.
2. A pagina mostra todas as checklists da actividade, agrupadas por departamento.
3. Para cada checklist ve-se:
   - Lista de tarefas com estado (pendente/concluida)
   - Responsavel por cada tarefa
   - Barra de progresso individual e geral

## Criar uma checklist para um departamento

1. Na pagina de checklist da actividade, se tem permissao de gestao, aparece o formulario **Nova Checklist**.
2. Seleccione o departamento.
3. Clique em **Criar Checklist**.
4. Apos criar, pode adicionar tarefas.

## Adicionar tarefas

1. Dentro de cada checklist (cartao por departamento), clique em **Adicionar tarefa**.
2. Introduza a descricao da tarefa.
3. Seleccione o responsavel (opcional).
4. Defina a ordem (opcional).
5. Clique em **Adicionar**.

## Marcar tarefas como concluidas

- Clique no checkbox ao lado da tarefa para alternar entre pendente e concluida.
- A actualizacao e instantanea (AJAX) e a barra de progresso actualiza automaticamente.

## Remover tarefas e checklists

- Para remover uma tarefa, clique no icone de lixo ao lado da tarefa (apenas gestores).
- Para remover uma checklist inteira, clique em **Remover Checklist** no cartao do departamento (apenas gestores).

## Configurar recorrencia

1. No cartao de cada checklist, clique em **Configurar Recorrencia** (apenas gestores).
2. Seleccione a frequencia: Unica, Diaria, Semanal ou Mensal.
3. Para semanal, escolha o dia da semana. Para mensal, escolha o dia do mes.
4. Defina a hora de notificacao.
5. Active ou desactive a notificacao automatica aos responsaveis.
6. Clique em **Guardar**.

> Nota: As notificacoes sao geradas automaticamente pelo sistema atraves de um comando agendado.

## Minhas Tarefas

1. No menu lateral, clique em **Minhas Tarefas**.
2. Veja todas as tarefas atribuidas a si, organizadas por:
   - Pendentes
   - Concluidas
   - Atrasadas
3. Pode marcar tarefas como concluidas diretamente nesta pagina.
4. O painel mostra estatisticas (total, pendentes, concluidas, atrasadas).

## Notificacoes de checklist

- O sino de notificacoes no canto superior direito mostra notificacoes de checklists nao lidas.
- Tipos de notificacao:
  - **Disponivel**: Checklist disponivel para preparacao.
  - **Atrasada**: Tarefa nao concluida apos a data da actividade.
  - **Proxima do prazo**: Tarefa pendente com actividade no dia seguinte.
- Clique no sino para ver todas as notificacoes.
- Pode marcar notificacoes individuais ou todas como lidas.

## Permissoes

| Perfil | Acesso |
| --- | --- |
| Administrador | Gere todas as checklists, tarefas e recorrencias |
| Lider/Vice-Lider de Departamento | Gere checklists do seu departamento |
| Membro | Ve e marca as suas proprias tarefas atribuidas |

[Voltar ao indice](../../GUIA_UTILIZADOR.md)
