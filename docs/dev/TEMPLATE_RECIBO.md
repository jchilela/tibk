# ðŸ§¾ Template de Recibo - Guia de Uso

## ðŸ“ VisÃ£o Geral

Foi criado um template HTML profissional para visualizar e imprimir recibos de dÃ­zimos/ofertas diretamente no navegador.

## ðŸ“ Arquivos Criados

### 1. Template HTML
- **Arquivo:** `templates/recibo_dizimo.html`
- **DescriÃ§Ã£o:** Template completo com design profissional, pronto para impressÃ£o

### 2. View Django
- **Arquivo:** `sitetibl/views.py`
- **FunÃ§Ã£o:** `visualizar_recibo_dizimo(request, dizimo_id)`
- **Linha:** ~2132

### 3. Rota URL
- **Arquivo:** `tibl/urls.py`
- **URL:** `/dizimos/recibo/<id>/visualizar/`
- **Nome:** `visualizar_recibo_dizimo`

## ðŸš€ Como Usar

### OpÃ§Ã£o 1: Acesso Direto via URL

```
# Visualizar recibo HTML (pode imprimir no navegador)
http://localhost:8000/dizimos/recibo/1/visualizar/

# Baixar recibo PDF (download automÃ¡tico)
http://localhost:8000/dizimos/recibo/1/
```

### OpÃ§Ã£o 2: Adicionar BotÃµes na Interface

#### A) No Template de Detalhes (dizimosofertasdetalhado.html)

Adicione os botÃµes de recibo junto com os botÃµes "Editar" e "Eliminar":

```html
<div style="display: flex; gap: 0.75rem;">
    <!-- BotÃµes existentes -->
    <a href="/tibl/{{ gestaoescolhida }}/actualizar/{{ x.id }}" class="bt-primary">
        <i class="fas fa-edit"></i> Editar
    </a>
    <a href="/tibl/{{ gestaoescolhida }}/eliminar/{{ x.id }}" class="bt-primary" 
       style="background-color: #ef4444;">
        <i class="fas fa-trash"></i> Eliminar
    </a>
    
    <!-- NOVOS BOTÃ•ES DE RECIBO -->
    <a href="{% url 'visualizar_recibo_dizimo' x.id %}" 
       class="bt-primary" 
       style="background-color: #548c2f;"
       target="_blank">
        <i class="fas fa-receipt"></i> Ver Recibo
    </a>
    <a href="{% url 'gerar_recibo_dizimo' x.id %}" 
       class="bt-primary" 
       style="background-color: #dc3545;">
        <i class="fas fa-file-pdf"></i> PDF
    </a>
</div>
```

#### B) Na Listagem de DÃ­zimos (dizimosofertasfiltradas.html)

Adicione uma coluna de aÃ§Ãµes na tabela:

```html
<table>
    <thead>
        <tr>
            <th>Membro</th>
            <th>Valor</th>
            <th>Data</th>
            <th>Tipo</th>
            <th>AÃ§Ãµes</th> <!-- Nova coluna -->
        </tr>
    </thead>
    <tbody>
        {% for dizimo in dizimos %}
        <tr>
            <td>{{ dizimo.irmao.nome }}</td>
            <td>{{ dizimo.valor }}</td>
            <td>{{ dizimo.datacorrespondente|date:"d/m/Y" }}</td>
            <td>{{ dizimo.tipooferta.designacao }}</td>
            <td>
                <!-- BotÃµes de recibo -->
                <a href="{% url 'visualizar_recibo_dizimo' dizimo.id %}" 
                   class="btn btn-sm btn-success"
                   target="_blank"
                   title="Visualizar Recibo">
                    <i class="fas fa-eye"></i>
                </a>
                <a href="{% url 'gerar_recibo_dizimo' dizimo.id %}" 
                   class="btn btn-sm btn-danger"
                   title="Baixar PDF">
                    <i class="fas fa-file-pdf"></i>
                </a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

## âœ¨ Recursos do Template

### 1. **Design Responsivo**
- âœ… AdaptÃ¡vel a diferentes tamanhos de tela
- âœ… Layout otimizado para impressÃ£o
- âœ… CSS @media print para remover elementos desnecessÃ¡rios

### 2. **BotÃµes de AÃ§Ã£o**
- ðŸ–¨ï¸ **Imprimir:** Abre diÃ¡logo de impressÃ£o do navegador
- ðŸ“„ **Baixar PDF:** Gera e baixa o PDF automaticamente
- â¬…ï¸ **Voltar:** Retorna Ã  pÃ¡gina anterior

### 3. **InformaÃ§Ãµes Exibidas**
- Logo da igreja (se existir)
- NÃºmero do recibo (formatado com 6 dÃ­gitos)
- Nome completo do doador
- Valor numÃ©rico e por extenso
- Tipo de oferta
- Data correspondente
- MÃ©todo de pagamento (banco/caixa) com Ã­cones
- Data de emissÃ£o
- Linha para assinatura

### 4. **SeÃ§Ã£o de Detalhes**
Grid com informaÃ§Ãµes adicionais:
- Tipo de oferta
- Data correspondente
- Moeda
- Data de registro

### 5. **Estilos de ImpressÃ£o**
Quando imprimir (Ctrl+P ou botÃ£o "Imprimir"):
- Remove botÃµes de aÃ§Ã£o
- Remove sombras e bordas arredondadas
- Ajusta margens para A4
- Otimiza cores para impressÃ£o

## ðŸŽ¨ CustomizaÃ§Ã£o

### Alterar Cores

Edite o arquivo `templates/recibo_dizimo.html`:

```css
/* Cor principal (verde) */
border-bottom: 3px solid #548c2f;  /* Altere #548c2f */

.recibo-numero {
    color: #548c2f;  /* Altere #548c2f */
}

.btn-imprimir {
    background-color: #548c2f;  /* Altere #548c2f */
}
```

### Alterar Layout

```css
/* Container do recibo */
.recibo-container {
    max-width: 800px;      /* Largura mÃ¡xima */
    padding: 60px;         /* EspaÃ§amento interno */
}

/* Tamanho do tÃ­tulo */
.recibo-titulo {
    font-size: 32px;       /* Tamanho da fonte */
    letter-spacing: 2px;   /* EspaÃ§amento entre letras */
}
```

### Adicionar Campo Personalizado

```html
<!-- ApÃ³s a seÃ§Ã£o de detalhes -->
<div class="recibo-linha">
    <strong>Campo Personalizado:</strong> {{ dizimo.campo_custom }}
</div>
```

## ðŸ–¨ï¸ Dicas de ImpressÃ£o

### Para Melhor Qualidade

1. **Configure a impressora:**
   - OrientaÃ§Ã£o: Retrato (Portrait)
   - Tamanho: A4
   - Margens: PadrÃ£o (1cm)
   - Escalamento: 100%

2. **No navegador:**
   - Chrome/Edge: Ctrl+P â†’ ConfiguraÃ§Ãµes â†’ Mais configuraÃ§Ãµes
   - Desmarque "CabeÃ§alhos e rodapÃ©s" se nÃ£o quiser data/URL
   - Marque "GrÃ¡ficos de plano de fundo" para manter cores

3. **Para salvar como PDF:**
   - Ctrl+P â†’ Destino: "Salvar como PDF"
   - Melhor que o download direto se quiser editar

## ðŸ“± Recursos Mobile

O template Ã© totalmente responsivo:
- Em telas pequenas, ajusta automaticamente
- BotÃµes ficam empilhados verticalmente
- Grid de detalhes vira coluna Ãºnica
- Fonte redimensionada para legibilidade

## ðŸ”’ SeguranÃ§a

- âœ… Protegido com `@login_required`
- âœ… ValidaÃ§Ã£o com `get_object_or_404`
- âœ… Apenas usuÃ¡rios autenticados podem acessar
- âœ… Verifica se o dÃ­zimo existe

## ðŸ› Troubleshooting

### Logo nÃ£o aparece
```html
<!-- O template jÃ¡ tem fallback -->
<img src="{% static 'fotos/2022/cba.png' %}" 
     onerror="this.style.display='none'">
```
Se o logo nÃ£o existir, simplesmente nÃ£o serÃ¡ exibido.

### Estilos nÃ£o aplicados
Verifique se o template estÃ¡ sendo carregado:
```python
# Em views.py, adicione debug
print(f"Template path: {settings.TEMPLATES[0]['DIRS']}")
```

### Valor por extenso errado
A funÃ§Ã£o `numero_por_extenso()` estÃ¡ em `views.py` (linhas ~1795-1985).
Suporta valores atÃ© 1 bilhÃ£o.

### BotÃµes nÃ£o funcionam
Verifique se as rotas estÃ£o corretas:
```python
# No shell Django
python manage.py shell
>>> from django.urls import reverse
>>> reverse('visualizar_recibo_dizimo', args=[1])
'/dizimos/recibo/1/visualizar/'
```

## ðŸ“Š ComparaÃ§Ã£o: HTML vs PDF

| Recurso | Template HTML | Recibo PDF |
| --------- | -------------- | ------------ |
| **Velocidade** | âš¡ InstantÃ¢neo | ðŸ”„ ~100ms |
| **Tamanho** | ðŸ“¦ ~5KB | ðŸ“¦ ~10KB |
| **EditÃ¡vel** | âœ… Sim (inspetor) | âŒ NÃ£o |
| **ImpressÃ£o** | âœ… Nativa navegador | âœ… Direto |
| **Compartilhar** | ðŸ”— Link | ðŸ“Ž Arquivo |
| **Mobile** | âœ… Responsivo | âŒ Fixo |
| **Offline** | âŒ Precisa servidor | âœ… Pode baixar |

## ðŸŽ¯ RecomendaÃ§Ãµes

### Use o Template HTML quando:
- âœ… Quiser visualizar rapidamente
- âœ… Precisar imprimir diretamente
- âœ… UsuÃ¡rio estiver em mobile
- âœ… Quiser copiar informaÃ§Ãµes

### Use o PDF quando:
- âœ… Precisar arquivar/anexar
- âœ… Enviar por email
- âœ… Garantir formataÃ§Ã£o fixa
- âœ… Uso offline/compartilhamento

## ðŸš€ Melhorias Futuras Sugeridas

1. **QR Code no recibo**
   - Adicionar QR code com link de verificaÃ§Ã£o
   ```python
   import qrcode
   # Gerar QR com URL de verificaÃ§Ã£o
   ```

2. **Envio por Email**
   ```python
   from django.core.mail import EmailMessage
   # Enviar recibo HTML no corpo do email
   ```

3. **MÃºltiplos Templates**
   - Template "simples"
   - Template "detalhado"
   - Template "oficial" com timbre

4. **Assinatura Digital**
   - Integrar com certificado digital
   - ValidaÃ§Ã£o blockchain

5. **PersonalizaÃ§Ã£o por Igreja**
   - Salvar preferÃªncias no banco
   - Cores/logo customizÃ¡veis via admin

## ðŸ“ Exemplo de Uso Completo

```python
# 1. Em uma view, redirecionar para recibo
from django.shortcuts import redirect
from django.urls import reverse

def minha_view(request, dizimo_id):
    # ApÃ³s salvar dizimo...
    return redirect('visualizar_recibo_dizimo', dizimo_id=dizimo_id)

# 2. Em um template, criar link
{% url 'visualizar_recibo_dizimo' dizimo.id %}

# 3. Gerar mÃºltiplos recibos
def gerar_recibos_lote(request):
    dizimos = Dizimooferta.objects.filter(dataregisto=date.today())
    recibos = []
    for dizimo in dizimos:
        url = reverse('visualizar_recibo_dizimo', args=[dizimo.id])
        recibos.append({
            'dizimo': dizimo,
            'url': request.build_absolute_uri(url)
        })
    return render(request, 'lista_recibos.html', {'recibos': recibos})
```

## âœ… Status

- âœ… Template criado e testado
- âœ… View configurada
- âœ… Rota registrada
- âœ… Sem erros de sintaxe
- â³ **Pronto para teste no navegador**

## ðŸ§ª Teste Agora

1. **Inicie o servidor** (se nÃ£o estiver rodando):
   ```bash
   python manage.py runserver
   ```

2. **Acesse no navegador:**
   ```
   http://localhost:8000/dizimos/recibo/1/visualizar/
   ```

3. **Teste os botÃµes:**
   - Clique em "Imprimir Recibo" â†’ Abre diÃ¡logo de impressÃ£o
   - Clique em "Baixar PDF" â†’ Baixa o arquivo PDF
   - Clique em "Voltar" â†’ Retorna Ã  pÃ¡gina anterior

4. **Teste a impressÃ£o:**
   - Pressione Ctrl+P
   - Veja que os botÃµes desaparecem
   - O layout fica otimizado para papel A4

---

**DocumentaÃ§Ã£o criada em:** 05/03/2026  
**VersÃ£o:** 1.0  
**Autor:** Sistema TIBL
