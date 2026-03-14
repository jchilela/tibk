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
