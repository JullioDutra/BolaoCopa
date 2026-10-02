"""
Avatares de perfil: ícones (FontAwesome) em vez de emojis.
Os básicos são livres; os demais são desbloqueados pelas conquistas. O código tem no máximo 8 caracteres
(cabe no campo `PerfilUsuario.avatar`, sem migração). Valores antigos (emojis) viram o avatar padrão.
"""
from collections import OrderedDict

PADRAO = 'bola'

# código -> (nome, ícone, cor, conquista que desbloqueia | None)
LIVRES = OrderedDict([
    ('bola', ('Bola', 'fa-futbol', '#16a34a')),
    ('chuteira', ('Chuteira', 'fa-shoe-prints', '#0ea5e9')),
    ('luva', ('Luva', 'fa-hand', '#f59e0b')),
    ('camisa', ('Camisa 10', 'fa-shirt', '#e11d48')),
    ('estadio', ('Estádio', 'fa-landmark', '#64748b')),
    ('apito', ('Megafone', 'fa-bullhorn', '#475569')),
    ('rede', ('Rede', 'fa-bullseye', '#7c3aed')),
])

# conquista (slug) -> código do avatar liberado
POR_CONQUISTA = {
    'estreante': 'estreant', 'cravador': 'cravador', 'mestre_placares': 'mestre', 'pe_quente': 'pequente', 'fiel': 'fiel',
    'maratonista': 'maraton', 'torcedor': 'torcedor', 'perfil_vip': 'vip', 'apostador': 'apostad', 'zebreiro': 'zebra',
    'multipla_ouro': 'multipla', 'eleitor': 'eleitor', 'professor': 'professo', 'banqueiro': 'banco', 'tecnico': 'tecnico',
    'goleador_7a0': 'goleada', 'sete_a_zero': 'seteazer', 'campeao_7a0': 'campeao', 'rei_da_copa': 'reicopa',
    'sete_vitorias': 'invicto', 'campeao_mundo': 'mundo',
}


def catalogo():
    """ OrderedDict código -> dict(nome, icone, cor, conquista). Monta os desbloqueáveis a partir do catálogo de conquistas. """
    from avisos.conquistas import CATALOGO
    itens = OrderedDict()
    for codigo, (nome, icone, cor) in LIVRES.items():
        itens[codigo] = {'codigo': codigo, 'nome': nome, 'icone': icone, 'cor': cor, 'conquista': None, 'dica': 'Livre'}
    for slug, codigo in POR_CONQUISTA.items():
        if slug in CATALOGO:
            nome, descricao, icone, cor = CATALOGO[slug]
            itens[codigo] = {'codigo': codigo, 'nome': nome, 'icone': icone, 'cor': cor, 'conquista': slug, 'dica': descricao}
    return itens


def normalizar(codigo):
    return codigo if codigo in catalogo() else PADRAO


def liberados(usuario):
    """ Conjunto de códigos que o usuário pode usar (livres + conquistas desbloqueadas). """
    from avisos.models import Conquista
    ganhas = set(Conquista.objects.filter(usuario=usuario).values_list('slug', flat=True))
    return {c for c, i in catalogo().items() if i['conquista'] is None or i['conquista'] in ganhas}


def do_usuario(usuario):
    """ Lista para a tela de perfil, com `liberado` marcado. """
    ok = liberados(usuario)
    return [{**i, 'liberado': i['codigo'] in ok} for i in catalogo().values()]


def info(codigo):
    return catalogo()[normalizar(codigo)]
