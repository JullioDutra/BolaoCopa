"""Cliente mínimo da API REST do Gemini (substitui google-generativeai, que pesa ~100 MB)."""
import json
import urllib.error
import urllib.request

from django.conf import settings

URL = 'https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={chave}'
MODELO_PADRAO = 'gemini-2.5-flash'


class RespostaIA:
    def __init__(self, texto):
        self.text = texto


class GeminiIndisponivel(Exception):
    pass


def gerar(prompt, formato_json=False, modelo=MODELO_PADRAO, timeout=15):
    chave = getattr(settings, 'GEMINI_API_KEY', None)
    if not chave:
        raise GeminiIndisponivel('GEMINI_API_KEY não configurada')
    corpo = {'contents': [{'parts': [{'text': prompt}]}]}
    if formato_json:
        corpo['generationConfig'] = {'responseMimeType': 'application/json'}
    req = urllib.request.Request(
        URL.format(modelo=modelo, chave=chave),
        data=json.dumps(corpo).encode(),
        headers={'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            dados = json.loads(r.read().decode())
        return RespostaIA(dados['candidates'][0]['content']['parts'][0]['text'])
    except (urllib.error.URLError, KeyError, IndexError, ValueError) as e:
        raise GeminiIndisponivel(str(e))


class _Modelo:
    def __init__(self, formato_json=False, modelo=MODELO_PADRAO):
        self.formato_json, self.modelo = formato_json, modelo

    def generate_content(self, prompt):
        return gerar(prompt, self.formato_json, self.modelo)


def obter_modelo(formato_json=False, modelo=MODELO_PADRAO):
    return _Modelo(formato_json, modelo)
