from django import template

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name):
    if not hasattr(user, '_group_cache'):
        user._group_cache = set(user.groups.values_list('name', flat=True))
    return group_name in user._group_cache

@register.filter
def replace(value, arg):
    """
    Usage: {{ value|replace:"_, " }}
    """
    if not value or not isinstance(value, str): return value
    if ',' in arg:
        old, new = arg.split(',', 1)
    else:
        old = arg
        new = ''
    return value.replace(old, new)

@register.filter(name='dinheiro')
def dinheiro(value):
    """Formata um numero com separador de milhares (virgula) e 2 casas decimais (ponto).
    Ex: 1234567.89 -> 1,234,567.89
    """
    if value is None or value == '':
        return '0.00'
    try:
        val = float(value)
    except (TypeError, ValueError):
        return value
    return f'{val:,.2f}'

@register.filter(name='dinheiro_int')
def dinheiro_int(value):
    """Formata um numero inteiro com separador de milhares (virgula), sem decimais.
    Ex: 1234567 -> 1,234,567
    """
    if value is None or value == '':
        return '0'
    try:
        val = int(float(value))
    except (TypeError, ValueError):
        return value
    return f'{val:,}'
