"""Baralho do Super Trunfo: garante cartas suficientes (banco único de atletas + craques de referência)."""
import zlib

from .models import CartaTrunfo, ClubeFutebol

# (nome, posição, clube, overall)
CRAQUES = [
    ('Pelé', 'ATA', 'Santos', 99), ('Zico', 'MEI', 'Flamengo', 96), ('Romário', 'ATA', 'Vasco', 95),
    ('Ronaldo Fenômeno', 'ATA', 'Corinthians', 98), ('Ronaldinho Gaúcho', 'MEI', 'Grêmio', 95),
    ('Rivaldo', 'MEI', 'Palmeiras', 91), ('Cafu', 'DEF', 'São Paulo', 90), ('Roberto Carlos', 'DEF', 'Palmeiras', 90),
    ('Taffarel', 'GOL', 'Atlético-MG', 89), ('Dida', 'GOL', 'Corinthians', 86), ('Rogério Ceni', 'GOL', 'São Paulo', 90),
    ('Marcos', 'GOL', 'Palmeiras', 88), ('Neymar', 'ATA', 'Santos', 93), ('Kaká', 'MEI', 'São Paulo', 92),
    ('Falcão', 'MEI', 'Internacional', 90), ('Sócrates', 'MEI', 'Corinthians', 91), ('Júnior', 'DEF', 'Flamengo', 88),
    ('Leandro', 'DEF', 'Flamengo', 86), ('Gabigol', 'ATA', 'Flamengo', 87), ('Arrascaeta', 'MEI', 'Flamengo', 86),
    ('Hulk', 'ATA', 'Atlético-MG', 86), ('Dudu', 'ATA', 'Palmeiras', 85), ('Raphael Veiga', 'MEI', 'Palmeiras', 84),
    ('Fágner', 'DEF', 'Corinthians', 78), ('Cássio', 'GOL', 'Corinthians', 84), ('Fábio', 'GOL', 'Fluminense', 83),
    ('Ganso', 'MEI', 'Fluminense', 82), ('Fred', 'ATA', 'Fluminense', 84), ('Éverton Ribeiro', 'MEI', 'Bahia', 82),
    ('Tiago Silva', 'DEF', 'Fluminense', 87), ('Marquinhos', 'DEF', 'Corinthians', 85), ('Casemiro', 'MEI', 'São Paulo', 88),
    ('Vini Jr.', 'ATA', 'Flamengo', 90), ('Endrick', 'ATA', 'Palmeiras', 82), ('Raphinha', 'ATA', 'Leeds', 86),
    ('Alisson', 'GOL', 'Internacional', 89), ('Ederson', 'GOL', 'Atlético-MG', 88), ('Paulinho', 'MEI', 'Corinthians', 80),
    ('Everaldo', 'ATA', 'Grêmio', 80), ('Tite', 'MEI', 'Corinthians', 60),
]

# ritmo, finalização, passe, drible, defesa, físico — deslocamentos por posição sobre o overall
PERFIL = {
    'GOL': (-25, -45, -10, -35, +8, -2),
    'DEF': (-8, -25, -8, -18, +8, +6),
    'MEI': (-3, -8, +6, +4, -12, -5),
    'ATA': (+4, +8, -6, +5, -35, -4),
}
CAMPOS = ('ritmo', 'finalizacao', 'passe', 'drible', 'defesa', 'fisico')


def atributos(nome, posicao, overall):
    perfil = PERFIL.get(posicao, PERFIL['MEI'])
    base = zlib.crc32(nome.encode())
    valores = {}
    for i, (campo, off) in enumerate(zip(CAMPOS, perfil)):
        ruido = ((base >> (i * 4)) & 15) - 7  # -7..+8, estável por nome
        valores[campo] = max(15, min(99, overall + off + ruido))
    return valores


def _carta(nome, posicao, clube_nome, overall, foto=None):
    clube, _ = ClubeFutebol.objects.get_or_create(nome=clube_nome)
    carta = CartaTrunfo.objects.filter(nome=nome, clube=clube).first()
    if carta:
        return carta, False
    carta = CartaTrunfo(nome=nome, posicao=posicao, overall=overall, clube=clube, **atributos(nome, posicao, overall))
    if foto:
        carta.foto = foto
    carta.save()
    return carta, True


def garantir_cartas(minimo=10):
    """ Se o banco tem menos de `minimo` cartas, completa com atletas do banco único e depois com craques de referência. """
    faltam = minimo - CartaTrunfo.objects.count()
    if faltam <= 0:
        return 0
    criadas = 0
    try:
        from futebol.models import Atleta
        for a in Atleta.objects.filter(overall__isnull=False, time__isnull=False).select_related('time').order_by('-overall')[:200]:
            if criadas >= faltam:
                break
            _, novo = _carta(a.nome, a.posicao if a.posicao != 'DEF' else 'DEF', a.time.nome, a.overall, a.foto.name if a.foto else None)
            criadas += novo
    except Exception:
        pass
    for nome, pos, clube, ovr in CRAQUES:
        if criadas >= faltam:
            break
        _, novo = _carta(nome, pos, clube, ovr)
        criadas += novo
    return criadas
