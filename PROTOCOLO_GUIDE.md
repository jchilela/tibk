# Sistema de Protocolo - Guia de Utilização

## Visão Geral

O Sistema de Protocolo foi desenvolvido para organizar actividades da igreja, permitindo a criação de protocolos com atribuição de irmãos a diferentes funções e actividades. **Característica principal**: é possível substituir irmãos mesmo após a criação do protocolo.

---

## Fluxo de Utilização

### 1. Criar Novo Protocolo

**URL**: `/tibl/gestao/protocolo/criar`

**Passos**:
1. Preencha as informações básicas:
   - **Número de Protocolo**: Ex: `PROT-001-2026`
   - **Tipo**: Entrada, Saída ou Interno
   - **Assunto**: Título do protocolo
   - **Remetente**: Quem envia (informacional)
   - **Destinatário**: Quem recebe (informacional)
   - **Responsável**: Irmão responsável pelo protocolo
   - **Prioridade**: Baixa, Normal, Alta ou Urgente

2. Preencha descrição e observações (opcional)

3. **Selecione Escalas** (Opcional):
   - Escolha uma Actividade (carrega data automaticamente)
   - Selecione até 10 irmãos com checkboxes
   - Escolha a função/cargo para cada um
   - Adicione à lista

4. Clique em **"Criar Protocolo"**

---

### 2. Visualizar Detalhes do Protocolo

**URL**: `/tibl/gestao/protocolo/{id}`

**O que vê**:
- Informações completas do protocolo
- Status e prioridade (com badges coloridas)
- Remetente e destinatário
- Irmãos atribuídos às actividades (tabela)
- Data de entrada e processamento

**Ações disponíveis**:
- **Adicionar Irmão**: Novo botão para adicionar mais irmãos
- **Remover**: Cada irmão tem botão de remoção
- **Editar**: Modificar detalhes do protocolo
- **Eliminar**: Apagar protocolo completamente

---

### 3. Substituir Irmão (Edição Pós-Criação)

Para **substituir um irmão** que já foi atribuído:

1. Abra os detalhes do protocolo
2. Na tabela de "Irmãos Atribuídos às Actividades":
   - Clique no botão **"Remover"** ao lado do irmão a substituir
3. Clique em **"Adicionar Irmão"** na parte superior
4. Selecione o novo irmão e a sua função
5. Confirme

---

## Endpoints da API

### GET - Listar Irmãos
```
GET /tibl/api/irmaos/
```
Retorna lista JSON de todos os irmãos disponíveis.

### GET - Listar Actividades
```
GET /tibl/api/actividades/
```
Retorna lista JSON com `id`, `designacao` e `data` de cada actividade.

### GET - Listar Funções
```
GET /tibl/api/funcoes/
```
Retorna lista JSON de todas as funções/cargos disponíveis.

### POST - Adicionar Escalas
```
POST /tibl/protocolo/add-escalas/
Content-Type: application/json

{
  "actividade_id": 123,
  "irmao_ids": [1, 2, 3],
  "funcao_id": 456
}
```

### DELETE - Remover Escala
```
DELETE /tibl/protocolo/delete-escala/{escala_id}/
```

---

## Permissões Requeridas

| Operação | Permissão Django | Grupo(s) Permitido(s) |
|----------|------------------|----------------------|
| Ver protocolo | `view_protocolo` | Administrador, Financeiro, Secretaria, etc |
| Criar protocolo | `add_protocolo` | Administrador, Secretaria |
| Editar protocolo | `change_protocolo` | Administrador, Secretaria |
| Eliminar protocolo | `delete_protocolo` | Administrador |
| Adicionar escalas | `add_escala` | Administrador, Secretaria |
| Remover escalas | `delete_escala` | Administrador, Secretaria |

---

## Estrutura de Dados

### Protocolo
- `numero`: String única (Ex: "PROT-001-2026")
- `tipo`: "entrada", "saida", "interno"
- `assunto`: Texto do protocolo
- `status`: "novo", "em_processamento", "processado", "arquivado"
- `prioridade`: "baixa", "normal", "alta", "urgente"
- `remetente`: String informacional
- `destinatario`: String informacional
- `responsavel`: FK → Irmao
- `data_entrada`: DateTime (auto)
- `data_processamento`: DateTime (opcional)

### Escala
- `irmao`: FK → Irmao
- `actividade`: FK → Actividade
- `funcao`: FK → Funcao (opcional)
- Restrição: Única (irmao, actividade, funcao)

---

## Estrutura de Ficheiros

```
templates/
├── protocolo_form.html          # Formulário de criação
└── protocolodetalhado.html      # Página de detalhes

sitetibl/
├── forms.py                      # ProtocoloForm
├── views.py                      # Views e API endpoints
├── urls.py                       # Rotas
└── models.py                     # Modelos (Protocolo, Escala, etc)

Testes:
├── test_protocolo_integration.py # Suite de testes
└── validate_template.py          # Validador DTL
```

---

## DTL Template Tags Utilizadas

```django
{% load static %}           # Para assets estáticos
{% load verificagrupo %}    # Custom tag para has_group
{% if perms.sitetibl.xxx %} # Verificação de permissões
{% if request.user|has_group:"GroupName" %} # Grupo do utilizador
```

**Nota**: Este projeto usa **Django Template Language (DTL)**, não Jinja2.

---

## Troubleshooting

### "Escala não encontrada" ao remover
- Verifique se o ID da escala está correcto
- Verifique permissões do utilizador

### "Sem permissão" ao criar protocolo
- Verifique se o utilizador tem permissão `add_protocolo`
- Verifique se pertence a um grupo com esta permissão

### "Máximo de 10 irmãos" ao seleccionar
- O formulário só permite seleccionar até 10 irmãos por protocolo
- Para adicionar mais, crie outro protocolo ou aguarde por actualização

### Template não renderiza correctamente
- Execute: `python validate_template.py`
- Verifique se tags DTL estão balanceadas (if/endif, for/endfor, block/endblock)

---

## Suporte

Para dúvidas ou problemas:
1. Consulte os logs: `python manage.py runserver`
2. Execute validação: `python manage.py check`
3. Verifique permissões: Django Admin → Utilizadores → Grupos

---

**Versão**: 1.0  
**Última Actualização**: 11/05/2026  
**Status**: ✅ Testado e Pronto para Produção
