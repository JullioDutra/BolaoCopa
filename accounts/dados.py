"""Normalização e validação dos dados pessoais usados no perfil e na recuperação de senha."""
import re
import unicodedata

from django.contrib.auth.hashers import check_password, make_password


def normalizar_telefone(valor):
    """
    Devolve só dígitos com DDI. Aceita "(21) 98888-7777", "+55 21 98888-7777" etc.
    Retorna '' se o valor for vazio e levanta ValueError se não parecer um celular/telefone BR.
    """
    digitos = re.sub(r'\D', '', valor or '')
    if not digitos:
        if (valor or '').strip():
            raise ValueError("Informe o WhatsApp com DDD, ex.: (21) 98888-7777.")
        return ''
    if len(digitos) in (10, 11):          # sem DDI
        digitos = '55' + digitos
    if not (12 <= len(digitos) <= 13) or not digitos.startswith('55'):
        raise ValueError("Informe o WhatsApp com DDD, ex.: (21) 98888-7777.")
    return digitos


def telefone_formatado(digitos):
    if len(digitos or '') < 12:
        return digitos or ''
    ddd, resto = digitos[2:4], digitos[4:]
    return f"({ddd}) {resto[:-4]}-{resto[-4:]}"


def _normalizar_resposta(texto):
    sem_acento = unicodedata.normalize('NFKD', texto or '').encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]', '', sem_acento.lower())


def hash_resposta(texto):
    return make_password(_normalizar_resposta(texto))


def resposta_confere(texto, hash_guardado):
    normalizada = _normalizar_resposta(texto)
    return bool(normalizada and hash_guardado and check_password(normalizada, hash_guardado))
