"""
Cliente da Claude compartilhado pelos jogos.

Regras da casa:
- Modelo barato (settings.IA_MODELO, padrão Claude Haiku 5.5), esforço baixo e resposta curta.
- Toda resposta é JSON validado por um schema (structured outputs), nunca texto livre para o código interpretar.
- Limite diário de chamadas por usuário (settings.IA_LIMITE_DIARIO), contado no banco.
- Sem chave, sem cota, ou com qualquer erro da API: devolve None e o jogo usa o texto pronto dele. A IA
  enfeita a experiência; nenhuma regra de jogo (placar, pontos, coins) depende dela.
"""
import json
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import UsoIA

logger = logging.getLogger(__name__)

TIMEOUT_S = 25.0
_cliente = None


def disponivel():
    return bool(getattr(settings, 'ANTHROPIC_API_KEY', None))


def _client():
    global _cliente
    if _cliente is None:
        import anthropic
        _cliente = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=TIMEOUT_S, max_retries=1)
    return _cliente


def limite():
    return getattr(settings, 'IA_LIMITE_DIARIO', 60)


def restantes(usuario):
    uso = UsoIA.objects.filter(usuario=usuario, dia=timezone.localdate()).first()
    return max(0, limite() - (uso.chamadas if uso else 0))


@transaction.atomic
def _reservar(usuario):
    uso, _ = UsoIA.objects.select_for_update().get_or_create(usuario=usuario, dia=timezone.localdate())
    if uso.chamadas >= limite():
        return None
    uso.chamadas += 1
    uso.save(update_fields=['chamadas'])
    return uso


def _contabilizar(uso, usage):
    if uso is None or usage is None:
        return
    UsoIA.objects.filter(pk=uso.pk).update(
        tokens_entrada=uso.tokens_entrada + (getattr(usage, 'input_tokens', 0) or 0),
        tokens_saida=uso.tokens_saida + (getattr(usage, 'output_tokens', 0) or 0),
    )


def gerar_json(usuario, system, mensagem, schema, max_tokens=2000, esforco='low'):
    """
    Pede à Claude um JSON no formato `schema` e devolve o dict, ou None (sem chave, sem cota, erro, recusa).
    `usuario` pode ser None para chamadas do sistema (não conta cota).
    """
    if not disponivel():
        return None
    uso = _reservar(usuario) if usuario is not None else None
    if usuario is not None and uso is None:
        return None
    import anthropic
    try:
        resposta = _client().messages.create(
            model=settings.IA_MODELO,
            max_tokens=max_tokens,
            system=system,
            messages=[{'role': 'user', 'content': mensagem}],
            output_config={'effort': esforco, 'format': {'type': 'json_schema', 'schema': schema}},
        )
    except anthropic.RateLimitError:
        logger.warning('IA: limite de requisições da Anthropic atingido')
        return None
    except anthropic.APIStatusError as e:
        logger.warning('IA: erro %s da API: %s', e.status_code, getattr(e, 'message', e))
        return None
    except anthropic.APIConnectionError as e:
        logger.warning('IA: falha de conexão: %s', e)
        return None
    _contabilizar(uso, getattr(resposta, 'usage', None))
    if resposta.stop_reason in ('refusal', 'max_tokens'):
        logger.info('IA: resposta descartada (%s)', resposta.stop_reason)
        return None
    texto = next((b.text for b in resposta.content if b.type == 'text'), None)
    try:
        return json.loads(texto) if texto else None
    except ValueError:
        return None


def schema(propriedades, obrigatorias=None):
    """ Atalho para um schema de objeto estrito. """
    return {'type': 'object', 'properties': propriedades,
            'required': obrigatorias or list(propriedades), 'additionalProperties': False}


def texto(maximo=None):
    s = {'type': 'string'}
    if maximo:
        s['description'] = f'no máximo {maximo} caracteres'
    return s


def enum(*valores):
    return {'type': 'string', 'enum': list(valores)}


def inteiro(minimo, maximo):
    return {'type': 'integer', 'description': f'entre {minimo} e {maximo}'}


def limitar(valor, minimo, maximo, padrao=0):
    """ Números vindos da IA nunca são confiáveis: sempre passam por aqui. """
    try:
        return max(minimo, min(maximo, int(valor)))
    except (TypeError, ValueError):
        return padrao


def cortar(valor, maximo):
    s = str(valor or '').strip()
    return s if len(s) <= maximo else s[:maximo - 1].rstrip() + '…'
