"""
Sincroniza jogos/resultados do Brasileirão (ou outra competição) com o Bolão.

Uso:
    python manage.py sincronizar_jogos                 # rodada atual do Brasileirão
    python manage.py sincronizar_jogos --rodada 12
    python manage.py sincronizar_jogos --competicao BSA --sem-finalizar

No PythonAnywhere: aba "Tasks" -> agende `python manage.py sincronizar_jogos`
(conta gratuita tem 1 tarefa diária; conta paga permite de hora em hora). Para
rodar com mais frequência no plano gratuito, use o endpoint com token em
/palpites/api/sincronizar/<CRON_SECRET_TOKEN>/ com um serviço de cron externo.
"""
from django.core.management.base import BaseCommand, CommandError

from palpites import api_futebol
from palpites.sincronizacao import sincronizar


class Command(BaseCommand):
    help = "Busca jogos e resultados na API football-data.org e atualiza o Bolão."

    def add_arguments(self, parser):
        parser.add_argument('--competicao', default=api_futebol.COMPETICAO_PADRAO)
        parser.add_argument('--rodada', type=int, default=None)
        parser.add_argument('--rodadas', type=int, default=1,
                            help="Quantas rodadas puxar a partir da atual/--rodada (ex.: 2 = atual e próxima).")
        parser.add_argument('--sem-finalizar', action='store_true',
                            help="Atualiza jogos mas não marca como finalizados (não paga prêmios).")

    def handle(self, *args, **opts):
        total = {'total': 0, 'criados': 0, 'atualizados': 0, 'finalizados': 0}
        try:
            inicio = opts['rodada'] or api_futebol.rodada_atual(opts['competicao'])
            for rodada in range(inicio, inicio + max(opts['rodadas'], 1)) if inicio else [None]:
                resumo = sincronizar(competicao=opts['competicao'], rodada=rodada, finalizar=not opts['sem_finalizar'])
                for chave in total:
                    total[chave] += resumo[chave]
        except api_futebol.ApiIndisponivel as erro:
            raise CommandError(str(erro))
        self.stdout.write(self.style.SUCCESS(
            f"{total['total']} partidas: {total['criados']} novas, "
            f"{total['atualizados']} atualizadas, {total['finalizados']} finalizadas agora."
        ))
