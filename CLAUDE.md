# ANTIGRAVITY.md — Instructions for AI Coding Assistants: TIBL Project (tibk)

## 1. Project Identity

| Attribute | Value |
|---|---|
| **Framework** | Django 4.2.5 |
| **Template Engine** | Django Template Language (DTL) — **not Jinja2** |
| **Architectural Pattern** | FBV (Function-Based Views) — no CBVs in the main app |
| **Main App** | `sitetibl` |
| **Settings** | `tibl/settings.py` |
| **Root URL** | `tibl/urls.py` |
| **Database** | SQLite (configured in `.env`, via `db.sqlite3`) |
| **Authentication** | `django.contrib.auth` — standard Django user |

---

## 2. Template Engine — Strict DTL Syntax Rules

> ⚠️ NEVER use Jinja2 syntax (`{{ variable() }}`, `{% import %}`, etc.). Only DTL is valid.

### Allowed DTL Syntax:

```django
{# Variable #}
{{ variable }}
{{ variable|filter }}
{{ variable|filter:"argument" }}

{# Conditionals #}
{% if condition %}...{% elif other %}...{% else %}...{% endif %}

{# Loops #}
{% for item in list %}...{% empty %}...{% endfor %}

{# Blocks and Inheritance #}
{% extends "base_modern.html" %}
{% block name %}...{% endblock %}

{# Loading tags #}
{% load static %}
{% load verificagrupo %}
{% load i18n %}

{# URLs #}
{% url 'url_name' %}

{# Forms #}
{% csrf_token %}

{# Comments #}
{# inline comment #}
{% comment %}block comment{% endcomment %}
```

### ❌ FORBIDDEN — Common mistakes to avoid:

```django
{# WRONG — default filter does not resolve empty strings #}
{{ user.first_name|default:user.username }}

{# CORRECT #}
{% if user.first_name %}{{ user.first_name }}{% else %}{{ user.username }}{% endif %}

{# WRONG — multi-line {% if %} with broken or/and operators #}
{% if user|has_group:"A" or
user|has_group:"B" %}

{# CORRECT — always on a single line #}
{% if user|has_group:"Administrador" or user|has_group:"Financeiro" %}

{# WRONG — calling methods with parentheses #}
{{ user.groups.first() }}

{# CORRECT — DTL does not allow parentheses in calls #}
{{ user.groups.first.name }}
```

---

## 3. File Structure

```
tibk/
├── tibl/
│   ├── settings.py          # Project settings
│   └── urls.py              # Root URLs
├── sitetibl/
│   ├── models.py            # All models (FBV)
│   ├── views.py             # All views (FBV)
│   ├── forms.py             # Django forms
│   └── templatetags/
│       └── verificagrupo.py # Custom tags and filters
├── templates/
│   └── base_modern.html     # Base template — all others inherit from this
├── static/
│   ├── estilos/modern.css
│   └── js/tibl-core.js
├── requirements.txt
└── .env                     # Environment variables (DB, email, etc.)
```

---

## 4. Base Template: `base_modern.html`

All project templates must start with:
```django
{% extends "base_modern.html" %}
{% load static %}
{% load verificagrupo %}
```

### Available blocks in the base template:

| Block | Usage |
|---|---|
| `{% block title %}` | Page title |
| `{% block extra_css %}` | Additional CSS |
| `{% block content %}` | Main content |
| `{% block extra_js %}` | Additional JavaScript |
| `{% block Titulo %}` | Legacy compatibility |
| `{% block Irmaos %}`, `{% block irmaosdetalhe %}`, etc. | Legacy section blocks |

### Context variables always available in the base template:

| Variable | Source | Description |
|---|---|---|
| `request.user` | Django Auth Middleware | Authenticated user |
| `request.user.username` | `User.username` | Login name |
| `request.user.first_name` | `User.first_name` | **Can be an empty string** |
| `request.user.is_authenticated` | Django Auth | Boolean |
| `request.user.is_superuser` | Django Auth | Boolean |
| `request.user.groups` | ManyToMany | User's groups |
| `request.path` | Django | Current URL |
| `request.resolver_match.url_name` | Django | Active URL name |
| `messages` | Django Messages Framework | Flash messages |

---

## 5. User Groups and Access Control

The project uses standard Django groups (`django.contrib.auth.models.Group`).

### Existing groups:

- `Administrador`
- `Financeiro`
- `Secretaria`
- `Membros Baptizados`
- `Membro Geral`

### Custom filter `has_group` (in `verificagrupo.py`):

```python
# Location: sitetibl/templatetags/verificagrupo.py
@register.filter(name='has_group')
def has_group(user, group_name):
    if not hasattr(user, '_group_cache'):
        user._group_cache = set(user.groups.values_list('name', flat=True))
    return group_name in user._group_cache
```

**To use in templates:**
```django
{% load verificagrupo %}
{% if request.user|has_group:"Administrador" %}...{% endif %}
```

> ⚠️ `is_superuser=True` **DOES NOT imply belonging to a group**. A superuser must be explicitly added to the `Administrador` group for `has_group` to work.

---

## 6. Main Models

| Model | Description |
|---|---|
| `Pessoa` | Base entity (people in general) |
| `Irmao(Pessoa)` | Church member — extends Pessoa, has `OneToOneField(User)` |
| `Sitio` | Physical location (Church, Cell, etc.) |
| `Departamento` | Church departments |
| `Mandato` | Relation Irmão ↔ Departamento ↔ Cargo (M2M through) |
| `Actividade` | Events/activities |
| `Escala` | Relation Irmão ↔ Actividade ↔ Função |
| `Dizimooferta` | Tithes and offerings |
| `Entradabanco` / `Saidabanco` | Bank transactions |
| `Entradacaixa` / `Saidacaixa` | Cash transactions |
| `PedidoSaida` | Payment requests |
| `OrcamentoDepartamento` | Budgets per department |
| `InventarioPatrimonio` | Asset inventory |
| `RelatorioSemanalCelula` | Cell reports |
| `ConteudoEnsino` | Teaching files |
| `EnvioMensagem` | Message sending (email/SMS) |

---

## 7. Views — FBV Patterns

The application uses Function-Based Views. The general pattern is:

```python
@login_required
def my_view(request):
    data = Model.objects.all()
    return render(request, 'template.html', {'data': data})
```

Generic management views follow the pattern:
- `mostraGestao(request, gestaoescolhida, pagina)` — listings
- `mostraDetalhe(request, gestaoescolhida, identificador)` — details
- `mostraCriacao(request, gestaoescolhida)` — create
- `mostraActualizacao(request, gestaoescolhida, id)` — edit
- `mostraEliminacao(request, gestaoescolhida, id)` — delete

---

## 8. Obligatory Structural Validation Rules

**For every change in an `.html` file, ALWAYS execute:**

```bash
# Verify DTL tag balance
python3 << 'EOF'
import re
with open('templates/filename.html') as f:
    content = f.read()
ifs = len(re.findall(r'\{%-?\s*if\s', content))
endifs = len(re.findall(r'\{%-?\s*endif\s*-?%\}', content))
fors = len(re.findall(r'\{%-?\s*for\s', content))
endfors = len(re.findall(r'\{%-?\s*endfor\s*-?%\}', content))
blocks = len(re.findall(r'\{%-?\s*block\s', content))
endblocks = len(re.findall(r'\{%-?\s*endblock\s*-?%\}', content))
print(f"if/endif: {ifs}/{endifs} ({'OK' if ifs==endifs else 'ERROR'})")
print(f"for/endfor: {fors}/{endfors} ({'OK' if fors==endfors else 'ERROR'})")
print(f"block/endblock: {blocks}/{endblocks} ({'OK' if blocks==endblocks else 'ERROR'})")
EOF
```

**Golden Rules:**
1. Each `{% if %}` must have exactly one `{% endif %}`
2. Each `{% for %}` must have exactly one `{% endfor %}`
3. Each `{% block %}` must have exactly one `{% endblock %}`
4. DTL tags **must never** be split across multiple lines: `{% if\ncondition %}` is invalid
5. Variables `{{ }}` **must never** be split across multiple lines
6. Before removing any `{% endif %}`, verify which `{% if %}` it closes

---

## 9. Security Checklist Before Any Template Change

- [ ] Does the `{% if %}` I'm adding have its corresponding `{% endif %}`?
- [ ] Am I not removing an `{% endif %}` that closes an existing `{% if %}`?
- [ ] Are all `{% %}` and `{{ }}` tags on a single line?
- [ ] Did I run the structural balance verification script?
- [ ] Is the `has_group` filter available (`{% load verificagrupo %}`)?
- [ ] Did I use `{% if user.first_name %}` instead of `{{ user.first_name|default:x }}` to prevent the empty string bug?

---

## 10. Operational Notes

- **Virtual environment:** `source venv/bin/activate` before any `python manage.py ...`
- **Development server:** `python manage.py runserver`
- **Database:** SQLite in `db.sqlite3` (does not require XAMPP)
- **Configuration:** via `.env` file in the project root
- **Static files:** `manage.py collectstatic` for production only
