---
description: "Use when modifying Django authorization logic, permission checks, group-based access control, template visibility guards, or view-level access restrictions. Covers perms vs has_group, backend has_perm, and group permission architecture."
applyTo: ["templates/**/*.html", "sitetibl/views.py", "sitetibl/templatetags/**", "sitetibl/management/commands/seed_*.py"]
---

# Django Permission Architecture

This project uses a two-layer permission system. Permissions are the **source of truth**; groups are bundles of permissions.

## Templates — Authorization

Use Django's built-in `perms` variable for showing/hiding UI based on access:

```django
{# CORRECT — permission-based authorization #}
{% if perms.sitetibl.view_dizimooferta or perms.sitetibl.view_entradabanco %}
  {# financial menu items #}
{% endif %}

{# CORRECT — staff flag for admin-panel access #}
{% if request.user.is_staff %}
  <a href="/admin/">Admin</a>
{% endif %}
```

### ❌ FORBIDDEN for authorization

```django
{# WRONG — group names are fragile, not the source of truth #}
{% if request.user|has_group:"Financeiro" %}
  {# financial menu #}
{% endif %}
```

### ✅ has_group is allowed ONLY for display/labels

```django
{# OK — showing the user's role label, not gating access #}
{% if request.user|has_group:"Administrador" %}
  <span class="badge">Admin</span>
{% elif request.user|has_group:"Financeiro" %}
  <span class="badge">Financeiro</span>
{% endif %}
```

## Views — Backend Authorization

Always use `has_perm()` with the canonical format `app_label.action_modelname`:

```python
# CORRECT
perm = f'{model._meta.app_label}.change_{model._meta.model_name}'
if not request.user.has_perm(perm):
    raise PermissionDenied

# WRONG — never check group name in views
if not request.user.groups.filter(name='Administrador').exists():
    ...
```

## Group → Permission Mapping

Groups are permission bundles assigned via the seeder (`seed_base_data.py`):

| Group | Scope |
|---|---|
| Administrador | All `sitetibl` permissions (176) |
| Pastor | Supervisão pastoral — CRUD actividades/membros/pedidos, view financeiro (58) |
| Financeiro | CRUD financeiro + aprovação de pedidos + view membros (45) |
| Secretaria | CRUD membros/actividades/comunicação + view financeiro (60) |
| Líder de Departamento | CRUD actividades/escalas/mandatos do dept, cria pedidos, envia mensagens (37) |
| Vice-Líder de Departamento | CRUD actividades/escalas/mandatos do dept, cria pedidos (26) |
| Líder de Célula | Relatórios semanais (CRU) + view membros/actividades (9) |
| Membros Baptizados | View maioria + add relatório + view escalas (11) |
| Membro Geral | View actividade, departamento, conteúdo, anúncios (4) |

When adding a new model or permission, update `_assign_group_permissions()` in the seeder.
