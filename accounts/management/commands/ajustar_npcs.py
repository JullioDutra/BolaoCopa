"""
Marca como NPC os "jogadores reais" que os scripts do modo carreira criaram como usuários.

  python manage.py ajustar_npcs            # lista o que seria ajustado (nada é gravado)
  python manage.py ajustar_npcs --aplicar  # inativa, tira a senha e marca como [NPC]
Só mexe em quem NUNCA entrou no site, não é staff e não tem participação nem palpites.
"""
from django.core.management.base import BaseCommand

from accounts import npc


class Command(BaseCommand):
    help = 'Separa os NPCs do modo carreira dos usuários reais.'

    def add_arguments(self, parser):
        parser.add_argument('--aplicar', action='store_true')

    def handle(self, *args, aplicar=False, **opts):
        lista = list(npc.candidatos_a_npc())
        for u in lista[:15]:
            self.stdout.write(f'  {u.username}')
        if len(lista) > 15:
            self.stdout.write(f'  … e mais {len(lista) - 15}')
        if aplicar:
            for u in lista:
                u.last_name = npc.MARCA
                u.is_active = False
                u.set_unusable_password()
                u.save(update_fields=['last_name', 'is_active', 'password'])
        modo = 'APLICADO' if aplicar else 'SIMULAÇÃO (use --aplicar)'
        self.stdout.write(self.style.SUCCESS(f'{modo}: {len(lista)} usuários identificados como NPC.'))
