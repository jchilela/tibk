# Documentação Técnica - Sistema TIBL

## 1. Arquitetura do Sistema

### 1.1 Visão Geral da Arquitetura

O Sistema TIBL segue o padrão arquitetural **MVT (Model-View-Template)** do Django, com as seguintes camadas:

```
┌─────────────────────────────────────────┐
│         Camada de Apresentação          │
│     (Templates HTML + Static Files)     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Camada de Controle             │
│         (Views + Forms + URLs)          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Camada de Negócio               │
│      (Models + Business Logic)          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Camada de Persistência            │
│         (MySQL/MariaDB)                 │
└─────────────────────────────────────────┘

        Serviços Externos:
┌──────────────┐  ┌──────────────┐
│    Redis     │  │   Celery     │
│   (Cache)    │  │ (Background) │
└──────────────┘  └──────────────┘
```

### 1.2 Componentes Principais

#### 1.2.1 Aplicações Django

- **tibl/**: Aplicação principal (configurações, URLs, Celery)
- **sitetibl/**: Aplicação de gestão da igreja (models, views, forms)

#### 1.2.2 Serviços

- **Web Server**: Django Development Server / Gunicorn
- **Database**: MySQL/MariaDB
- **Cache**: Redis
- **Task Queue**: Celery + Celery Beat
- **Email**: SMTP (Gmail)

## 2. Modelos de Dados

### 2.1 Diagrama de Entidades (Principais)

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    Pessoa    │──────▶│    Irmao     │──────▶│  Departamento│
│  (Abstract)  │       │              │       │              │
└──────────────┘       └──────┬───────┘       └──────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              ┌─────▼─────┐      ┌─────▼─────┐
              │ Actividade│      │  Escala   │
              │           │      │           │
              └───────────┘      └───────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│Contabancaria │──────▶│ Entradabanco │       │ Entradacaixa │
│              │       │              │       │              │
└──────────────┘       └──────────────┘       └──────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Dizimooferta    │
                    │                  │
                    └──────────────────┘
```

### 2.2 Modelos Principais

#### 2.2.1 Pessoa (Abstract Base Model)

**Arquivo**: `sitetibl/models.py`

```python
class Pessoa(models.Model):
    # Campos principais:
    - nome: CharField(30)
    - apelido: CharField(30)
    - outrosnomes: CharField(60)
    - sexo: CharField(2) [M/F]
    - foto: ImageField
    - datanascimento: DateField
    - estadocivil: CharField(30)
    - grauescolaridade: CharField(50)
    - profissao: ForeignKey(Profissao)
    - especialidade: CharField(50)
    - localdetrabalho: CharField(50)
    - ruaenumero: CharField(60)
    - bairro: CharField(50)
    - municipio: CharField(50)
    - provincia: CharField(50)
    - telefone: CharField(50)
    - telefonewhatsapp: CharField(50)
    - email: EmailField
    - observacao: TextField
```

#### 2.2.2 Irmao (Herda de Pessoa)

```python
class Irmao(Pessoa):
    # Campos adicionais:
    - celula: ForeignKey(Sitio) [relacionado à célula]
    - localcongregacao: ForeignKey(Sitio) [relacionado à igreja]
    - culto: CharField(2) [P/I - Português/Inglês]
    - dizimista: CharField(10) [sim/nao]
    - batizado: BooleanField
    - user: OneToOneField(User)
    - data_criacao: DateTimeField (auto)
    - data_atualizacao: DateTimeField (auto)
```

#### 2.2.3 Departamento

```python
class Departamento(models.Model):
    - designacao: CharField(100) [unique]
    - abreviacao: CharField(10) [unique]
    - descricao: TextField
    - lider_departamento: ForeignKey(Irmao)
    - vice_lider_departamento: ForeignKey(Irmao)
    - integrantes: ManyToManyField(Irmao) [through='Mandato']
```

#### 2.2.4 Mandato (Tabela Intermediária)

```python
class Mandato(models.Model):
    - irmao: ForeignKey(Irmao)
    - departamento: ForeignKey(Departamento)
    - cargo: ForeignKey(Cargo)
    - inicio: DateField
    - fim: DateField
    
    # Constraint:
    unique_together = ('irmao', 'departamento', 'cargo', 'inicio')
```

#### 2.2.5 Actividade

```python
class Actividade(models.Model):
    - designacao: ForeignKey(Listaactividades)
    - inicio: TimeField
    - fim: TimeField
    - data: DateField
    - tema: CharField(500)
    - localactividade: ForeignKey(Sitio)
    - versosbiblicos: CharField(200)
    - hinos: CharField(300)
    - participantes: ManyToManyField(Irmao) [through='Escala']
    - totalpresentes: IntegerField
    - observacao: TextField
```

#### 2.2.6 Contabancaria

```python
class Contabancaria(models.Model):
    - banco: ForeignKey(Banco)
    - numeroconta: CharField(100) [unique]
    - iban: CharField(100) [unique]
    - moeda: CharField(50)
    - saldo: DecimalField(11, 2)
    - proprietario: ForeignKey(Pessoa)
    - instituicao: ForeignKey(Sitio)
```

#### 2.2.7 Dizimooferta

```python
class Dizimooferta(models.Model):
    - valor: DecimalField(11, 2)
    - moeda: CharField(50)
    - tipooferta: ForeignKey(TipoOferta)
    - datacorrespondente: DateField
    - irmao: ForeignKey(Irmao)
    - actividade: ForeignKey(Actividade) [opcional]
    - datacontrolo: DateField (auto)
    - dataregisto: DateField
    - entradabanco: ForeignKey(Entradabanco)
    - entradacaixa: ForeignKey(Entradacaixa)
```

#### 2.2.8 InventarioPatrimonio

```python
class InventarioPatrimonio(models.Model):
    - nome: CharField(100)
    - descricao: CharField(100)
    - categoria_patrimonio: ForeignKey(Categoria_Patrimonio)
    - codigo: CharField(100) [unique]
    - quantidade: IntegerField
    - localizacao: CharField(100)
    - preco: BigIntegerField
    - moeda: ForeignKey(Tipo_Moeda)
    - data_aquisicao: DateField
    - responsavel: ForeignKey(Irmao)
    - foto: FileField
    - estado: ForeignKey(Estado_Patrimonio)
    - observacao: TextField
    - registo_danos: TextField
    - data_ultima_manutencao: DateField
    - data_proxima_manutencao: DateField
    - descricao_manutencao_realizada: TextField
    - data_criacao: DateTimeField (auto)
    - data_atualizacao: DateTimeField (auto)
```

### 2.3 Relacionamentos Importantes

1. **Irmao → Departamento**: Relacionamento Many-to-Many através de `Mandato`
2. **Irmao → Actividade**: Relacionamento Many-to-Many através de `Escala`
3. **Entradas/Saídas**: Vinculadas a contas bancárias e rubricas
4. **Ajudas**: Vinculadas a beneficiários (Pessoa) e saídas financeiras

## 3. Camada de Views

### 3.1 Estrutura de Views

**Arquivo**: `sitetibl/views.py` (1545 linhas)

#### 3.1.1 Views Principais de CRUD

```python
def mostraGestao(request, gestaoescolhida, pagina):
    """
    View genérica para listagem paginada de entidades
    URL: /tibl/gestao/<gestaoescolhida>/<pagina>/
    Suporta: irmaos, departamentos, actividades, cestas, etc.
    Paginação: 20 itens por página
    """

def mostraDetalhe(request, gestaoescolhida, identificador):
    """
    View genérica para exibir detalhes de um registro
    URL: /tibl/<gestaoescolhida>/detalhe/<id>/
    """

def mostraCriacao(request, gestaoescolhida):
    """
    View genérica para criação de novos registros
    URL: /tibl/<gestaoescolhida>/criar/
    Usa formulários Django (forms.py)
    """

def mostraActualizacao(request, gestaoescolhida, id):
    """
    View genérica para atualização de registros
    URL: /tibl/<gestaoescolhida>/actualizar/<id>/
    """

def mostraEliminacao(request, gestaoescolhida, id):
    """
    View genérica para exclusão de registros
    URL: /tibl/<gestaoescolhida>/eliminar/<id>/
    """
```

#### 3.1.2 Views de Busca/Filtro

```python
def encontraIrmao(request):
    """
    Busca irmãos por múltiplos critérios
    Parâmetros GET: nomev, apelidov, bairrov, municipiov, provinciav, etc.
    """

def encontraDizimosofertas(request):
    """
    Filtra dízimos e ofertas por data e membro
    """

def encontraInventarioPatrimonio(request):
    """
    Filtra patrimônio por categoria, localização, responsável
    """
```

#### 3.1.3 Views de Dashboard (API JSON)

```python
def dashboardIrmaos(request):
    """
    Retorna JSON com número de membros cadastrados por mês
    Usado para gráficos no frontend
    """

def dashboardOrcamentoDepartamento(request):
    """
    Retorna JSON com orçamento agregado por departamento
    """

def dashboardPedidosSaidaSemana(request):
    """
    Retorna JSON com pedidos de saída agrupados por dia da semana
    """

def dashboardDizimoOferta(request):
    """
    Retorna JSON com dados de dízimos e ofertas
    """

def dashboardCrescimentoMembros(request):
    """
    Retorna JSON com crescimento de membros ao longo do tempo
    """
```

#### 3.1.4 Views de Relatórios PDF

```python
def relatorio_irmaos_pdf(request):
    """
    Gera PDF com listagem de membros
    Usa: ReportLab, Table, Paragraph
    Inclui logo da igreja
    """

def relatorio_dizimos_pdf(request):
    """
    Gera PDF com relatório de dízimos e ofertas
    """

def relatorio_inventario_patrimonio_pdf(request):
    """
    Gera PDF com inventário patrimonial
    """

def relatorio_saida_caixa_pdf(request):
    """
    Gera PDF com saídas de caixa (pedidos)
    """
```

### 3.2 Padrões de View Implementados

#### 3.2.1 View Genérica CRUD

O sistema utiliza um dicionário para mapear entidades e formulários:

```python
lista = {
    'escalas': Escala,
    'mandatos': Mandato,
    'irmaos': Irmao,
    'ajudas': Ajuda,
    # ... outras entidades
}

listaformularios = {
    'escalas': EscalaForm,
    'mandatos': MandatoForm,
    'irmaos': IrmaoForm,
    # ... outros formulários
}
```

#### 3.2.2 Filtros Dinâmicos

```python
kwargs = {
    'campo__icontains': valor_busca,
    'campo_fk__campo__icontains': valor_busca,
}
resultado = Model.objects.filter(**kwargs)
```

#### 3.2.3 Agregações e Anotações

```python
queryset = (
    Irmao.objects
    .filter(data_criacao__year=ano)
    .annotate(mes=TruncMonth('data_criacao'))
    .values('mes')
    .annotate(total=Count('id'))
    .order_by('mes')
)
```

## 4. Camada de Forms

**Arquivo**: `sitetibl/forms.py` (216 linhas)

### 4.1 Estrutura de Forms

Todos os formulários herdam de `ModelForm`:

```python
class IrmaoForm(ModelForm):
    # Validação customizada
    telefone = forms.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',
                message='O telefone deve conter exatamente 9 números.'
            )
        ]
    )
    
    class Meta:
        model = Irmao
        fields = '__all__'
        widgets = {
            'datanascimento': forms.DateInput(attrs={'type': 'date'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar dropdowns
        self.fields['celula'].queryset = Sitio.objects.filter(tipo='2')
        self.fields['localcongregacao'].queryset = Sitio.objects.filter(tipo='1')
```

### 4.2 Forms Principais

- **IrmaoForm**: Cadastro de membros com validações
- **ActividadeForm**: Criação de atividades (exclui campo ManyToMany)
- **DepartamentoForm**: Gestão de departamentos
- **DizimoofertaForm**: Registro de dízimos
- **EntradabancoForm / SaidabancoForm**: Movimentações bancárias
- **RelatorioSemanalCelulaForm**: Relatórios de células
- **PedidoSaidaForm / PedidoSaidaUpdateForm**: Pedidos financeiros
- **InventarioPatrimonioForm**: Gestão de patrimônio

### 4.3 Widgets Customizados

```python
widgets = {
    'data': forms.DateInput(attrs={'type': 'date'}),
    'inicio': forms.TimeInput(attrs={'type': 'time'}),
    'fim': forms.TimeInput(attrs={'type': 'time'}),
}
```

## 5. Sistema de Tarefas Assíncronas

### 5.1 Configuração do Celery

**Arquivo**: `tibl/celery.py`

```python
app = Celery('tibl')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'notificacoes_escala_cada_1_minuto': {
        'task': 'sitetibl.tasks.enviar_notificacoes_escala',
        'schedule': crontab(hour=4, minute=0),  # 4h da manhã
    },
}
```

### 5.2 Tarefas Implementadas

**Arquivo**: `sitetibl/tasks.py`

```python
@shared_task
def enviar_notificacoes_escala():
    """
    Tarefa agendada para enviar notificações de escala
    
    Execução: Diariamente às 4h da manhã
    
    Lógica:
    1. Busca atividades para daqui a 2 dias e 1 dia
    2. Para cada atividade, busca escalas associadas
    3. Para cada membro escalado com email:
       - Renderiza template HTML personalizado
       - Envia email com detalhes da atividade
    
    Template: templates/emails/lembrete_escala.html
    """
```

### 5.3 Configuração no Settings

```python
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

## 6. Configurações

### 6.1 Settings Principais

**Arquivo**: `tibl/settings.py`

#### 6.1.1 Banco de Dados

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'tibldb'),
        'USER': os.getenv('DB_USER', 'tibl_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', '46.224.57.18'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

#### 6.1.2 Workarounds

```python
# Workaround para MariaDB 10.4 (Django 4.2+ requer 10.5+)
from django.db.backends.base.base import BaseDatabaseWrapper
BaseDatabaseWrapper.check_database_version_supported = lambda self: None

from django.db.backends.mysql.features import DatabaseFeatures
DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)
DatabaseFeatures.can_return_rows_from_bulk_insert = property(lambda self: False)
```

#### 6.1.3 Email

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

#### 6.1.4 Aplicações Instaladas

```python
INSTALLED_APPS = [
    'clearcache',           # Limpeza de cache
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_mysql',         # Extensões MySQL
    'sitetibl',            # App principal
    'django_celery_beat',  # Agendamento de tarefas
]
```

#### 6.1.5 Segurança

```python
CSRF_TRUSTED_ORIGINS = ['https://gestao.tibl.ao']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CORS_ALLOWED_ORIGINS = ['https://gestao.tibl.ao']
```

#### 6.1.6 Timezone

```python
TIME_ZONE = 'Africa/Luanda'
USE_TZ = False
```

### 6.2 Variáveis de Ambiente (.env)

```bash
SECRET_KEY=<secret>
DEBUG=False
ALLOWED_HOSTS=gestao.tibl.ao,localhost

DB_ENGINE=django.db.backends.mysql
DB_NAME=tibldb
DB_USER=tibl_user
DB_PASSWORD=<password>
DB_HOST=46.224.57.18
DB_PORT=3306

CELERY_BROKER_URL=redis://127.0.0.1:6379/0

EMAIL_HOST_USER=tiblbaptista7@gmail.com
EMAIL_HOST_PASSWORD=<app_password>

CSRF_TRUSTED_ORIGINS=https://gestao.tibl.ao
CORS_ALLOWED_ORIGINS=https://gestao.tibl.ao
```

## 7. URLs e Roteamento

**Arquivo**: `tibl/urls.py`

### 7.1 Padrões de URL

```python
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('admin/clearcache/', include('clearcache.urls')),
    
    # Autenticação
    path('accounts/', include('django.contrib.auth.urls')),
    
    # CRUD Genérico
    path('tibl/gestao/<gestaoescolhida>/<int:pagina>/', mostraGestao),
    path('tibl/<gestaoescolhida>/detalhe/<int:identificador>/', mostraDetalhe),
    path('tibl/<gestaoescolhida>/criar/', mostraCriacao),
    path('tibl/<gestaoescolhida>/actualizar/<int:id>/', mostraActualizacao),
    path('tibl/<gestaoescolhida>/eliminar/<int:id>/', mostraEliminacao),
    
    # Buscas Específicas
    path('tibl/buscairmao/', encontraIrmao),
    path('tibl/buscadizimosofertas/', encontraDizimosofertas),
    path('tibl/buscainventariopatrimonio/', encontraInventarioPatrimonio),
    
    # Dashboard (APIs JSON)
    path('dashboard/numero-irmaos-cadastrados-mensalmente', dashboardIrmaos),
    path('dashboard/orcamento-departamento', dashboardOrcamentoDepartamento),
    path('dashboard/pedido-saida-semana', dashboardPedidosSaidaSemana),
    
    # Relatórios PDF
    path('relatorios/', pagina_relatorios, name='pagina_relatorios'),
    path('relatorios/irmaos/pdf/', relatorio_irmaos_pdf),
    path('relatorios/dizimos/pdf/', relatorio_dizimos_pdf),
    path('relatorios/inventario_patrimonio/pdf/', relatorio_inventario_patrimonio_pdf),
]
```

### 7.2 Convenções de Nomenclatura

- **Gestão genérica**: `/tibl/gestao/<entidade>/<pagina>/`
- **Detalhes**: `/tibl/<entidade>/detalhe/<id>/`
- **Criação**: `/tibl/<entidade>/criar/`
- **Atualização**: `/tibl/<entidade>/actualizar/<id>/`
- **Eliminação**: `/tibl/<entidade>/eliminar/<id>/`
- **Busca**: `/tibl/busca<entidade>/`
- **Dashboard**: `/dashboard/<metrica>`
- **Relatórios**: `/relatorios/<tipo>/pdf/`

## 8. Templates

### 8.1 Estrutura de Templates

```
templates/
├── index.html                      # Página inicial
├── login.html                      # Login
├── formulario_criacao.html         # Form genérico de criação
├── formulario_actualizacao.html    # Form genérico de atualização
├── confirmar_eliminacao.html       # Confirmação de exclusão
├── paginacao                       # Template de paginação
├── relatorios/                     # Página de relatórios
├── emails/
│   └── lembrete_escala.html       # Email de notificação
├── <entidade>                      # Listagem (ex: irmaos)
├── <entidade>detalhado.html       # Detalhes
└── <entidade>filtrados.html       # Resultados de busca
```

### 8.2 Padrão de Templates

#### Listagem
```html
{% extends "base.html" %}
{% block content %}
<table>
  {% for item in bb %}
    <tr>
      <td>{{ item.campo }}</td>
      <td><a href="/tibl/<entidade>/detalhe/{{ item.id }}/">Ver</a></td>
    </tr>
  {% endfor %}
</table>
<!-- Paginação -->
{% include "paginacao" %}
{% endblock %}
```

## 9. Geração de Relatórios PDF

### 9.1 Estrutura com ReportLab

```python
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.pagesizes import A4

def relatorio_exemplo_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    
    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'fotos', 'cba.png')
    logo = Image(logo_path, width=70, height=70)
    elements.append(logo)
    
    # Título
    elements.append(Paragraph("<b>Título</b>", styles['Title']))
    
    # Tabela
    data = [['Col1', 'Col2'], ['Dado1', 'Dado2']]
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#548c2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    
    doc.build(elements)
    return response
```

### 9.2 Estilo Padrão

- **Cor de cabeçalho**: `#548c2f` (verde)
- **Fonte**: Helvetica
- **Tamanho de célula**: 9pt
- **Logo**: 70x70 pixels
- **Largura da página**: A4
- **Margens**: 40 pontos

## 10. Deployment

### 10.1 Docker

**Arquivo**: `docker-compose.yml`

```yaml
version: '3'
services:
  web:
    build: ..
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### 10.2 Dockerfile

```dockerfile
FROM python:3.10
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### 10.3 Comandos de Deploy

```bash
# Instalar dependências
pip install -r requirements.txt

# Migrations
python manage.py makemigrations
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser

# Iniciar Celery Worker
celery -A tibl worker --loglevel=info

# Iniciar Celery Beat
celery -A tibl beat --loglevel=info

# Iniciar servidor (produção)
gunicorn tibl.wsgi:application --bind 0.0.0.0:8000
```

## 11. Performance e Otimizações

### 11.1 Paginação

- Todas as listagens são paginadas em 20 itens
- Uso de `Paginator` do Django

### 11.2 Select Related / Prefetch Related

Implementar em queries complexas:

```python
Irmao.objects.select_related('profissao', 'celula', 'localcongregacao')
Escala.objects.select_related('irmao', 'funcao', 'actividade')
```

### 11.3 Cache (Redis)

Configurado mas pode ser expandido para:
- Cache de queries frequentes
- Cache de templates
- Session storage

### 11.4 Índices de Banco de Dados

Campos com `unique=True` já possuem índices automáticos.
Considerar adicionar índices em:
- Campos de data (para filtros)
- ForeignKeys sem CASCADE
- Campos de busca frequente

## 12. Segurança

### 12.1 Medidas Implementadas

1. **CSRF Protection**: Ativado em todas as forms
2. **SQL Injection**: ORM do Django previne automaticamente
3. **XSS**: Template engine escapa HTML automaticamente
4. **Senhas**: Hasheadas com PBKDF2
5. **HTTPS**: Configurado em produção
6. **Variáveis de Ambiente**: Dados sensíveis em `.env`

### 12.2 Recomendações Adicionais

1. Implementar rate limiting
2. Adicionar 2FA para admin
3. Logs de auditoria para ações críticas
4. Backup automático do banco
5. Monitoramento de tentativas de login
6. Validação de upload de arquivos

## 13. Testes

### 13.1 Estrutura para Testes

**Arquivo**: `sitetibl/tests.py` (vazio atualmente)

Implementar:

```python
from django.test import TestCase
from .models import Irmao, Departamento

class IrmaoModelTest(TestCase):
    def setUp(self):
        # Criar dados de teste
        pass
    
    def test_criacao_irmao(self):
        # Testar criação
        pass
    
    def test_validacao_telefone(self):
        # Testar validação
        pass
```

### 13.2 Tipos de Testes Recomendados

1. **Unit Tests**: Models, forms, validações
2. **Integration Tests**: Views, workflows completos
3. **API Tests**: Endpoints de dashboard
4. **PDF Tests**: Geração de relatórios
5. **Email Tests**: Envio de notificações

## 14. Monitoramento e Logs

### 14.1 Logs do Django

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### 14.2 Monitoramento do Celery

```bash
# Ver tasks em execução
celery -A tibl inspect active

# Ver tasks agendadas
celery -A tibl inspect scheduled

# Ver workers disponíveis
celery -A tibl inspect stats
```

## 15. Manutenção

### 15.1 Backup do Banco de Dados

```bash
# Backup MySQL
mysqldump -u tibl_user -p tibldb > backup_$(date +%Y%m%d).sql

# Restore
mysql -u tibl_user -p tibldb < backup_20260206.sql
```

### 15.2 Limpeza de Arquivos Antigos

```bash
# Limpar sessões expiradas
python manage.py clearsessions

# Limpar cache
python manage.py clear_cache
```

### 15.3 Atualizações

```bash
# Atualizar dependências
pip install -r requirements.txt --upgrade

# Verificar migrações pendentes
python manage.py showmigrations

# Aplicar migrações
python manage.py migrate
```

## 16. Troubleshooting

### 16.1 Problemas Comuns

#### Erro: "django.db.utils.OperationalError: (2006, 'MySQL server has gone away')"

**Solução**: Aumentar `wait_timeout` no MySQL ou usar connection pooling

#### Erro: Celery não processa tasks

**Solução**:
1. Verificar se Redis está rodando: `redis-cli ping`
2. Verificar worker: `celery -A tibl inspect active`
3. Reiniciar worker e beat

#### Erro: Imagens não carregam

**Solução**: Verificar `MEDIA_URL` e `MEDIA_ROOT` no settings

### 16.2 Debug Mode

```python
# Em desenvolvimento
DEBUG = True

# Ver queries SQL
from django.db import connection
print(connection.queries)

# Shell interativo
python manage.py shell
```

## 17. Glossário Técnico

- **MVT**: Model-View-Template (padrão do Django)
- **ORM**: Object-Relational Mapping
- **CRUD**: Create, Read, Update, Delete
- **Celery**: Framework de tarefas assíncronas
- **Redis**: Banco de dados em memória (cache/broker)
- **WSGI**: Web Server Gateway Interface
- **QuerySet**: Conjunto de resultados de query do Django
- **Migration**: Arquivo de alteração de schema do banco

## 18. Referências

- [Documentação Django 4.2](https://docs.djangoproject.com/en/4.2/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Redis Documentation](https://redis.io/documentation)
