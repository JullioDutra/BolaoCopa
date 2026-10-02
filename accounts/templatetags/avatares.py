from django import template
from django.utils.html import format_html

from accounts import avatares

register = template.Library()


@register.simple_tag
def avatar(codigo, tamanho=40):
    """ {% avatar perfil.avatar 48 %} -> círculo colorido com o ícone do avatar. """
    i = avatares.info(codigo or avatares.PADRAO)
    tamanho = int(tamanho)
    return format_html(
        '<span class="av-ico" title="{}" style="width:{}px;height:{}px;font-size:{}px;background:{}"><i class="fa-solid {}"></i></span>',
        i['nome'], tamanho, tamanho, int(tamanho * 0.48), i['cor'], i['icone'])
