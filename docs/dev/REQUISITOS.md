# Documentação de Requisitos do Sistema TIBL

## 1. Visão Geral do Projeto

O Sistema TIBL (Terceira Igreja Baptista de Luanda) é uma plataforma de gestão integrada desenvolvida em Django para administrar todas as operações da igreja. O sistema centraliza a gestão de membros, finanças, patrimônio, atividades, departamentos e comunicação.

## 2. Objetivos do Sistema

- **Centralização da Informação**: Unificar todos os dados da igreja em uma única plataforma
- **Gestão Financeira**: Controlar entradas, saídas, dízimos, ofertas e contas bancárias
- **Gestão de Membros**: Cadastro completo de membros com histórico e informações detalhadas
- **Gestão de Atividades**: Organizar cultos, células, escalas e eventos
- **Controle Patrimonial**: Inventário e manutenção de bens da igreja
- **Comunicação**: Facilitar o envio de mensagens e notificações aos membros
- **Relatórios**: Gerar relatórios gerenciais e operacionais em PDF

## 3. Requisitos Funcionais

### 3.1 Gestão de Membros (Irmãos)

**RF001**: O sistema deve permitir o cadastro completo de membros com:
- Dados pessoais (nome, apelido, data de nascimento, sexo)
- Foto do membro
- Estado civil e escolaridade
- Profissão e especialidade
- Endereço completo (rua, bairro, município, província)
- Contatos (telefone, WhatsApp, email)
- Igreja/local de congregação
- Célula a que pertence
- Indicação se é dizimista
- Status de batismo
- Vinculação com usuário do sistema Django

**RF002**: O sistema deve permitir filtrar membros por diversos critérios (nome, província, célula, etc.)

**RF003**: O sistema deve exibir detalhes completos de cada membro

**RF004**: O sistema deve permitir atualizar e excluir cadastros de membros

**RF005**: O sistema deve validar que o telefone tenha exatamente 9 dígitos

### 3.2 Gestão de Departamentos

**RF006**: O sistema deve permitir cadastrar departamentos com:
- Designação e abreviação
- Descrição
- Líder e vice-líder do departamento
- Lista de integrantes

**RF007**: O sistema deve gerenciar mandatos de membros em departamentos com:
- Irmão associado
- Departamento
- Cargo ocupado
- Data de início e fim do mandato

**RF008**: O sistema deve impedir duplicação de mandatos (mesma combinação irmão-departamento-cargo-data início)

### 3.3 Gestão Financeira

#### 3.3.1 Contas Bancárias

**RF009**: O sistema deve cadastrar bancos com designação, abreviação, gestor e contatos

**RF010**: O sistema deve cadastrar contas bancárias com:
- Banco associado
- Número da conta e IBAN (únicos)
- Tipo de moeda
- Saldo atual
- Proprietário ou instituição associada

#### 3.3.2 Movimentações Financeiras

**RF011**: O sistema deve registrar entradas de caixa com:
- Valor e moeda
- Data e hora
- Responsável
- Rubrica de entrada
- Observações

**RF012**: O sistema deve registrar saídas de caixa com:
- Valor e moeda
- Data e hora
- Responsável
- Rubrica de saída
- Data de controlo automática
- Observações

**RF013**: O sistema deve registrar entradas bancárias com:
- Conta a ser creditada
- Valor, moeda, data e hora
- Via (depósito, transferência, multicaixa)
- Rubrica
- Conta de origem (se aplicável)
- Responsável e observações

**RF014**: O sistema deve registrar saídas bancárias com:
- Conta de débito
- Valor, moeda, data e hora
- Rubrica
- Conta destino (se aplicável)
- Responsável e observações

#### 3.3.3 Dízimos e Ofertas

**RF015**: O sistema deve registrar dízimos e ofertas com:
- Valor e moeda
- Tipo de oferta
- Data correspondente
- Membro dizimista
- Atividade associada (opcional)
- Vinculação com entrada bancária ou caixa
- Data de registro e controle automáticas

#### 3.3.4 Orçamento

**RF016**: O sistema deve gerenciar orçamento por departamento com:
- Departamento associado
- Valor do orçamento
- Moeda
- Ano de referência
- Datas de criação e atualização automáticas

**RF017**: O sistema deve processar pedidos de saída financeira com:
- Departamento solicitante
- Projeto/motivo
- Montante e moeda
- Centro de custo e tipificação
- Requerente
- IBAN de destino
- Justificativa e documento comprobatório
- Status de aprovação
- Aprovador
- Datas de criação e atualização

### 3.4 Gestão de Atividades

**RF018**: O sistema deve cadastrar tipos de atividades (cultos, células, eventos, etc.)

**RF019**: O sistema deve registrar atividades com:
- Tipo de atividade
- Data, hora de início e fim
- Tema
- Local
- Versículos bíblicos e hinos
- Total de participantes
- Observações

**RF020**: O sistema deve gerenciar escalas de participação em atividades:
- Irmão escalado
- Atividade
- Função a ser desempenhada
- Não permitir duplicação (mesma combinação irmão-atividade-função)

**RF021**: O sistema deve enviar notificações automáticas por email aos membros escalados:
- 2 dias antes da atividade
- 1 dia antes da atividade
- Detalhes da atividade, função e horário

### 3.5 Gestão de Células

**RF022**: O sistema deve gerenciar relatórios semanais de células com:
- Nome da célula
- Líder responsável
- Local da reunião
- Número de participantes (membros, visitantes, crianças)
- Momentos realizados
- Tema e versículo chave
- Resumo da mensagem
- Tópicos de oração
- Alvos e ações para próxima semana
- Observações e necessidades
- Assinatura do líder
- Data da reunião
- Datas de criação e atualização

### 3.6 Gestão de Patrimônio

**RF023**: O sistema deve gerenciar inventário de patrimônio com:
- Nome e descrição
- Categoria do bem
- Código único
- Quantidade
- Localização
- Preço e moeda
- Data de aquisição
- Responsável
- Foto do bem
- Estado (bom, regular, ruim, etc.)
- Observações
- Registro de danos
- Data da última e próxima manutenção
- Descrição da manutenção realizada
- Datas de criação e atualização

### 3.7 Gestão de Ajudas Sociais

**RF024**: O sistema deve cadastrar tipos de ajuda (saúde, falecimento, propina, cesta básica, casamento, outras)

**RF025**: O sistema deve registrar ajudas concedidas com:
- Tipo de ajuda
- Beneficiário
- Patrocinador (opcional)
- Valor
- Cesta básica associada (se aplicável)
- Data
- Vinculação com saída bancária ou caixa
- Observações

**RF026**: O sistema deve gerenciar cestas básicas com:
- Código único (data)
- Vinculação com saída bancária ou caixa
- Data de disponibilização do valor
- Observações

**RF027**: O sistema deve registrar composição das cestas:
- Produto
- Quantidade
- Preço unitário

### 3.8 Gestão de Conteúdo de Ensino

**RF028**: O sistema deve permitir upload de conteúdo de ensino com:
- Autor
- Título
- Arquivo
- Datas de criação e atualização

### 3.9 Comunicação

**RF029**: O sistema deve permitir envio de mensagens com:
- Conteúdo da mensagem
- Opções de envio (SMS e/ou Email)
- Registro de quem enviou
- Datas de criação e atualização

### 3.10 Dashboard e Relatórios

**RF030**: O sistema deve fornecer dashboard com:
- Número de irmãos cadastrados mensalmente
- Orçamento por departamento
- Pedidos de saída por dia da semana
- Conteúdo de ensino mensal
- Dízimos e ofertas
- Crescimento de membros

**RF031**: O sistema deve gerar relatórios em PDF:
- Relatório de membros
- Relatório de dízimos e ofertas
- Relatório de departamentos
- Relatório de escalas
- Relatório de atividades
- Relatório de inventário patrimonial
- Relatório de saídas de caixa

**RF032**: O sistema deve incluir logo da igreja nos relatórios PDF

### 3.11 Autenticação e Autorização

**RF033**: O sistema deve integrar com sistema de autenticação do Django

**RF034**: O sistema deve vincular membros da igreja com usuários do sistema

**RF035**: O sistema deve ter controle de permissões para diferentes funcionalidades

**RF036**: O sistema deve ter áreas restritas que exigem login

## 4. Requisitos Não-Funcionais

### 4.1 Performance

**RNF001**: O sistema deve paginar resultados em 20 registros por página

**RNF002**: O sistema deve utilizar cache Redis para melhorar performance

**RNF003**: O sistema deve utilizar Celery para processar tarefas em background (notificações)

### 4.2 Usabilidade

**RNF004**: O sistema deve ter interface web responsiva

**RNF005**: O sistema deve fornecer feedback visual para ações do usuário (mensagens de sucesso/erro)

**RNF006**: O sistema deve ter filtros de busca para facilitar localização de registros

### 4.3 Segurança

**RNF007**: O sistema deve validar dados de entrada (telefones, emails, datas)

**RNF008**: O sistema deve proteger contra CSRF attacks

**RNF009**: O sistema deve usar HTTPS em produção

**RNF010**: O sistema deve ter senhas criptografadas

**RNF011**: O sistema deve validar origens permitidas (CORS e CSRF_TRUSTED_ORIGINS)

### 4.4 Confiabilidade

**RNF012**: O sistema deve ter backup automático de dados

**RNF013**: O sistema deve registrar data de criação e atualização em entidades críticas

**RNF014**: O sistema deve ter integridade referencial no banco de dados

**RNF015**: O sistema deve impedir exclusão de registros vinculados (CASCADE, PROTECT)

### 4.5 Manutenibilidade

**RNF016**: O código deve seguir padrões Django (MVT - Model View Template)

**RNF017**: O sistema deve ter separação clara entre camadas (models, views, forms, templates)

**RNF018**: O sistema deve usar variáveis de ambiente para configurações sensíveis

**RNF019**: O sistema deve ter código comentado e auto-documentado

### 4.6 Portabilidade

**RNF020**: O sistema deve ser compatível com MySQL/MariaDB

**RNF021**: O sistema deve ter suporte a Docker para deploy

**RNF022**: O sistema deve funcionar em diferentes ambientes (desenvolvimento, produção)

**RNF023**: O sistema deve suportar diferentes fusos horários (configurado para Africa/Luanda)

### 4.7 Escalabilidade

**RNF024**: O sistema deve usar Celery Beat para agendamento de tarefas

**RNF025**: O sistema deve usar filas assíncronas para processamento (Redis)

**RNF026**: O sistema deve suportar múltiplas moedas (AKZ, USD, EUR, etc.)

**RNF027**: O sistema deve suportar múltiplas localizações (províncias de Angola)

## 5. Regras de Negócio

**RN001**: Um membro só pode ter um mandato ativo por vez no mesmo departamento

**RN002**: Contas bancárias devem ter número e IBAN únicos

**RN003**: Um membro não pode ser escalado duas vezes na mesma função na mesma atividade

**RN004**: Cestas básicas devem ter código único baseado em data

**RN005**: Todas as movimentações financeiras devem ter responsável identificado

**RN006**: Dízimos e ofertas devem estar vinculados a entrada bancária ou caixa

**RN007**: Ajudas devem estar vinculadas a saída bancária ou caixa

**RN008**: Notificações de escala devem ser enviadas automaticamente às 4h da manhã

**RN009**: O sistema deve diferenciar entre igrejas (tipo 1) e células (tipo 2)

**RN010**: Telefones devem ter exatamente 9 dígitos

## 6. Casos de Uso Principais

### UC001: Cadastrar Novo Membro
**Ator**: Administrador/Secretário
**Descrição**: Registrar um novo membro na igreja com todos os dados pessoais

### UC002: Registrar Dízimo
**Ator**: Tesoureiro
**Descrição**: Registrar entrada de dízimo de um membro vinculando à conta bancária ou caixa

### UC003: Criar Escala de Atividade
**Ator**: Líder de Departamento
**Descrição**: Escalar membros para funções específicas em atividades programadas

### UC004: Aprovar Pedido de Saída
**Ator**: Aprovador Financeiro
**Descrição**: Analisar e aprovar/rejeitar pedidos de saída financeira de departamentos

### UC005: Gerar Relatório Financeiro
**Ator**: Administrador/Tesoureiro
**Descrição**: Gerar relatório em PDF de movimentações financeiras

### UC006: Enviar Mensagem aos Membros
**Ator**: Líder/Comunicação
**Descrição**: Enviar mensagens em massa por email/SMS aos membros

### UC007: Registrar Relatório de Célula
**Ator**: Líder de Célula
**Descrição**: Preencher relatório semanal da reunião de célula

### UC008: Gerenciar Patrimônio
**Ator**: Administrador
**Descrição**: Cadastrar e acompanhar bens patrimoniais da igreja

## 7. Integrações

**INT001**: Sistema de email (SMTP - Gmail)
- Envio de notificações
- Lembretes de escalas
- Comunicação com membros

**INT002**: Sistema de arquivos
- Upload de fotos de membros
- Upload de documentos justificativos
- Upload de conteúdo de ensino
- Upload de fotos de patrimônio

**INT003**: Sistema de agendamento (Celery + Redis)
- Tarefas agendadas
- Notificações automáticas
- Processamento assíncrono

## 8. Tecnologias Utilizadas

- **Backend**: Django 4.2.5
- **Banco de Dados**: MySQL/MariaDB (com PyMySQL)
- **Cache**: Redis 5.0.1
- **Tarefas Assíncronas**: Celery 5.4.0 + django-celery-beat 2.8.1
- **Relatórios**: ReportLab 3.6.0+
- **Upload de Arquivos**: Pillow 10.1.0
- **Deploy**: Gunicorn 23.0.0 + Docker

## 9. Limitações Conhecidas

- Sistema configurado especificamente para Angola (províncias, moedas)
- Interface em português
- Validação de telefone específica para padrão angolano (9 dígitos)
- Workaround para MariaDB 10.4 (Django 4.2+ requer 10.5+)

## 10. Próximas Funcionalidades Sugeridas

- Sistema de presença em atividades
- Aplicativo mobile
- Sistema de permissões mais granular
- Integração com gateway de pagamento
- Sistema de doações online
- Portal do membro
- Gestão de salas/ambientes
- Calendário integrado
- Sistema de biblioteca
- Gestão de cursos e treinamentos
