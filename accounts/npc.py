"""
NPCs do modo carreira.

Os jogadores "reais" do metaverso (Neymar, Gabigol…) precisam de um `User` porque `Avatar.usuario` é obrigatório,
mas NÃO são pessoas: ficam inativos (não entram, não recebem avisos, não aparecem nas listas) e marcados com
`last_name = '[NPC]'`. Use `usuarios_reais()` sempre que for listar participantes.
"""
from django.contrib.auth.models import User

MARCA = '[NPC]'


def criar_usuario_npc(username, nome=''):
    """ Cria (ou reaproveita) o usuário técnico de um NPC: inativo, sem senha e marcado. """
    usuario, criado = User.objects.get_or_create(username=username)
    if criado or not eh_npc(usuario):
        usuario.first_name = (nome or usuario.first_name)[:150]
        usuario.last_name = MARCA
        usuario.is_active = False
        usuario.set_unusable_password()
        usuario.save()
    return usuario


def eh_npc(usuario):
    return usuario.last_name == MARCA


def usuarios_reais():
    return User.objects.exclude(last_name=MARCA)


def candidatos_a_npc():
    """
    Usuários criados pelos scripts do carreira antes desta marcação: têm Avatar, nunca entraram no site e
    não têm nenhuma atividade de pessoa (participação no bolão, palpites, carteira com saldo, apostas).
    """
    from django.db.models import Q
    tecnicos = Q(username='cbf_oficial') | Q(username__startswith='bot_')
    return (User.objects.filter(Q(avatar_carreira__isnull=False) | tecnicos, last_login__isnull=True, is_staff=False, is_superuser=False)
            .exclude(last_name=MARCA)
            .filter(participacao__isnull=True, palpites__isnull=True)
            .exclude(Q(username__icontains='@'))
            .distinct())
