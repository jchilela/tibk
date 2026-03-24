# SPRINT 2 â€” PermissÃµes, Perfil de Utilizador, Dark Mode & Actividades

**Branch:** `feature/user-permissions`  
**PerÃ­odo:** MarÃ§o 2026

---

## Contexto

Sprint de consolidaÃ§Ã£o que completa a arquitectura de permissÃµes iniciada na Fase 15 e adiciona funcionalidades Ã  gestÃ£o de actividades e escalas.

---

## 1. Guardas de PermissÃ£o CRUD nos Templates (Fase 15)

**Ficheiros:** todos os templates em `templates/`

Todos os botÃµes Criar/Editar/Eliminar em ~40 templates guardados com:
```django
{% if perms.sitetibl.add_<modelo> %}...{% endif %}
{% if perms.sitetibl.change_<modelo> %}...{% endif %}
{% if perms.sitetibl.delete_<modelo> %}...{% endif %}
```
Afecta: barra lateral, cabeÃ§alhos de listagem, pÃ¡ginas de detalhe, listagens inline, botÃ£o "Escalar IrmÃ£os".

---

## 2. Visibilidade de Menu â€” CorrecÃ§Ã£o de Grupos (Seeder)

**Ficheiro:** `sitetibl/management/commands/seed_base_data.py`

**Problema:** "RelatÃ³rio CÃ©lulas" e "ConteÃºdo Ensino" apareciam para Membro Geral e Membros Baptizados.

**CorrecÃ§Ã£o:**
- Membros Baptizados: removido `view_conteudoensino`; `relatoriosemanalcelula` reduzido a `add` + `view` â†’ **9 permissÃµes**
- Membro Geral: removido `view_conteudoensino` â†’ **3 permissÃµes**

---

## 3. RelatÃ³rio de IrmÃ£os PDF â€” Guarda Elevada

**Ficheiros:** `templates/relatorios/template_relatorio.html`, `sitetibl/views.py`

Guarda alterado de `view_irmao` â†’ `change_irmao` (apenas Secretaria/Admin/Pastor).

---

## 4. PÃ¡gina "Meu Perfil"

| Ficheiro | AlteraÃ§Ã£o |
| --- | --- |
| `sitetibl/forms.py` | `MeuPerfilForm` + `MeuPerfilPasswordForm` com labels PT |
| `sitetibl/views.py` | Vista `meu_perfil` com dispatch POST (perfil/senha) |
| `templates/meu_perfil.html` | Template com banner, formulÃ¡rio de contactos, senha, info read-only |
| `sitetibl/urls.py` | `path('meu-perfil/', views.meu_perfil, name='meu_perfil')` |
| `templates/base_modern.html` | Avatar envolto em link para `meu_perfil` |

**Campos editÃ¡veis:** foto, telefone, whatsapp, email  
**Campos read-only:** nome, apelido, data de nascimento, sexo, estado civil, cÃ©lula, congregaÃ§Ã£o

---

## 5. Barra de Pesquisa Removida do Topbar

**Ficheiro:** `templates/base_modern.html` â€” remoÃ§Ã£o do `<div class="topbar-search">`, `margin-left: auto` em `.user-info`.

---

## 6. Dark Mode â€” CorrecÃ§Ã£o de Contraste

**Ficheiro:** `static/estilos/modern.css`

Bloco `[data-theme="dark"]` adicionado com overrides para todos os componentes com cores `white`/pastel hardcoded:

| Componente | Problema | CorrecÃ§Ã£o |
| --- | --- | --- |
| `.stat-card` | `background: white` | `var(--bg-card)` |
| `.modern-table-container` | `background: white` | `var(--bg-card)` |
| `.badge-*` (6 variantes) | Fundos pastÃ©is claros | Semi-transparentes com texto vibrante |
| `.detail-field` / `.detail-actions` | Bordas `#f5f8fa` invisÃ­veis | `rgba(255,255,255,0.07)` |
| `.confirm-dialog` | `background: white` | `var(--bg-card)` |
| `.alert-*` (4 variantes) | PastÃ©is claros com texto escuro | Fundos tinted escuros |
| `.login-card` / `.landing-hero` | White / gradiente claro | Dark card / gradiente escuro |
| `.filter-bar` | `background: white` | `var(--bg-card)` |
| `.modern-pagination a` | `background: white` | `var(--bg-card)` |
| `tr[bgcolor="#548c2f"]` | `background: #f0f7f1` | `#0f172a` + texto `#a7f3d0` |
| `.report-page .report-toolbar` | Gradiente branco | `var(--bg-card)` |
| `.non-field-errors` | Fundo claro | Dark tinted red |

---

## 7. GestÃ£o de Actividades, Escalas e Mandatos

### 7.1 PermissÃµes de Mandato â€” LÃ­der e Vice-LÃ­der de Departamento

**Ficheiro:** `sitetibl/management/commands/seed_base_data.py`

- LÃ­der de Departamento: `mandato` de `crud` â†’ `['add', 'view']` (sem `change`/`delete`)
- Vice-LÃ­der de Departamento: idem
- Total de permissÃµes: LÃ­der 35 â†’ Vice-LÃ­der 24 (reduzidas 2 cada)
- BotÃµes editar/eliminar mandatos jÃ¡ guardados por `{% if perms.sitetibl.change_mandato %}` nas Fase 15

### 7.2 Novos Campos no Modelo `Actividade`

**Ficheiro:** `sitetibl/models.py`, `sitetibl/migrations/0082_actividade_criado_por_departamento.py`

```python
criado_por = ForeignKey(User, null=True, blank=True, on_delete=SET_NULL, related_name='actividades_criadas')
departamento = ForeignKey(Departamento, null=True, blank=True, on_delete=SET_NULL, related_name='actividades')
```

### 7.3 Propriedade de Actividades (Ownership)

**Ficheiro:** `sitetibl/views.py` (`mostraActualizacao`, `mostraEliminacao`)

LÃ­der/Vice-LÃ­der sÃ³ podem editar/eliminar actividades que criaram. Proxy de "papel elevado": `change_mandato` (Admin/Pastor/Secretaria).

Regras:
- `criado_por == request.user` â†’ pode editar
- `criado_por is None` (actividade legada) â†’ sÃ³ papel elevado pode editar  
- `has_perm('sitetibl.change_mandato')` â†’ papel elevado, pode editar qualquer

### 7.4 DetecÃ§Ã£o de Conflitos

**Ficheiro:** `sitetibl/views.py` (`mostraCriacao`, `mostraActualizacao`)

- Actividades com horÃ¡rio sobreponÃ­vel no mesmo dia â†’ **erro** (bloqueia)
- Actividades no mesmo dia com horÃ¡rios diferentes â†’ **aviso** ("Se for num local diferente, pode prosseguir")

### 7.5 Actividades Recorrentes

**Ficheiros:** `sitetibl/forms.py`, `sitetibl/views.py`, `sitetibl/urls.py`, `templates/actividades_recorrentes.html`

Novo formulÃ¡rio com checkboxes de dias-da-semana. Vista gera N actividades por loop de datas (sem novo modelo).

URL: `actividades/recorrentes/`

### 7.6 Filtro por Departamento nas Escalas

**Ficheiros:** `sitetibl/views.py` (`encontraEscalas`), `templates/escalas.html`, `templates/escalasfiltrados.html`

- Dropdown de departamento adicionado ao formulÃ¡rio de filtro de escalas
- Query filter: `actividade__departamento_id`

---

## Grupos de PermissÃ£o (estado final)

| Grupo | Total Perms |
| --- | --- |
| Administrador | 176 (todas) |
| Pastor | 58 |
| Financeiro | 45 |
| Secretaria | 60 |
| LÃ­der de Departamento | 35 |
| Vice-LÃ­der de Departamento | 24 |
| LÃ­der de CÃ©lula | 9 |
| Membros Baptizados | 9 |
| Membro Geral | 3 |

---

## VerificaÃ§Ã£o (Checklist)

- [ ] `seed_base_data` â†’ LD sem `change_mandato`/`delete_mandato`
- [ ] LD tenta editar mandato alheio â†’ bloqueado por perm
- [ ] URL directa `/mandatos/actualizar/1/` como LD â†’ "Acesso negado"
- [ ] LD edita actividade que nÃ£o criou â†’ "SÃ³ pode editar actividades que criou"
- [ ] Criar actividade com horÃ¡rio sobreponÃ­vel â†’ erro imediato
- [ ] Criar no mesmo dia, horÃ¡rio diferente â†’ aviso mas guarda
- [ ] FormulÃ¡rio recorrente: Domingo + Quarta, 3 semanas â†’ 6 actividades criadas
- [ ] Filtrar escalas por departamento â†’ mostra apenas as desse dept

---

## 8. RestriÃ§Ãµes de LÃ­der de Departamento (LD/VLD)

### 8.1 GestÃ£o de Membros Restrita ao PrÃ³prio Departamento

**Ficheiro:** `sitetibl/views.py` (`mostraDetalhe` â€” `departamentos`)

- `pode_gerir_membros` agora exige: ser lÃ­der/vice do departamento **ou** ter `change_mandato` (papel elevado).
- LD/VLD de outro departamento nÃ£o consegue adicionar/remover membros.
- VerificaÃ§Ã£o usa `Departamento.lider_departamento_id` e `vice_lider_departamento_id`.

### 8.2 Propriedade de Actividades por Departamento

**Ficheiro:** `sitetibl/views.py` (`mostraActualizacao`, `mostraEliminacao`)

LD/VLD pode editar/eliminar actividades se:
1. `criado_por == request.user`, **ou**
2. Lidera o departamento associado Ã  actividade (via `Departamento.lider_departamento`/`vice_lider_departamento`).

### 8.3 Departamento NÃ£o EditÃ¡vel pelo LD

**Ficheiro:** `sitetibl/management/commands/seed_base_data.py`

- LD perdeu `change_departamento` â†’ sÃ³ pode `view_departamento`.
- Impede que LD altere o nome/descriÃ§Ã£o do departamento; sÃ³ gere membros e funÃ§Ãµes.

### 8.4 Cargos Exclusivos nos Mandatos

**Ficheiro:** `sitetibl/models.py` (`Mandato.save()`)

FunÃ§Ãµes exclusivas (apenas 1 por departamento): `lider`, `vice_lider`, `secretario`, `tesoureiro`, `coordenador`.

Ao atribuir um cargo exclusivo jÃ¡ ocupado:
- O ocupante anterior Ã© automaticamente rebaixado a **Membro**.
- Mensagem de aviso: *"Fulano deixou de ser LÃ­der e voltou a ser Membro."*

---

## 9. FunÃ§Ãµes de Escalas por Departamento

### 9.1 Modelo `Funcao` â€” Campo `departamento`

**Ficheiro:** `sitetibl/models.py`, `sitetibl/migrations/0083_funcao_departamento.py`

```python
departamento = ForeignKey('Departamento', null=True, blank=True, on_delete=SET_NULL, related_name='funcoes')
```
- `departamento=None` â†’ funÃ§Ã£o genÃ©rica (disponÃ­vel para todos).
- `departamento=X` â†’ funÃ§Ã£o especÃ­fica desse departamento.

### 9.2 GestÃ£o de FunÃ§Ãµes no Detalhe do Departamento

**Ficheiro:** `sitetibl/views.py` (`mostraDetalhe` â€” `departamentos`), `templates/departamentosdetalhado.html`

SecÃ§Ã£o "FunÃ§Ãµes do Departamento" com:
- Lista de funÃ§Ãµes em chips/pills com botÃ£o remover.
- ProtecÃ§Ã£o: nÃ£o remove funÃ§Ãµes em uso por escalas.
- FormulÃ¡rio inline para adicionar novas funÃ§Ãµes.
- PermissÃ£o: LD/VLD do departamento ou quem tenha `add_funcao`.

### 9.3 API Cascading: Actividade â†’ FunÃ§Ã£o

**Ficheiros:** `sitetibl/views.py` (`api_funcoes_por_actividade`), `sitetibl/urls.py`, `templates/formulario_criacao.html`

Endpoint: `GET /tibl/api/funcoes-actividade/<id>/`
- Retorna funÃ§Ãµes do departamento da actividade **+** funÃ§Ãµes genÃ©ricas.
- Dropdown de funÃ§Ã£o no formulÃ¡rio de criaÃ§Ã£o de escalas actualiza-se via AJAX ao seleccionar actividade.

### 9.4 PermissÃµes de FunÃ§Ãµes no Seeder

**Ficheiro:** `sitetibl/management/commands/seed_base_data.py`

| Grupo | PermissÃµes `funcao` |
| --- | --- |
| LÃ­der de Departamento | `add`, `change`, `delete`, `view` |
| Vice-LÃ­der de Departamento | `add`, `view` |

---

## 10. ClarificaÃ§Ã£o TerminolÃ³gica: Cargo vs FunÃ§Ã£o

### Problema
O termo "FunÃ§Ã£o" era usado para dois conceitos distintos, causando confusÃ£o na UI:

| Antes | Contexto | Exemplo |
| --- | --- | --- |
| FunÃ§Ã£o (Mandato) | Papel organizativo no departamento | LÃ­der, Vice-LÃ­der, Membro |
| FunÃ§Ã£o (Funcao) | Papel nas escalas/actividades | Pregador, Louvor, Som |

### SoluÃ§Ã£o

| Conceito | Termo na UI | Modelo | Exemplo |
| --- | --- | --- | --- |
| Papel no departamento | **Cargo** | `Mandato.funcao` | LÃ­der, Vice-LÃ­der, SecretÃ¡rio, Membro |
| Papel nas escalas | **FunÃ§Ã£o** | `Funcao` (modelo) | Pregador, Louvor, TÃ©cnico de Som |

**Ficheiros alterados:**
- `sitetibl/models.py` â€” verbose_name `'FunÃ§Ã£o'` â†’ `'Cargo'`
- `templates/departamentosdetalhado.html` â€” cabeÃ§alho tabela e label â†’ "Cargo"
- `templates/departamentos.html` â€” filtro de pesquisa â†’ "Cargo"
- `templates/mandatos.html` â€” cabeÃ§alho tabela â†’ "Cargo"
- `templates/mandatosdetalhado.html` â€” detalhe â†’ "Cargo"
- `templates/departamentosfiltrados.html` â€” cabeÃ§alho â†’ "Cargo" + correcÃ§Ã£o exibiÃ§Ã£o (valor bruto â†’ `cargo_display`)

---

## 11. SincronizaÃ§Ã£o de LideranÃ§a (Mandato â†” Departamento)

### Problema
`Departamento.lider_departamento` (FK) e `Mandato.funcao='lider'` podiam apontar para pessoas diferentes, levando a inconsistÃªncias entre a listagem de departamentos e os mandatos.

### SoluÃ§Ã£o â€” Mandato como fonte Ãºnica de verdade

| Mecanismo | Ficheiro | DescriÃ§Ã£o |
| --- | --- | --- |
| `Mandato.save()` | `sitetibl/models.py` | Ao gravar mandato com cargo `lider`/`vice_lider`, actualiza o FK do Departamento. Ao alterar para outro cargo, limpa o FK. |
| `post_delete` signal | `sitetibl/signals.py` | Ao apagar mandato de lÃ­der/vice, limpa o FK correspondente. |
| Comando `sync_lideranca` | `sitetibl/management/commands/sync_lideranca.py` | Comando de manutenÃ§Ã£o: `python manage.py sync_lideranca` â€” percorre todos os departamentos e corrige FKs com base nos mandatos existentes. |

---

## Grupos de PermissÃ£o (estado final actualizado)

| Grupo | Total Perms |
| --- | --- |
| Administrador | 176 (todas) |
| Pastor | 58 |
| Secretaria | 60 |
| Financeiro | 45 |
| LÃ­der de Departamento | 29 |
| Vice-LÃ­der de Departamento | 24 |
| LÃ­der de CÃ©lula | 9 |
| Membros Baptizados | 9 |
| Membro Geral | 3 |

---

## VerificaÃ§Ã£o (Checklist actualizado)

- [ ] `seed_base_data` â†’ LD sem `change_departamento`, com `funcao` crud
- [ ] LD tenta editar mandato alheio â†’ bloqueado por perm
- [ ] URL directa `/mandatos/actualizar/1/` como LD â†’ "Acesso negado"
- [ ] LD edita actividade que nÃ£o criou e nÃ£o Ã© do seu dept â†’ bloqueado
- [ ] LD edita actividade do seu departamento â†’ permitido
- [ ] Criar actividade com horÃ¡rio sobreponÃ­vel â†’ erro imediato
- [ ] Criar no mesmo dia, horÃ¡rio diferente â†’ aviso mas guarda
- [ ] FormulÃ¡rio recorrente: Domingo + Quarta, 3 semanas â†’ 6 actividades criadas
- [ ] Filtrar escalas por departamento â†’ mostra apenas as desse dept
- [ ] LD adiciona membro noutro departamento â†’ bloqueado
- [ ] Atribuir cargo "LÃ­der" a novo membro â†’ antigo lÃ­der rebaixado a Membro
- [ ] Adicionar funÃ§Ã£o ao departamento â†’ aparece nas chips
- [ ] Remover funÃ§Ã£o em uso por escala â†’ aviso e bloqueio
- [ ] Criar escala: seleccionar actividade â†’ dropdown funÃ§Ãµes filtra por dept
- [ ] Templates mostram "Cargo" (mandato) e "FunÃ§Ã£o" (escalas) sem confusÃ£o
- [ ] Mandatos Executivos e Departamentos mostram mesmo lÃ­der
- [ ] `python manage.py sync_lideranca` â†’ corrige inconsistÃªncias
