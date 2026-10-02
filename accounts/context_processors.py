from django.db import DatabaseError

from .models import CarteiraCoins, PerfilUsuario
from .temas import tema_padrao, tema_para_clube


def tema_e_coins(request):
    """
    Injeta em todos os templates:
      - `tema`: cores/apelido do time do coração (ou o tema padrão)
      - `coins_saldo`: saldo de Cartola Coins (mostrado na navbar)
      - `perfil`: PerfilUsuario do usuário logado

    Se as tabelas novas ainda não foram migradas (deploy sem `migrate`), o site
    continua no ar com o tema padrão em vez de quebrar todas as páginas.
    """
    padrao = {'tema': tema_padrao(), 'coins_saldo': None, 'perfil': None}
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return padrao

    try:
        perfil = PerfilUsuario.objects.select_related('time_coracao').filter(usuario=user).first()
        saldo = CarteiraCoins.objects.filter(usuario=user).values_list('saldo', flat=True).first()
    except DatabaseError:
        padrao['coins_saldo'] = CarteiraCoins.SALDO_INICIAL
        return padrao

    if perfil and perfil.usar_tema_do_time and perfil.time_coracao_id:
        tema = tema_para_clube(perfil.time_coracao)
    else:
        tema = tema_padrao()

    if saldo is None:
        saldo = CarteiraCoins.SALDO_INICIAL  # a carteira é criada no primeiro uso real

    return {'tema': tema, 'coins_saldo': saldo, 'perfil': perfil}
