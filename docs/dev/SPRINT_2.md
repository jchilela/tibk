# SPRINT 2 — Permissões, Perfil de Utilizador, Dark Mode & Actividades

**Branch:** `feature/user-permissions`  
**Período:** Março 2026

---

## Contexto

Sprint de consolidação que completa a arquitectura de permissões iniciada na Fase 15 e adiciona funcionalidades à gestão de actividades e escalas.

---

## 1. Guardas de Permissão CRUD nos Templates (Fase 15)

**Ficheiros:** todos os templates em `templates/`

Todos os botões Criar/Editar/Eliminar em ~40 templates guardados com:
```django
{% if perms.sitetibl.add_<modelo> %}...{% endif %}
{% if perms.sitetibl.change_<modelo> %}...{% endif %}
{% if perms.sitetibl.delete_<modelo> %}...{% endif %}
```
Afecta: barra lateral, cabeçalhos de listagem, páginas de detalhe, listagens inline, botão "Escalar Irmãos".

---

## 2. Visibilidade de Menu — Correcção de Grupos (Seeder)

**Ficheiro:** `sitetibl/management/commands/seed_base_data.py`

**Problema:** "Relatório Células" e "Conteúdo Ensino" apareciam para Membro Geral e Membros Baptizados.

**Correcção:**
- Membros Baptizados: removido `view_conteudoensino`; `relatoriosemanalcelula` reduzido a `add` + `view` → **9 permissões**
- Membro Geral: removido `view_conteudoensino` → **3 permissões**

---

## 3. Relatório de Irmãos PDF — Guarda Elevada

**Ficheiros:** `templates/relatorios/template_relatorio.html`, `sitetibl/views.py`

Guarda alterado de `view_irmao` → `change_irmao` (apenas Secretaria/Admin/Pastor).

---

## 4. Página "Meu Perfil"

| Ficheiro | Alteração |
|---|---|
| `sitetibl/forms.py` | `MeuPerfilForm` + `MeuPerfilPasswordForm` com labels PT |
| `sitetibl/views.py` | Vista `meu_perfil` com dispatch POST (perfil/senha) |
| `templates/meu_perfil.html` | Template com banner, formulário de contactos, senha, info read-only |
| `sitetibl/urls.py` | `path('meu-perfil/', views.meu_perfil, name='meu_perfil')` |
| `templates/base_modern.html` | Avatar envolto em link para `meu_perfil` |

**Campos editáveis:** foto, telefone, whatsapp, email  
**Campos read-only:** nome, apelido, data de nascimento, sexo, estado civil, célula, congregação

---

## 5. Barra de Pesquisa Removida do Topbar

**Ficheiro:** `templates/base_modern.html` — remoção do `<div class="topbar-search">`, `margin-left: auto` em `.user-info`.

---

## 6. Dark Mode — Correcção de Contraste

**Ficheiro:** `static/estilos/modern.css`

Bloco `[data-theme="dark"]` adicionado com overrides para todos os componentes com cores `white`/pastel hardcoded:

| Componente | Problema | Correcção |
|---|---|---|
| `.stat-card` | `background: white` | `var(--bg-card)` |
| `.modern-table-container` | `background: white` | `var(--bg-card)` |
| `.badge-*` (6 variantes) | Fundos pastéis claros | Semi-transparentes com texto vibrante |
| `.detail-field` / `.detail-actions` | Bordas `#f5f8fa` invisíveis | `rgba(255,255,255,0.07)` |
| `.confirm-dialog` | `background: white` | `var(--bg-card)` |
| `.alert-*` (4 variantes) | Pastéis claros com texto escuro | Fundos tinted escuros |
| `.login-card` / `.landing-hero` | White / gradiente claro | Dark card / gradiente escuro |
| `.filter-bar` | `background: white` | `var(--bg-card)` |
| `.modern-pagination a` | `background: white` | `var(--bg-card)` |
| `tr[bgcolor="#548c2f"]` | `background: #f0f7f1` | `#0f172a` + texto `#a7f3d0` |
| `.report-page .report-toolbar` | Gradiente branco | `var(--bg-card)` |
| `.non-field-errors` | Fundo claro | Dark tinted red |

---

## 7. Gestão de Actividades, Escalas e Mandatos

### 7.1 Permissões de Mandato — Líder e Vice-Líder de Departamento

**Ficheiro:** `sitetibl/management/commands/seed_base_data.py`

- Líder de Departamento: `mandato` de `crud` → `['add', 'view']` (sem `change`/`delete`)
- Vice-Líder de Departamento: idem
- Total de permissões: Líder 35 → Vice-Líder 24 (reduzidas 2 cada)
- Botões editar/eliminar mandatos já guardados por `{% if perms.sitetibl.change_mandato %}` nas Fase 15

### 7.2 Novos Campos no Modelo `Actividade`

**Ficheiro:** `sitetibl/models.py`, `sitetibl/migrations/0082_actividade_criado_por_departamento.py`

```python
criado_por = ForeignKey(User, null=True, blank=True, on_delete=SET_NULL, related_name='actividades_criadas')
departamento = ForeignKey(Departamento, null=True, blank=True, on_delete=SET_NULL, related_name='actividades')
```

### 7.3 Propriedade de Actividades (Ownership)

**Ficheiro:** `sitetibl/views.py` (`mostraActualizacao`, `mostraEliminacao`)

Líder/Vice-Líder só podem editar/eliminar actividades que criaram. Proxy de "papel elevado": `change_mandato` (Admin/Pastor/Secretaria).

Regras:
- `criado_por == request.user` → pode editar
- `criado_por is None` (actividade legada) → só papel elevado pode editar  
- `has_perm('sitetibl.change_mandato')` → papel elevado, pode editar qualquer

### 7.4 Detecção de Conflitos

**Ficheiro:** `sitetibl/views.py` (`mostraCriacao`, `mostraActualizacao`)

- Actividades com horário sobreponível no mesmo dia → **erro** (bloqueia)
- Actividades no mesmo dia com horários diferentes → **aviso** ("Se for num local diferente, pode prosseguir")

### 7.5 Actividades Recorrentes

**Ficheiros:** `sitetibl/forms.py`, `sitetibl/views.py`, `sitetibl/urls.py`, `templates/actividades_recorrentes.html`

Novo formulário com checkboxes de dias-da-semana. Vista gera N actividades por loop de datas (sem novo modelo).

URL: `actividades/recorrentes/`

### 7.6 Filtro por Departamento nas Escalas

**Ficheiros:** `sitetibl/views.py` (`encontraEscalas`), `templates/escalas.html`, `templates/escalasfiltrados.html`

- Dropdown de departamento adicionado ao formulário de filtro de escalas
- Query filter: `actividade__departamento_id`

---

## Grupos de Permissão (estado final)

| Grupo | Total Perms |
|---|---|
| Administrador | 176 (todas) |
| Pastor | 58 |
| Financeiro | 45 |
| Secretaria | 60 |
| Líder de Departamento | 35 |
| Vice-Líder de Departamento | 24 |
| Líder de Célula | 9 |
| Membros Baptizados | 9 |
| Membro Geral | 3 |

---

## Verificação (Checklist)

- [ ] `seed_base_data` → LD sem `change_mandato`/`delete_mandato`
- [ ] LD tenta editar mandato alheio → bloqueado por perm
- [ ] URL directa `/mandatos/actualizar/1/` como LD → "Acesso negado"
- [ ] LD edita actividade que não criou → "Só pode editar actividades que criou"
- [ ] Criar actividade com horário sobreponível → erro imediato
- [ ] Criar no mesmo dia, horário diferente → aviso mas guarda
- [ ] Formulário recorrente: Domingo + Quarta, 3 semanas → 6 actividades criadas
- [ ] Filtrar escalas por departamento → mostra apenas as desse dept

---

## 8. Restrições de Líder de Departamento (LD/VLD)

### 8.1 Gestão de Membros Restrita ao Próprio Departamento

**Ficheiro:** `sitetibl/views.py` (`mostraDetalhe` — `departamentos`)

- `pode_gerir_membros` agora exige: ser líder/vice do departamento **ou** ter `change_mandato` (papel elevado).
- LD/VLD de outro departamento não consegue adicionar/remover membros.
- Verificação usa `Departamento.lider_departamento_id` e `vice_lider_departamento_id`.

### 8.2 Propriedade de Actividades por Departamento

**Ficheiro:** `sitetibl/views.py` (`mostraActualizacao`, `mostraEliminacao`)

LD/VLD pode editar/eliminar actividades se:
1. `criado_por == request.user`, **ou**
2. Lidera o departamento associado à actividade (via `Departamento.lider_departamento`/`vice_lider_departamento`).

### 8.3 Departamento Não Editável pelo LD

**Ficheiro:** `sitetibl/management/commands/seed_base_data.py`

- LD perdeu `change_departamento` → só pode `view_departamento`.
- Impede que LD altere o nome/descrição do departamento; só gere membros e funções.

### 8.4 Cargos Exclusivos nos Mandatos

**Ficheiro:** `sitetibl/models.py` (`Mandato.save()`)

Funções exclusivas (apenas 1 por departamento): `lider`, `vice_lider`, `secretario`, `tesoureiro`, `coordenador`.

Ao atribuir um cargo exclusivo já ocupado:
- O ocupante anterior é automaticamente rebaixado a **Membro**.
- Mensagem de aviso: *"Fulano deixou de ser Líder e voltou a ser Membro."*

---

## 9. Funções de Escalas por Departamento

### 9.1 Modelo `Funcao` — Campo `departamento`

**Ficheiro:** `sitetibl/models.py`, `sitetibl/migrations/0083_funcao_departamento.py`

```python
departamento = ForeignKey('Departamento', null=True, blank=True, on_delete=SET_NULL, related_name='funcoes')
```
- `departamento=None` → função genérica (disponível para todos).
- `departamento=X` → função específica desse departamento.

### 9.2 Gestão de Funções no Detalhe do Departamento

**Ficheiro:** `sitetibl/views.py` (`mostraDetalhe` — `departamentos`), `templates/departamentosdetalhado.html`

Secção "Funções do Departamento" com:
- Lista de funções em chips/pills com botão remover.
- Protecção: não remove funções em uso por escalas.
- Formulário inline para adicionar novas funções.
- Permissão: LD/VLD do departamento ou quem tenha `add_funcao`.

### 9.3 API Cascading: Actividade → Função

**Ficheiros:** `sitetibl/views.py` (`api_funcoes_por_actividade`), `sitetibl/urls.py`, `templates/formulario_criacao.html`

Endpoint: `GET /tibl/api/funcoes-actividade/<id>/`
- Retorna funções do departamento da actividade **+** funções genéricas.
- Dropdown de função no formulário de criação de escalas actualiza-se via AJAX ao seleccionar actividade.

### 9.4 Permissões de Funções no Seeder

**Ficheiro:** `sitetibl/management/commands/seed_base_data.py`

| Grupo | Permissões `funcao` |
|---|---|
| Líder de Departamento | `add`, `change`, `delete`, `view` |
| Vice-Líder de Departamento | `add`, `view` |

---

## 10. Clarificação Terminológica: Cargo vs Função

### Problema
O termo "Função" era usado para dois conceitos distintos, causando confusão na UI:

| Antes | Contexto | Exemplo |
|---|---|---|
| Função (Mandato) | Papel organizativo no departamento | Líder, Vice-Líder, Membro |
| Função (Funcao) | Papel nas escalas/actividades | Pregador, Louvor, Som |

### Solução

| Conceito | Termo na UI | Modelo | Exemplo |
|---|---|---|---|
| Papel no departamento | **Cargo** | `Mandato.funcao` | Líder, Vice-Líder, Secretário, Membro |
| Papel nas escalas | **Função** | `Funcao` (modelo) | Pregador, Louvor, Técnico de Som |

**Ficheiros alterados:**
- `sitetibl/models.py` — verbose_name `'Função'` → `'Cargo'`
- `templates/departamentosdetalhado.html` — cabeçalho tabela e label → "Cargo"
- `templates/departamentos.html` — filtro de pesquisa → "Cargo"
- `templates/mandatos.html` — cabeçalho tabela → "Cargo"
- `templates/mandatosdetalhado.html` — detalhe → "Cargo"
- `templates/departamentosfiltrados.html` — cabeçalho → "Cargo" + correcção exibição (valor bruto → `cargo_display`)

---

## 11. Sincronização de Liderança (Mandato ↔ Departamento)

### Problema
`Departamento.lider_departamento` (FK) e `Mandato.funcao='lider'` podiam apontar para pessoas diferentes, levando a inconsistências entre a listagem de departamentos e os mandatos.

### Solução — Mandato como fonte única de verdade

| Mecanismo | Ficheiro | Descrição |
|---|---|---|
| `Mandato.save()` | `sitetibl/models.py` | Ao gravar mandato com cargo `lider`/`vice_lider`, actualiza o FK do Departamento. Ao alterar para outro cargo, limpa o FK. |
| `post_delete` signal | `sitetibl/signals.py` | Ao apagar mandato de líder/vice, limpa o FK correspondente. |
| Comando `sync_lideranca` | `sitetibl/management/commands/sync_lideranca.py` | Comando de manutenção: `python manage.py sync_lideranca` — percorre todos os departamentos e corrige FKs com base nos mandatos existentes. |

---

## Grupos de Permissão (estado final actualizado)

| Grupo | Total Perms |
|---|---|
| Administrador | 176 (todas) |
| Pastor | 58 |
| Secretaria | 60 |
| Financeiro | 45 |
| Líder de Departamento | 29 |
| Vice-Líder de Departamento | 24 |
| Líder de Célula | 9 |
| Membros Baptizados | 9 |
| Membro Geral | 3 |

---

## Verificação (Checklist actualizado)

- [ ] `seed_base_data` → LD sem `change_departamento`, com `funcao` crud
- [ ] LD tenta editar mandato alheio → bloqueado por perm
- [ ] URL directa `/mandatos/actualizar/1/` como LD → "Acesso negado"
- [ ] LD edita actividade que não criou e não é do seu dept → bloqueado
- [ ] LD edita actividade do seu departamento → permitido
- [ ] Criar actividade com horário sobreponível → erro imediato
- [ ] Criar no mesmo dia, horário diferente → aviso mas guarda
- [ ] Formulário recorrente: Domingo + Quarta, 3 semanas → 6 actividades criadas
- [ ] Filtrar escalas por departamento → mostra apenas as desse dept
- [ ] LD adiciona membro noutro departamento → bloqueado
- [ ] Atribuir cargo "Líder" a novo membro → antigo líder rebaixado a Membro
- [ ] Adicionar função ao departamento → aparece nas chips
- [ ] Remover função em uso por escala → aviso e bloqueio
- [ ] Criar escala: seleccionar actividade → dropdown funções filtra por dept
- [ ] Templates mostram "Cargo" (mandato) e "Função" (escalas) sem confusão
- [ ] Mandatos Executivos e Departamentos mostram mesmo líder
- [ ] `python manage.py sync_lideranca` → corrige inconsistências
