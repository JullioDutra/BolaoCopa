"""
Lógica central do Ranking Geral do Bolão.
Usada tanto pela view 'ranking_geral' quanto pela action do admin 'finalizar_temporada',
para não duplicar a mesma regra em dois lugares.

Soma:
  - Pontos dos jogos normais do Bolão            -> Palpite.pontuacao_obtida
  - Pontos dos palpites de longo prazo            -> PalpiteLongoPrazo.pontos_obtidos
      (Campeão/G4/Z4 do Brasileirão + Campeão Europeu + Campeão Copa do Brasil)
  - Pontos da Seleção 4-3-3 do Brasileirão        -> SelecaoBrasileirao.pontuacao_total
"""
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from .models import Palpite, PalpiteLongoPrazo


def calcular_ranking_geral(temporada=None):
    # Import local para evitar import circular entre os apps palpites <-> convocacao
    from convocacao.models import SelecaoBrasileirao

    resultado = []

    usuarios_com_atividade = User.objects.filter(
        is_active=True
    ).distinct()

    for usuario in usuarios_com_atividade:
        palpites_usuario = Palpite.objects.filter(usuario=usuario)

        agregados_jogos = palpites_usuario.aggregate(
            total=Sum('pontuacao_obtida'),
            # AP: acertou o placar cheio (15 pts)
            acertos_placar=Count('id', filter=Q(pontuacao_obtida=15)),
            # AV: acertou vencedor/empate (5 pts)
            acertos_vencedor=Count('id', filter=Q(pontuacao_obtida=5)),
            # MP: foi o maior pontuador da rodada em algum jogo
            maior_pontuador=Count('id', filter=Q(is_maior_pontuador=True)),
        )
        pontos_jogos = agregados_jogos['total'] or 0

        qs_longo = PalpiteLongoPrazo.objects.filter(usuario=usuario)
        if temporada is not None:
            qs_longo = qs_longo.filter(temporada=temporada)
        pontos_longo = qs_longo.aggregate(total=Sum('pontos_obtidos'))['total'] or 0

        selecao = SelecaoBrasileirao.objects.filter(usuario=usuario).first()
        pontos_selecao = selecao.pontuacao_total if selecao else 0

        total = pontos_jogos + pontos_longo + pontos_selecao

        tem_atividade = (
            palpites_usuario.exists()
            or qs_longo.exists()
            or selecao is not None
        )

        if tem_atividade:
            resultado.append({
                'usuario': usuario,
                'pontos_jogos': pontos_jogos,
                'acertos_placar': agregados_jogos['acertos_placar'] or 0,
                'acertos_vencedor': agregados_jogos['acertos_vencedor'] or 0,
                'maior_pontuador': agregados_jogos['maior_pontuador'] or 0,
                'pontos_longo_prazo': pontos_longo,
                'pontos_selecao_brasileirao': pontos_selecao,
                'total_pontos': total,
            })

    resultado.sort(key=lambda x: x['total_pontos'], reverse=True)
    return resultado
