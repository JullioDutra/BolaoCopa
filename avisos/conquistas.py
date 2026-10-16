"""
Conquistas (troféus de perfil). Cada uma tem uma regra simples calculada do banco; `checar(usuario)` desbloqueia
o que faltar, dá uma recompensa em Cartola Coins e avisa (caixa de entrada + feed). Idempotente e à prova de falha.
"""
import logging
from collections import OrderedDict

from django.db.models import Max

from accounts import coins

from . import atividade, servico
from .models import Conquista

logger = logging.getLogger(__name__)
RECOMPENSA = 25

# slug -> (nome, descrição, ícone FontAwesome, cor)
CATALOGO = OrderedDict([
    ('estreante', ('Estreante', 'Fez o primeiro palpite', 'fa-futbol', '#16a34a')),
    ('cravador', ('Cravador', 'Cravou um placar exato', 'fa-bullseye', '#dc2626')),
    ('mestre_placares', ('Mestre dos Placares', 'Cravou 5 placares exatos', 'fa-crosshairs', '#b91c1c')),
    ('pe_quente', ('Pé-quente', 'Acertou 10 palpites', 'fa-fire', '#ea580c')),
    ('fiel', ('Fiel', '7 dias seguidos no app', 'fa-calendar-check', '#0891b2')),
    ('maratonista', ('Maratonista', '30 dias seguidos no app', 'fa-person-running', '#0e7490')),
    ('torcedor', ('Torcedor de Carteirinha', 'Escolheu o time do coração', 'fa-heart', '#e11d48')),
    ('perfil_vip', ('Perfil VIP', 'Completou o perfil', 'fa-id-card', '#4f46e5')),
    ('apostador', ('Apostador', 'Fez a primeira aposta nos Melhores do Ano', 'fa-ticket', '#d97706')),
    ('zebreiro', ('Zebreiro', 'Ganhou uma aposta com odd 6 ou mais', 'fa-horse-head', '#7c3aed')),
    ('multipla_ouro', ('Múltipla de Ouro', 'Ganhou uma múltipla', 'fa-layer-group', '#ca8a04')),
    ('eleitor', ('Eleitor', 'Votou no 11 ideal', 'fa-check-to-slot', '#2563eb')),
    ('professor', ('Professor', 'Abriu uma votação de comparativo', 'fa-chalkboard-user', '#0d9488')),
    ('banqueiro', ('Banqueiro', 'Juntou 2000 Cartola Coins', 'fa-sack-dollar', '#65a30d')),
    ('tecnico', ('Professor Pardal', 'Terminou uma partida do 7 a 0', 'fa-clipboard-user', '#0f766e')),
    ('goleador_7a0', ('Goleada Histórica', 'Venceu o 7 a 0 por 4 ou mais gols', 'fa-explosion', '#c2410c')),
    ('sete_a_zero', ('Sete a Zero!', 'Venceu um jogo por 7 gols de diferença', 'fa-7', '#b91c1c')),
    ('rei_da_copa', ('Rei da Copa do Brasil', 'Foi campeão do draft do 7 a 0', 'fa-crown', '#b45309')),
    ('campeao_mundo', ('Campeão do Mundo', 'Venceu a Busca pelo Mundial do 7 a 0', 'fa-earth-americas', '#1d4ed8')),
    ('sete_vitorias', ('7 a 0 de Verdade', 'Campeão do draft sem perder e sem pênaltis', 'fa-medal', '#be123c')),
    ('campeao_7a0', ('Campeão dos Campeões', 'Ganhou um campeonato do 7 a 0', 'fa-trophy', '#a16207')),
    ('apito_inicial', ('Apito Inicial', 'Terminou uma partida do Apito Final', 'fa-flag', '#a16207')),
    ('arbitro_fifa', ('Árbitro FIFA', 'Acertou 8 ou mais lances numa partida do Apito Final', 'fa-earth-americas', '#0f766e')),
    ('apito_de_ouro', ('Apito de Ouro', 'Acertou os 10 lances numa partida do Apito Final', 'fa-crown', '#ca8a04')),
    ('detetive', ('Detetive', 'Descobriu o craque do dia no Quem Sou Eu?', 'fa-user-secret', '#6d28d9')),
    ('faro_de_gol', ('Faro Apurado', 'Descobriu o craque do dia com 5 perguntas ou menos', 'fa-magnifying-glass', '#7c3aed')),
    ('craque_campeao', ('Craque Campeão', 'Foi campeão com seu jogador no Vida de Craque', 'fa-shirt', '#c2410c')),
    ('cabecudo_rei', ('Rei dos Cabeçudos', 'Venceu O Fenômeno na final do Cabeçudos', 'fa-futbol', '#15803d')),
])


def _setezero(u):
    """ Números do jogo 7 a 0 (tolerante a tabela ainda não migrada). """
    try:
        from setezero.models import DraftCopa7a0, Partida7a0, Temporada7a0
        fim = Partida7a0.objects.filter(usuario=u, resultado__in=['V', 'E', 'D'])
        saldos = [p.gols_usuario - p.gols_rival for p in fim]
        return {'jogos': len(saldos), 'maior_saldo': max(saldos, default=0),
                'titulos': Temporada7a0.objects.filter(usuario=u, posicao_final=1).count(),
                'copas': DraftCopa7a0.objects.filter(usuario=u, status='campeao', torneio='brasil').count(),
                'mundiais': DraftCopa7a0.objects.filter(usuario=u, status='campeao', torneio='mundial').count(),
                'invictos': DraftCopa7a0.objects.filter(usuario=u, invicto=True).count()}
    except Exception:
        return {'jogos': 0, 'maior_saldo': 0, 'titulos': 0, 'copas': 0, 'mundiais': 0, 'invictos': 0}


def _arbitro(u):
    """ Melhor número de acertos numa partida do Apito Final (tolerante a tabela ainda não migrada). """
    try:
        from arbitro.models import PartidaArbitro
        fim = PartidaArbitro.objects.filter(usuario=u, status='fim')
        return {'jogos': fim.count(), 'max_acertos': fim.aggregate(m=Max('acertos'))['m'] or 0}
    except Exception:
        return {'jogos': 0, 'max_acertos': 0}


def _jogos_ia(u):
    """ Quem Sou Eu?, Vida de Craque e Cabeçudos (tolerante a tabelas ainda não migradas). """
    r = {'detetive': False, 'faro': False, 'craque_campeao': False, 'cabecudo_rei': False}
    try:
        from quemsoueu.models import PartidaQSE
        acertos = list(PartidaQSE.objects.filter(usuario=u, modo='diario', status='acertou').values_list('perguntas', flat=True))
        r['detetive'] = bool(acertos)
        r['faro'] = any(len(p) <= 5 for p in acertos)
    except Exception:
        pass
    try:
        from craque.models import Carreira
        r['craque_campeao'] = any(c.get('carreira', {}).get('titulos') for c in Carreira.objects.filter(usuario=u).values_list('estado', flat=True))
    except Exception:
        pass
    try:
        from cabecudos.fases import FASES
        from cabecudos.models import PartidaCabecudos
        r['cabecudo_rei'] = PartidaCabecudos.objects.filter(usuario=u, status='vitoria', fase=len(FASES)).exists()
    except Exception:
        pass
    return r


def _regras(u):
    from accounts.models import PerfilUsuario
    from futebol.models import Comparativo, Voto
    from melhores.models import Aposta, Multipla
    from palpites.models import Palpite

    palpites = Palpite.objects.filter(usuario=u)
    exatos = palpites.filter(pontuacao_obtida=15).count()
    perfil = PerfilUsuario.objects.filter(usuario=u).first()
    saldo = coins.saldo(u)
    sete = _setezero(u)
    apito = _arbitro(u)
    novos = _jogos_ia(u)
    return {
        'detetive': novos['detetive'],
        'faro_de_gol': novos['faro'],
        'craque_campeao': novos['craque_campeao'],
        'cabecudo_rei': novos['cabecudo_rei'],
        'apito_inicial': apito['jogos'] > 0,
        'arbitro_fifa': apito['max_acertos'] >= 8,
        'apito_de_ouro': apito['max_acertos'] >= 10,
        'tecnico': sete['jogos'] > 0,
        'goleador_7a0': sete['maior_saldo'] >= 4,
        'sete_a_zero': sete['maior_saldo'] >= 7,
        'campeao_7a0': sete['titulos'] > 0,
        'rei_da_copa': sete['copas'] > 0,
        'campeao_mundo': sete['mundiais'] > 0,
        'sete_vitorias': sete['invictos'] > 0,
        'estreante': palpites.exists(),
        'cravador': exatos >= 1,
        'mestre_placares': exatos >= 5,
        'pe_quente': palpites.filter(pontuacao_obtida__gt=0).count() >= 10,
        'fiel': bool(perfil and perfil.maior_streak >= 7),
        'maratonista': bool(perfil and perfil.maior_streak >= 30),
        'torcedor': bool(perfil and perfil.time_coracao_id),
        'perfil_vip': bool(perfil and perfil.perfil_completo),
        'apostador': Aposta.objects.filter(usuario=u).exists() or Multipla.objects.filter(usuario=u).exists(),
        'zebreiro': (Aposta.objects.filter(usuario=u, status='ganha').aggregate(m=Max('odd_travada'))['m'] or 0) >= 6,
        'multipla_ouro': Multipla.objects.filter(usuario=u, status='ganha').exists(),
        'eleitor': Voto.objects.filter(usuario=u).exists(),
        'professor': Comparativo.objects.filter(criador=u).exists(),
        'banqueiro': saldo >= 2000,
    }


def checar(usuario):
    """ Desbloqueia o que o usuário já merece. Devolve a lista de slugs novos. Nunca levanta exceção. """
    try:
        ja = set(Conquista.objects.filter(usuario=usuario).values_list('slug', flat=True))
        novos = []
        for slug, cumpriu in _regras(usuario).items():
            if cumpriu and slug not in ja:
                _, criada = Conquista.objects.get_or_create(usuario=usuario, slug=slug)
                if criada:
                    novos.append(slug)
        for slug in novos:
            nome, descricao, _, _ = CATALOGO[slug]
            coins.creditar(usuario, RECOMPENSA, f"🏅 Conquista: {nome}")
            servico.notificar(usuario, f"🏅 Conquista desbloqueada: {nome}", f"{descricao}. +{RECOMPENSA} Cartola Coins!",
                              url='/conta/perfil/', tipo='conquista', chave=f'conquista:{slug}')
            atividade.registrar(usuario, 'conquista', f"{atividade.nome_publico(usuario)} desbloqueou “{nome}”")
        return novos
    except Exception as erro:
        logger.warning("Falha ao checar conquistas de %s: %s", getattr(usuario, 'pk', '?'), erro)
        return []


def do_usuario(usuario):
    """ Lista para exibir no perfil: todas as conquistas, marcando quais já foram desbloqueadas. """
    ganhas = {c.slug: c.desbloqueada_em for c in Conquista.objects.filter(usuario=usuario)}
    return [{'slug': slug, 'nome': n, 'descricao': d, 'icone': i, 'cor': c, 'em': ganhas.get(slug), 'ganha': slug in ganhas}
            for slug, (n, d, i, c) in CATALOGO.items()]
