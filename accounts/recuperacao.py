"""
Recuperação de senha por dados do participante.

O usuário informa o e-mail e prova que é ele com UM dos dados do cadastro:
  * o WhatsApp cadastrado, ou
  * a resposta da pergunta secreta que ele escolheu no perfil.
Se acertar, recebe um token assinado (vale 15 min, uso único) para criar a nova senha.
Tentativas erradas são limitadas por e-mail e por IP para impedir "chutes" em massa.
"""
from django.contrib.auth.models import User
from django.core import signing
from django.core.cache import cache

from . import dados
from .models import PerfilUsuario

MAX_TENTATIVAS = 5
JANELA_SEGUNDOS = 15 * 60
VALIDADE_TOKEN = 15 * 60
SAL = 'recuperacao-senha'


class Bloqueado(Exception):
    pass


def _chaves(email, ip):
    return [f"rec:email:{(email or '').strip().lower()}", f"rec:ip:{ip or '?'}"]


def _verificar_limite(email, ip):
    if any(cache.get(c, 0) >= MAX_TENTATIVAS for c in _chaves(email, ip)):
        raise Bloqueado("Muitas tentativas. Aguarde 15 minutos ou peça um link à staff.")


def _registrar_falha(email, ip):
    for chave in _chaves(email, ip):
        try:
            cache.incr(chave)
        except ValueError:
            cache.set(chave, 1, JANELA_SEGUNDOS)


def verificar(email, telefone, pergunta, resposta, ip=None):
    """
    Devolve o usuário se algum dado confere; None caso contrário (mensagem sempre genérica
    para não revelar se o e-mail existe). Levanta Bloqueado se estourou o limite.
    """
    _verificar_limite(email, ip)
    usuario = User.objects.filter(username__iexact=(email or '').strip(), is_active=True).first()
    perfil = PerfilUsuario.objects.filter(usuario=usuario).first() if usuario else None

    ok = False
    if perfil:
        if telefone:
            try:
                ok = bool(perfil.telefone) and dados.normalizar_telefone(telefone) == perfil.telefone
            except ValueError:
                ok = False
        if not ok and pergunta and resposta:
            ok = (perfil.pergunta_secreta == pergunta
                  and dados.resposta_confere(resposta, perfil.resposta_secreta_hash))
    if not ok:
        _registrar_falha(email, ip)
        return None
    for chave in _chaves(email, ip):
        cache.delete(chave)
    return usuario


def gerar_token(usuario):
    # Inclui um pedaço do hash da senha: ao trocar a senha o token deixa de valer (uso único)
    return signing.dumps({'u': usuario.pk, 'p': usuario.password[-12:]}, salt=SAL)


def usuario_do_token(token):
    try:
        info = signing.loads(token, salt=SAL, max_age=VALIDADE_TOKEN)
    except signing.BadSignature:
        return None
    usuario = User.objects.filter(pk=info.get('u'), is_active=True).first()
    if usuario and usuario.password[-12:] == info.get('p'):
        return usuario
    return None
