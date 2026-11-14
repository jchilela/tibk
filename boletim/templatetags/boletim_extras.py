from django import template
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe

from boletim.htmlutil import parece_html, sanitizar_campo

register = template.Library()


@register.filter(name='formatado', is_safe=True)
def formatado(valor):
    """Mostra HTML limitado já limpo, ou texto simples com as quebras de linha."""
    if not valor:
        return ''
    if parece_html(valor):
        return mark_safe(sanitizar_campo(valor))
    return mark_safe(linebreaks(valor, autoescape=True))
