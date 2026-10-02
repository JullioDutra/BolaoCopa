"""
Reúne os jogadores de todos os jogos (Seleção, Trunfo, Draft) no banco único `futebol.Atleta`
sem alterar nenhuma tabela dos jogos antigos.

  python manage.py consolidar_jogadores            # simulação (nada é gravado)
  python manage.py consolidar_jogadores --aplicar
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from futebol import importar
from futebol.models import Atleta, FonteAtleta


class _Simulacao(Exception):
    pass


class Command(BaseCommand):
    help = 'Consolida jogadores dos jogos no banco único de atletas.'

    def add_arguments(self, parser):
        parser.add_argument('--aplicar', action='store_true')

    def handle(self, *args, aplicar=False, **opts):
        resumo = None
        try:
            with transaction.atomic():
                resumo = importar.importar_internos()
                total = Atleta.objects.count()
                ligacoes = FonteAtleta.objects.count()
                if not aplicar:
                    raise _Simulacao()
        except _Simulacao:
            pass
        modo = 'APLICADO' if aplicar else 'SIMULAÇÃO (use --aplicar)'
        self.stdout.write(self.style.SUCCESS(
            f"{modo}: {resumo['atletas']} atletas novos, {resumo['atualizados']} já existiam, "
            f"{ligacoes} vínculos com os jogos, banco com {total} atletas."))
        for erro in resumo['erros']:
            self.stdout.write(self.style.WARNING(erro))
