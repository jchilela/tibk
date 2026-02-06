from django import template
import random
register = template.Library()



@register.simple_tag
def random_number(min_value, max_value):
    return random.randint(min_value, max_value)
