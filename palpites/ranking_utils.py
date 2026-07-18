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
from django.db.models import Sum
from .models import Palpite, PalpiteLongoPrazo


def calcular_ranking_geral(temporada=None):
    # Import local para evitar import circular entre os apps palpites <-> convocacao
    from convocacao.models import SelecaoBrasileirao

    resultado = []

    usuarios_com_atividade = User.objects.filter(
        is_active=True
    ).distinct()

    for usuario in usuarios_com_atividade:
        pontos_jogos = Palpite.objects.filter(usuario=usuario).aggregate(
            total=Sum('pontuacao_obtida')
        )['total'] or 0

        qs_longo = PalpiteLongoPrazo.objects.filter(usuario=usuario)
        if temporada is not None:
            qs_longo = qs_longo.filter(temporada=temporada)
        pontos_longo = qs_longo.aggregate(total=Sum('pontos_obtidos'))['total'] or 0

        selecao = SelecaoBrasileirao.objects.filter(usuario=usuario).first()
        pontos_selecao = selecao.pontuacao_total if selecao else 0

        total = pontos_jogos + pontos_longo + pontos_selecao

        tem_atividade = (
            Palpite.objects.filter(usuario=usuario).exists()
            or qs_longo.exists()
            or selecao is not None
        )

        if tem_atividade:
            resultado.append({
                'usuario': usuario,
                'pontos_jogos': pontos_jogos,
                'pontos_longo_prazo': pontos_longo,
                'pontos_selecao_brasileirao': pontos_selecao,
                'total_pontos': total,
            })

    resultado.sort(key=lambda x: x['total_pontos'], reverse=True)
    return resultado
