import re

from django import template

register = template.Library()


@register.filter
def sem_emoji(texto):
    """ Tira emoji/símbolos do começo ("🎯 CRAVOU!" -> "CRAVOU!"); o ícone do tipo já aparece ao lado. """
    limpo = re.sub(r'^[^\w¡¿"“]+', '', str(texto or '')).strip()
    return limpo or texto
