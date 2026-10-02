"""
Temas visuais por time do coração.

Cada tema define a cor principal (`base`, escura o bastante para texto branco por
cima), uma cor de destaque (`acento`) e um apelido/grito da torcida usado nas
saudações. Clubes que não estão na tabela usam a `cor_hexadecimal` cadastrada no
Admin; sem time, vale o tema verde clássico da Cartolândia.
"""
import re
import unicodedata

TEMA_PADRAO = {
    'chave': 'cartolandia',
    'nome': 'Cartolândia',
    'base': '#1b5e20',
    'acento': '#cfb53b',
    'apelido': 'Craque',
    'grito': 'Bora, Cartolândia!',
}

# chave normalizada do clube -> (base, acento, apelido, grito)
_TEMAS = {
    'flamengo':      ('#b3001b', '#f5f5f5', 'Nação Rubro-Negra', 'Mengooo!'),
    'corinthians':   ('#1c1c1c', '#f5f5f5', 'Fiel Torcida', 'Vai, Timão!'),
    'palmeiras':     ('#006437', '#e8f5e9', 'Alviverde', 'Avanti, Palestra!'),
    'sao paulo':     ('#c8102e', '#f5f5f5', 'Tricolor Paulista', 'Soberano!'),
    'santos':        ('#1c1c1c', '#f5f5f5', 'Alvinegro Praiano', 'Santos é Peixe!'),
    'vasco':         ('#1c1c1c', '#f5f5f5', 'Gigante da Colina', 'Vasco, Vasco!'),
    'botafogo':      ('#1c1c1c', '#f5f5f5', 'Glorioso', 'Fogão!'),
    'fluminense':    ('#7a0f2b', '#2e9b52', 'Tricolor das Laranjeiras', 'Fluuu!'),
    'gremio':        ('#0d6fb8', '#f5f5f5', 'Imortal Tricolor', 'Imortal!'),
    'internacional': ('#c8102e', '#f5f5f5', 'Colorado', 'Vamo, Inter!'),
    'cruzeiro':      ('#0b3a9c', '#f5f5f5', 'Nação Azul', 'Cabuloso!'),
    'atletico-mg':   ('#1c1c1c', '#f5f5f5', 'Massa Atleticana', 'Eu acredito!'),
    'bahia':         ('#1560bd', '#e53935', 'Esquadrão de Aço', 'Bora, Bahêa!'),
    'vitoria':       ('#b22222', '#1c1c1c', 'Rubro-Negro Baiano', 'Leão da Barra!'),
    'bragantino':    ('#c8102e', '#f5f5f5', 'Massa Bruta', 'Braga!'),
    'mirassol':      ('#1f7a3a', '#ffd400', 'Leão da Alta Paulista', 'Mirassol!'),
    'coritiba':      ('#00612b', '#f5f5f5', 'Coxa-Branca', 'Vamo, Coxa!'),
    'athletico-pr':  ('#b01f24', '#1c1c1c', 'Furacão', 'Furacão!'),
    'chapecoense':   ('#00873c', '#f5f5f5', 'Verdão do Oeste', 'Vai, Chape!'),
    'remo':          ('#002b7f', '#f5f5f5', 'Leão Azul', 'Remo!'),
}


def normalizar(nome):
    texto = unicodedata.normalize('NFKD', nome or '').encode('ascii', 'ignore').decode('ascii')
    return texto.strip().lower()


def _hex_para_rgb(cor):
    cor = cor.lstrip('#')
    if len(cor) == 3:
        cor = ''.join(c * 2 for c in cor)
    return tuple(int(cor[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_para_hex(rgb):
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def misturar(cor, com, proporcao):
    """ Mistura `cor` com `com` (hex). proporcao 0 = cor original, 1 = `com`. """
    a, b = _hex_para_rgb(cor), _hex_para_rgb(com)
    return _rgb_para_hex(tuple(x + (y - x) * proporcao for x, y in zip(a, b)))


def luminosidade(cor):
    r, g, b = (c / 255 for c in _hex_para_rgb(cor))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _montar(chave, nome, base, acento, apelido, grito, ativo=True):
    # Garante contraste com texto branco: cores claras são escurecidas
    base = base.lower()
    while luminosidade(base) > 0.35:
        base = misturar(base, '#000000', 0.25)
    return {
        'chave': chave,
        'ativo': ativo,  # False = tema padrão (nenhum CSS extra é injetado)
        'nome': nome,
        'base': base,
        'escura': misturar(base, '#000000', 0.45),
        'clara': misturar(base, '#ffffff', 0.25),
        'acento': acento,
        'apelido': apelido,
        'grito': grito,
    }


def tema_para_clube(clube):
    """ Devolve o dicionário de tema para um `palpites.Clube` (ou o padrão se None). """
    if clube is None:
        return tema_padrao()
    chave = normalizar(clube.nome)
    if chave in _TEMAS:
        base, acento, apelido, grito = _TEMAS[chave]
        return _montar(chave, clube.nome, base, acento, apelido, grito)
    cor = clube.cor_hexadecimal if re.fullmatch(r'#[0-9a-fA-F]{6}', clube.cor_hexadecimal or '') else '#1b5e20'
    return _montar(chave, clube.nome, cor, '#f5f5f5', 'Torcedor', f'Vamo, {clube.nome}!')


def tema_padrao():
    t = TEMA_PADRAO
    return _montar(t['chave'], t['nome'], t['base'], t['acento'], t['apelido'], t['grito'], ativo=False)
