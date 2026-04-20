# Plano: Módulo de Solicitações Interdepartamentais

## Problema
A comunicação entre departamentos da igreja é feita de forma informal (WhatsApp, e-mail, verbal), sem rastreabilidade. É necessário um módulo centralizado onde líderes de departamento possam criar pedidos formais a outros departamentos, com ciclo de vida definido e auditoria completa.

## Abordagem
Seguir os padrões existentes do projecto (FBV, CRUD genérico via `mostraGestao`/`mostraDetalhe`, DTL templates, signals para notificações), usando como referência o modelo `PedidoSaida` que já implementa um fluxo de aprovação com estados.

---

## Modelo de Dados

### `SolicitacaoInterdepartamental`
| Campo | Tipo | Descrição |
|---|---|---|
| `departamento_solicitante` | FK(Departamento) | Departamento que faz o pedido |
| `departamento_destinatario` | FK(Departamento) | Departamento que recebe o pedido |
| `solicitante` | FK(Irmao) | Quem criou a solicitação |
| `assunto` | CharField(200) | Resumo breve do pedido |
| `descricao` | TextField | Detalhes completos da solicitação |
| `categoria` | CharField(choices) | Tipo: material_criativo, equipamento, verba, cobertura_evento, apoio_logistico, outro |
| `data_necessidade` | DateField | Data limite desejada |
| `prioridade` | CharField(choices) | baixa, normal, alta, urgente |
| `documento_anexo` | FileField(blank) | Ficheiro de suporte opcional |
| `estado` | CharField(choices) | pendente → em_analise → aprovado/rejeitado → concluido |
| `responsavel_resposta` | FK(Irmao, null) | Quem respondeu pela parte destinatária |
| `justificacao_resposta` | TextField(blank) | Motivo de aprovação/rejeição |
| `data_resposta` | DateTimeField(null) | Quando foi aprovado/rejeitado |
| `data_conclusao` | DateTimeField(null) | Quando foi marcado como concluído |
| `data_criacao` | DateTimeField(auto_now_add) | Timestamp de criação |
| `data_atualizacao` | DateTimeField(auto_now) | Timestamp de última alteração |

### `HistoricoSolicitacao`
| Campo | Tipo | Descrição |
|---|---|---|
| `solicitacao` | FK(SolicitacaoInterdepartamental) | Referência à solicitação |
| `estado_anterior` | CharField | Estado antes da mudança |
| `estado_novo` | CharField | Estado após a mudança |
| `responsavel` | FK(Irmao) | Quem fez a alteração |
| `observacao` | TextField(blank) | Comentário opcional |
| `data` | DateTimeField(auto_now_add) | Quando ocorreu |

### `NotificacaoSistema` (modelo genérico reutilizável)
| Campo | Tipo | Descrição |
|---|---|---|
| `destinatario` | FK(User) | Utilizador que recebe a notificação |
| `titulo` | CharField(200) | Título breve |
| `mensagem` | TextField | Corpo da notificação |
| `lida` | BooleanField(default=False) | Se já foi visualizada |
| `url` | CharField(blank) | Link para a entidade relacionada |
| `data_criacao` | DateTimeField(auto_now_add) | Timestamp |

---

## Ciclo de Vida (Estados)

```
pendente → em_analise → aprovado → concluido
                      → rejeitado
```

- **pendente**: Criada pelo solicitante, aguarda acção do destinatário
- **em_analise**: Destinatário acusou recepção, está a avaliar
- **aprovado**: Destinatário aceitou, trabalho em curso
- **rejeitado**: Destinatário recusou, com justificação obrigatória
- **concluido**: Trabalho entregue, solicitação fechada

---

## Todos

### 1. Modelo e Migração (`model-migration`)
- Criar `SolicitacaoInterdepartamental`, `HistoricoSolicitacao` e `NotificacaoSistema` em `models.py`
- Gerar e aplicar migração

### 2. Formulários (`forms`)
- `SolicitacaoForm` para criação (campos: dept_destinatario, assunto, descricao, categoria, data_necessidade, prioridade, documento_anexo)
- `RespostaSolicitacaoForm` para aprovação/rejeição (campos: justificacao_resposta)

### 3. Views — CRUD + Acções de Estado (`views`)
- Integrar no CRUD genérico (`mostraGestao`, `mostraDetalhe`, `mostraCriacao`, `mostraActualizacao`)
- View dedicada para acções de estado: `aprovar_solicitacao`, `rejeitar_solicitacao`, `concluir_solicitacao`
- Filtros por estado, departamento solicitante/destinatário
- Lógica: dept_solicitante auto-preenchido com base no Mandato do user; validação que solicitante ≠ destinatário

### 4. URLs (`urls`)
- Registar no CRUD genérico via `gestaoescolhida = 'solicitacoes'`
- Rotas adicionais: `solicitacoes/<id>/aprovar/`, `solicitacoes/<id>/rejeitar/`, `solicitacoes/<id>/concluir/`
- Rota de busca: `buscasolicitacoes/`

### 5. Templates (`templates`)
- `solicitacoes.html` — listagem com tabs por estado (padrão PedidoSaida)
- `solicitacoesdetalhado.html` — detalhe com timeline de histórico + botões de acção
- `solicitacoesfiltradas.html` — resultados de busca
- Integrar no formulário genérico `formulario_criacao.html` / `formulario_actualizacao.html`

### 6. Notificações In-App (`notifications`)
- Signal `post_save` em `SolicitacaoInterdepartamental` para criar `NotificacaoSistema` em mudanças de estado
- Context processor ou middleware para injectar contagem de não-lidas no `base_modern.html`
- Badge/ícone de sino na barra superior com dropdown de notificações
- Marcar como lida ao clicar

### 7. Menu Lateral (`sidebar`)
- Adicionar entrada "Solicitações" no `base_modern.html` com ícone `fa-exchange-alt`
- Proteger com `perms.sitetibl.view_solicitacaointerdepartamental`
- Badge com contagem de pendentes para o departamento do user

### 8. Permissões e Seeder (`permissions`)
- Actualizar `seed_base_data.py` → `_assign_group_permissions()` com as novas permissões
- Grupos com acesso: Administrador (todas), Líder de Departamento (CRUD), Vice-Líder (CRUD), Pastor (view), Secretaria (view)

### 9. Admin (`admin`)
- Registar os 3 novos modelos no `admin.py`

### 10. Testes Manuais e Validação (`validation`)
- Verificar tag balance em todos os templates novos
- Testar ciclo completo: criar → em_análise → aprovar → concluir
- Testar rejeição com justificação
- Verificar notificações criadas em cada transição
- Confirmar permissões por grupo

---

## Notas
- Não existe modelo `Notificacao` no sistema actual — será criado como componente genérico reutilizável
- O padrão de referência mais próximo é `PedidoSaida` (estados, aprovação, signals)
- O dept_solicitante será determinado automaticamente pelo Mandato activo do utilizador (líder/vice-líder)
- Autorização nas views via `has_perm()`, nos templates via `perms.sitetibl.*`
- `has_group` usado apenas para badges de display, nunca para autorização
