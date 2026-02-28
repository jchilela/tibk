# ANTIGRAVITY.md — Instruções para IAs de Código: Projecto TIBL (tibk)

## 1. Identidade do Projecto

| Atributo | Valor |
|---|---|
| **Framework** | Django 4.2.5 |
| **Template Engine** | Django Template Language (DTL) — **não é Jinja2** |
| **Padrão Arquitectural** | FBV (Function-Based Views) — sem CBV na app principal |
| **App principal** | `sitetibl` |
| **Settings** | `tibl/settings.py` |
| **URL raiz** | `tibl/urls.py` |
| **Base de Dados** | SQLite (configurada em `.env`, via `db.sqlite3`) |
| **Autenticação** | `django.contrib.auth` — utilizador padrão do Django |

---

## 2. Template Engine — Regras Estritas de Sintaxe DTL

> ⚠️ NUNCA usar sintaxe Jinja2 (`{{ variable() }}`, `{% import %}`, etc.). Apenas DTL é válido.

### Sintaxe permitida no DTL:

```django
{# Variável #}
{{ variavel }}
{{ variavel|filtro }}
{{ variavel|filtro:"argumento" }}

{# Condicionais #}
{% if condicao %}...{% elif outra %}...{% else %}...{% endif %}

{# Ciclos #}
{% for item in lista %}...{% empty %}...{% endfor %}

{# Blocos e herança #}
{% extends "base_modern.html" %}
{% block nome %}...{% endblock %}

{# Carregamento de tags #}
{% load static %}
{% load verificagrupo %}
{% load i18n %}

{# URLs #}
{% url 'nome_da_url' %}

{# Formulários #}
{% csrf_token %}

{# Comentários #}
{# comentário de linha #}
{% comment %}comentário de bloco{% endcomment %}
```

### ❌ PROIBIDO — Erros comuns a evitar:

```django
{# ERRADO — filtro default não resolve strings vazias #}
{{ user.first_name|default:user.username }}

{# CORRECTO #}
{% if user.first_name %}{{ user.first_name }}{% else %}{{ user.username }}{% endif %}

{# ERRADO — {% if %} multi-linha com operadores or/and quebrados #}
{% if user|has_group:"A" or
user|has_group:"B" %}

{# CORRECTO — sempre numa única linha #}
{% if user|has_group:"Administrador" or user|has_group:"Financeiro" %}

{# ERRADO — chamar métodos com parênteses #}
{{ user.groups.first() }}

{# CORRECTO — DTL não permite parênteses em chamadas #}
{{ user.groups.first.name }}
```

---

## 3. Estrutura de Ficheiros

```
tibk/
├── tibl/
│   ├── settings.py          # Configurações do projecto
│   └── urls.py              # URLs raiz
├── sitetibl/
│   ├── models.py            # Todos os models (FBV)
│   ├── views.py             # Todas as views (FBV)
│   ├── forms.py             # Formulários Django
│   └── templatetags/
│       └── verificagrupo.py # Tags e filtros personalizados
├── templates/
│   └── base_modern.html     # Template base — todos os outros herdam deste
├── static/
│   ├── estilos/modern.css
│   └── js/tibl-core.js
├── requirements.txt
└── .env                     # Variáveis de ambiente (DB, email, etc.)
```

---

## 4. Template Base: `base_modern.html`

Todos os templates do projecto devem começar com:
```django
{% extends "base_modern.html" %}
{% load static %}
{% load verificagrupo %}
```

### Blocos disponíveis no template base:

| Block | Uso |
|---|---|
| `{% block title %}` | Título da página |
| `{% block extra_css %}` | CSS adicional |
| `{% block content %}` | Conteúdo principal |
| `{% block extra_js %}` | JavaScript adicional |
| `{% block Titulo %}` | Compatibilidade legada |
| `{% block Irmaos %}`, `{% block irmaosdetalhe %}`, etc. | Blocos legados por secção |

### Variáveis de contexto sempre disponíveis no base template:

| Variável | Fonte | Descrição |
|---|---|---|
| `request.user` | Django Auth Middleware | Utilizador autenticado |
| `request.user.username` | `User.username` | Nome de login |
| `request.user.first_name` | `User.first_name` | **Pode ser string vazia** |
| `request.user.is_authenticated` | Django Auth | Booleano |
| `request.user.is_superuser` | Django Auth | Booleano |
| `request.user.groups` | ManyToMany | Grupos do utilizador |
| `request.path` | Django | URL actual |
| `request.resolver_match.url_name` | Django | Nome da URL activa |
| `messages` | Django Messages Framework | Mensagens flash |

---

## 5. Grupos de Utilizadores e Controlo de Acesso

O projecto usa grupos standard do Django (`django.contrib.auth.models.Group`).

### Grupos existentes:

- `Administrador`
- `Financeiro`
- `Secretaria`
- `Membros Baptizados`
- `Membro Geral`

### Filtro personalizado `has_group` (em `verificagrupo.py`):

```python
# Localização: sitetibl/templatetags/verificagrupo.py
@register.filter(name='has_group')
def has_group(user, group_name):
    if not hasattr(user, '_group_cache'):
        user._group_cache = set(user.groups.values_list('name', flat=True))
    return group_name in user._group_cache
```

**Para usar em templates:**
```django
{% load verificagrupo %}
{% if request.user|has_group:"Administrador" %}...{% endif %}
```

> ⚠️ `is_superuser=True` **NÃO implica pertencer a um grupo**. Um superadmin precisa de ser explicitamente adicionado ao grupo `Administrador` para que `has_group` funcione.

---

## 6. Models Principais

| Model | Descrição |
|---|---|
| `Pessoa` | Entidade base (pessoas em geral) |
| `Irmao(Pessoa)` | Membro da igreja — extends Pessoa, tem `OneToOneField(User)` |
| `Sitio` | Local físico (Igreja, Célula, etc.) |
| `Departamento` | Departamentos da igreja |
| `Mandato` | Relação Irmão ↔ Departamento ↔ Cargo (M2M through) |
| `Actividade` | Eventos/actividades |
| `Escala` | Relação Irmão ↔ Actividade ↔ Função |
| `Dizimooferta` | Dízimos e ofertas |
| `Entradabanco` / `Saidabanco` | Movimentos bancários |
| `Entradacaixa` / `Saidacaixa` | Movimentos de caixa |
| `PedidoSaida` | Pedidos de pagamento |
| `OrcamentoDepartamento` | Orçamentos por departamento |
| `InventarioPatrimonio` | Inventário de bens |
| `RelatorioSemanalCelula` | Relatórios de células |
| `ConteudoEnsino` | Ficheiros de ensino |
| `EnvioMensagem` | Envio de mensagens (email/SMS) |

---

## 7. Views — Padrões FBV

A aplicação usa Function-Based Views. O padrão geral é:

```python
@login_required
def minha_view(request):
    dados = Model.objects.all()
    return render(request, 'template.html', {'dados': dados})
```

As views genéricas de gestão seguem o padrão:
- `mostraGestao(request, gestaoescolhida, pagina)` — listagens
- `mostraDetalhe(request, gestaoescolhida, identificador)` — detalhe
- `mostraCriacao(request, gestaoescolhida)` — criar
- `mostraActualizacao(request, gestaoescolhida, id)` — editar
- `mostraEliminacao(request, gestaoescolhida, id)` — eliminar

---

## 8. Regras de Validação Estrutural Obrigatória

**A cada alteração num ficheiro `.html`, SEMPRE executar:**

```bash
# Verificar balanço de tags DTL
python3 << 'EOF'
import re
with open('templates/nome_do_ficheiro.html') as f:
    content = f.read()
ifs = len(re.findall(r'\{%-?\s*if\s', content))
endifs = len(re.findall(r'\{%-?\s*endif\s*-?%\}', content))
fors = len(re.findall(r'\{%-?\s*for\s', content))
endfors = len(re.findall(r'\{%-?\s*endfor\s*-?%\}', content))
blocks = len(re.findall(r'\{%-?\s*block\s', content))
endblocks = len(re.findall(r'\{%-?\s*endblock\s*-?%\}', content))
print(f"if/endif: {ifs}/{endifs} ({'OK' if ifs==endifs else 'ERRO'})")
print(f"for/endfor: {fors}/{endfors} ({'OK' if fors==endfors else 'ERRO'})")
print(f"block/endblock: {blocks}/{endblocks} ({'OK' if blocks==endblocks else 'ERRO'})")
EOF
```

**Regras de ouro:**
1. Cada `{% if %}` deve ter exatamente um `{% endif %}`
2. Cada `{% for %}` deve ter exatamente um `{% endfor %}`
3. Cada `{% block %}` deve ter exatamente um `{% endblock %}`
4. Tags DTL **nunca** podem ser quebradas em múltiplas linhas: `{% if\ncondição %}` é inválido
5. Variáveis `{{ }}` **nunca** podem ser quebradas em múltiplas linhas
6. Antes de remover qualquer `{% endif %}`, verificar qual `{% if %}` ele fecha

---

## 9. Checklist de Segurança Antes de Qualquer Alteração a Templates

- [ ] O `{% if %}` que vou adicionar tem o seu `{% endif %}` correspondente?
- [ ] Não estou a remover um `{% endif %}` que fecha um `{% if %}` existente?
- [ ] As tags `{% %}` e `{{ }}` estão todas numa única linha?
- [ ] Executei o script de verificação de balanço?
- [ ] O filtro `has_group` está disponível (`{% load verificagrupo %}`)?
- [ ] Usei `{% if user.first_name %}` em vez de `{{ user.first_name|default:x }}` para evitar o bug com strings vazias?

---

## 10. Notas Operacionais

- **Ambiente virtual:** `source venv/bin/activate` antes de qualquer `python manage.py ...`
- **Servidor de desenvolvimento:** `python manage.py runserver`
- **Base de dados:** SQLite em `db.sqlite3` (não requer XAMPP)
- **Configuração:** via ficheiro `.env` na raiz do projecto
- **Static files:** `manage.py collectstatic` apenas para produção
