"""Padroniza posições vindas de qualquer fonte (inglês, português, siglas) em GOL/DEF/MEI/ATA."""
import unicodedata

POSICOES = [('GOL', 'Goleiro'), ('DEF', 'Defensor'), ('MEI', 'Meio-campista'), ('ATA', 'Atacante')]
NOME_POSICAO = dict(POSICOES)
ORDEM_POSICAO = {'GOL': 0, 'DEF': 1, 'MEI': 2, 'ATA': 3}


def _limpar(texto):
    sem_acento = unicodedata.normalize('NFKD', texto or '').encode('ascii', 'ignore').decode('ascii')
    return sem_acento.strip().lower()


def mapear_posicao(texto):
    """ 'Defensive Midfield' -> MEI, 'Centre-Back' -> DEF, 'Atacante' -> ATA. '' se não reconhecer. """
    t = _limpar(texto)
    if not t:
        return ''
    if t in ('g', 'gk', 'gol') or 'goalkeep' in t or 'goleir' in t or 'keeper' in t:
        return 'GOL'
    # meio vem antes de defesa: "Defensive Midfield" é meio-campo
    if t in ('m', 'mf', 'mei') or any(k in t for k in ('mid', 'meia', 'meio', 'volante')):
        return 'MEI'
    if t in ('d', 'df', 'def', 'cb', 'lb', 'rb', 'zag') or any(k in t for k in ('defen', 'back', 'zagueir', 'later', 'libero')):
        return 'DEF'
    if t in ('f', 'fw', 'a', 'ata', 'st', 'cf', 'lw', 'rw') or any(
            k in t for k in ('forward', 'attack', 'offence', 'offense', 'striker', 'wing', 'atac', 'ponta', 'centroavante')):
        return 'ATA'
    return ''
