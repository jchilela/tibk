# Sistema TIBL - Terceira Igreja Baptista de Luanda

![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![Django](https://img.shields.io/badge/django-4.2.5-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Sistema de gestão integrada para administração de TIBL, desenvolvido em Django. Centraliza a gestão de membros, finanças, patrimônio, atividades, departamentos e comunicação.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Documentação](#documentação)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## 🎯 Sobre o Projeto

O Sistema TIBL foi desenvolvido para facilitar a gestão completa de uma TIBL, oferecendo ferramentas para:

- Cadastro e gestão de membros
- Controle financeiro (dízimos, ofertas, entradas e saídas)
- Gestão de atividades e escalas de serviço
- Organização de departamentos e mandatos
- Controle patrimonial
- Relatórios de células
- Comunicação com membros (email/SMS)
- Dashboards e relatórios em PDF

## ✨ Funcionalidades Principais

### 👥 Gestão de Membros
- Cadastro completo com foto e dados pessoais
- Controle de batismo e status de dizimista
- Vinculação com células e departamentos
- Histórico de participações

### 💰 Gestão Financeira
- Registro de dízimos e ofertas
- Controle de entradas e saídas (caixa e banco)
- Gestão de contas bancárias
- Pedidos de saída com aprovação
- Orçamento por departamento

### 📅 Gestão de Atividades
- Cadastro de cultos, células e eventos
- Escalas de serviço com funções
- Notificações automáticas por email
- Controle de presença

### 🏛️ Gestão de Departamentos
- Organização hierárquica
- Mandatos com datas de início e fim
- Cargos e funções

### 📦 Gestão de Patrimônio
- Inventário completo de bens
- Controle de manutenções
- Registro de danos
- Fotos e documentação

### 📊 Relatórios e Dashboards
- Gráficos de crescimento
- Relatórios financeiros
- Relatórios em PDF customizados
- Dashboard executivo

## 🛠️ Tecnologias Utilizadas

### Backend
- **Django 4.2.5** - Framework web
- **Python 3.10** - Linguagem de programação
- **MySQL/MariaDB** - Banco de dados
- **Celery 5.4.0** - Tarefas assíncronas
- **Redis 5.0.1** - Cache e message broker

### Frontend
- **HTML5/CSS3** - Templates
- **JavaScript** - Interatividade
- **Chart.js** - Gráficos (inferido)

### Bibliotecas Principais
- **ReportLab** - Geração de PDFs
- **Pillow** - Processamento de imagens
- **django-celery-beat** - Agendamento de tarefas
- **PyMySQL** - Driver MySQL para Python

### Deploy
- **Gunicorn** - WSGI HTTP Server
- **Docker** - Containerização
- **Docker Compose** - Orquestração

## 📋 Pré-requisitos

- Python 3.10 ou superior
- MySQL 8.0 ou MariaDB 10.5+
- Redis 5.0+
- pip (gerenciador de pacotes Python)
- virtualenv (recomendado)
- Git

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/tibk.git
cd tibk
```

### 2. Criar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Banco de Dados

```bash
# Criar banco de dados MySQL
mysql -u root -p
CREATE DATABASE tibldb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tibl_user'@'localhost' IDENTIFIED BY 'sua_senha';
GRANT ALL PRIVILEGES ON tibldb.* TO 'tibl_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Configurar Variáveis de Ambiente

Criar arquivo `.env` na raiz do projeto:

```bash
SECRET_KEY=sua_secret_key_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.mysql
DB_NAME=tibldb
DB_USER=tibl_user
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=3306

CELERY_BROKER_URL=redis://127.0.0.1:6379/0

EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app

CSRF_TRUSTED_ORIGINS=http://localhost:8000
CORS_ALLOWED_ORIGINS=http://localhost:8000
```

### 6. Executar Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Criar Superusuário

```bash
python manage.py createsuperuser
```

### 8. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

## ⚙️ Configuração

### Iniciar Redis

```bash
redis-server
```

### Iniciar Celery Worker

```bash
celery -A tibl worker --loglevel=info
```

### Iniciar Celery Beat (Tarefas Agendadas)

```bash
celery -A tibl beat --loglevel=info
```

### Iniciar Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Acesse: http://localhost:8000

## 🎮 Uso

### Admin Panel

Acesse http://localhost:8000/admin/ com as credenciais do superusuário.

### Interface Principal

1. Faça login em http://localhost:8000/accounts/login/
2. Navegue pelo menu para acessar as diferentes funcionalidades
3. Use os filtros de busca para localizar registros
4. Gere relatórios em PDF pela seção de relatórios

### Endpoints da API (Dashboard)

```bash
# Membros cadastrados mensalmente
GET /dashboard/numero-irmaos-cadastrados-mensalmente

# Orçamento por departamento
GET /dashboard/orcamento-departamento

# Pedidos de saída por semana
GET /dashboard/pedido-saida-semana

# Dízimos e ofertas
GET /dashboard/dizimo-oferta

# Crescimento de membros
GET /dashboard/crescimento-membros
```

### Relatórios PDF

```bash
# Relatório de membros
GET /relatorios/irmaos/pdf/

# Relatório de dízimos
GET /relatorios/dizimos/pdf/

# Relatório de departamentos
GET /relatorios/departamentos/pdf/

# Relatório de patrimônio
GET /relatorios/inventario_patrimonio/pdf/
```

## 📚 Documentação

O projeto conta com documentação completa e detalhada:

- **[REQUISITOS.md](docs/REQUISITOS.md)** - Documentação de Requisitos
  - Requisitos funcionais e não-funcionais
  - Casos de uso
  - Regras de negócio
  - Limitações e próximas funcionalidades

- **[DOCUMENTACAO_TECNICA.md](docs/DOCUMENTACAO_TECNICA.md)** - Documentação Técnica
  - Arquitetura do sistema
  - Modelos de dados
  - Estrutura de views e forms
  - Configurações e deployment
  - Troubleshooting

- **[GITHUB_FLOW.md](docs/GITHUB_FLOW.md)** - Guia de Contribuição
  - Workflow de desenvolvimento
  - Padrões de branches e commits
  - Processo de Pull Request
  - Code review guidelines
  - CI/CD

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Por favor, siga o fluxo de trabalho descrito em [GITHUB_FLOW.md](docs/GITHUB_FLOW.md).

### Resumo do Processo:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrão de Commits

Seguimos o [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: adiciona nova funcionalidade
fix: corrige bug
docs: atualiza documentação
style: formatação de código
refactor: refatoração
test: adiciona testes
chore: manutenção
```

## 🐛 Reportar Bugs

Encontrou um bug? Por favor, abra uma issue com:
- Descrição detalhada do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Screenshots (se aplicável)
- Ambiente (OS, navegador, versão Django)

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Equipe

- **Desenvolvedores**: 
- **Organização**: Terceira Igreja Baptista de Luanda (TIBL)

## 📞 Contato

- **Email**: geral@tibl.ao
- **Website**: [https://gestao.tibl.ao](https://gestao.tibl.ao)

## 🙏 Agradecimentos

- Comunidade Django
- Todos os contribuidores do projeto
- Igreja Batista do Senhor - TIBL

## 📅 Changelog

### [1.0.0] - 2026-02-06

#### Adicionado
- Sistema completo de gestão de membros
- Controle financeiro integrado
- Gestão de atividades e escalas
- Sistema de notificações automáticas
- Dashboards e relatórios em PDF
- Gestão de patrimônio
- Relatórios de células
- Sistema de comunicação

---

**Desenvolvido com ❤️ para a Terceira Igreja Baptista de Luanda - TIBL**
