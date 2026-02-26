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
