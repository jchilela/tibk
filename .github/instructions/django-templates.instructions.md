---
description: "Use when creating or editing Django HTML templates. Enforces strict DTL syntax, tag balance validation, forbidden patterns, base template inheritance, and the empty-string bug guard."
applyTo: "templates/**"
---

# Django Template Language (DTL) â€” Strict Rules

> **NEVER** use Jinja2 syntax. This project uses DTL exclusively.

## Template Boilerplate

Every template MUST start with:

```django
{% extends "base_modern.html" %}
{% load static %}
{% load verificagrupo %}
```

## Allowed Syntax

```django
{{ variable }}                       {# variable output #}
{{ variable|filter:"arg" }}          {# filter with argument #}
{% if cond %}...{% endif %}          {# conditional #}
{% for x in list %}...{% endfor %}   {# loop #}
{% block name %}...{% endblock %}    {# block #}
{% url 'name' %}                     {# URL reverse #}
{% csrf_token %}                     {# CSRF #}
{% load static %}                    {# load tags #}
```

## âŒ Forbidden Patterns

| Wrong | Why | Correct |
| --- | --- | --- |
| `{{ user.first_name\ | default:user.username }}` | `default` does not catch empty strings | `{% if user.first_name %}{{ user.first_name }}{% else %}{{ user.username }}{% endif %}` |
| `{% if cond or` *(newline)* `other %}` | Multi-line DTL tags are invalid | Keep entire `{% if ... %}` on one single line |
| `{{ user.groups.first() }}` | DTL forbids parentheses in calls | `{{ user.groups.first.name }}` |
| `{{ variable() }}` | Jinja2 call syntax | `{{ variable }}` |
| `{% import %}` | Jinja2 import | `{% load taglib %}` |

## Golden Rules â€” Tag Balance

1. Every `{% if %}` must have exactly one `{% endif %}`
2. Every `{% for %}` must have exactly one `{% endfor %}`
3. Every `{% block %}` must have exactly one `{% endblock %}`
4. `{% %}` and `{{ }}` tags must NEVER be split across multiple lines
5. Before removing any `{% endif %}`, verify which `{% if %}` it closes

## Post-Edit Validation (MANDATORY)

After every `.html` edit, run the tag balance check:

```python
import re
with open('templates/<filename>.html') as f:
    content = f.read()
ifs = len(re.findall(r'\{%-?\s*if\s', content))
endifs = len(re.findall(r'\{%-?\s*endif\s*-?%\}', content))
fors = len(re.findall(r'\{%-?\s*for\s', content))
endfors = len(re.findall(r'\{%-?\s*endfor\s*-?%\}', content))
blocks = len(re.findall(r'\{%-?\s*block\s', content))
endblocks = len(re.findall(r'\{%-?\s*endblock\s*-?%\}', content))
# All pairs must match; any mismatch = ERROR
```

## Available Blocks in `base_modern.html`

| Block | Purpose |
| --- | --- |
| `title` | Page title |
| `extra_css` | Additional CSS |
| `content` | Main content |
| `extra_js` | Additional JavaScript |
| `Titulo` | Legacy compatibility |

## Authorization in Templates

Use `perms.sitetibl.*` for access control â€” NOT `has_group`:

```django
{# CORRECT â€” permission-based #}
{% if perms.sitetibl.view_dizimooferta %}
  {# show menu item #}
{% endif %}

{# has_group is ONLY for display labels #}
{% if request.user|has_group:"Administrador" %}
  <span class="badge">Admin</span>
{% endif %}
```

## Pre-Commit Checklist

- [ ] Each `{% if %}` has its `{% endif %}`?
- [ ] Not removing an `{% endif %}` that closes an existing `{% if %}`?
- [ ] All tags on single lines?
- [ ] Tag balance script passed?
- [ ] Using `{% if user.first_name %}` instead of `|default:` for empty strings?
