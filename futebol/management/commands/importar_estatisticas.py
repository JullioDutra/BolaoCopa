"""
Estatísticas de jogadores para o Scout (mitou ou bagre).

  python manage.py importar_estatisticas --csv estatisticas.csv
  python manage.py importar_estatisticas --api-football --temporada 2024 --time Flamengo
  python manage.py importar_estatisticas --api-football --temporada 2024 --todos   # gasta ~1-3 req por time (cota: 100/dia)
CSV: nome,time,posicao,temporada,competicao,jogos,minutos,gols,assistencias,amarelos,vermelhos,nota,
     gols_sofridos,jogos_sem_sofrer,defesas,contratado,valor
(o plano grátis da API-Football só libera temporadas antigas, ex.: 2021–2023)
"""
from django.core.management.base import BaseCommand, CommandError

from futebol import importar_stats


class Command(BaseCommand):
    help = 'Importa estatísticas de jogadores (CSV ou API-Football).'

    def add_arguments(self, parser):
        parser.add_argument('--csv')
        parser.add_argument('--api-football', action='store_true')
        parser.add_argument('--temporada', type=int)
        parser.add_argument('--time')
        parser.add_argument('--todos', action='store_true')

    def handle(self, *args, **o):
        if o['csv']:
            resumo = importar_stats.importar_csv(o['csv'])
        elif o['api_football']:
            if not o['temporada']:
                raise CommandError('Informe --temporada.')
            if not (o['time'] or o['todos']):
                raise CommandError('Informe --time NOME ou --todos.')
            times = importar_stats.times_para_importar(o['time'])
            if not times:
                raise CommandError('Nenhum time com id da API-Football. Rode antes: importar_futebol --fonte api-football --buscar "Nome".')
            resumo = None
            for t in times:
                parcial = importar_stats.importar_api_football(t, o['temporada'])
                self.stdout.write(f"{t.nome}: {parcial['atletas']} novos, {parcial['atualizados']} atualizados")
                resumo = resumo or parcial
                if resumo is not parcial:
                    for k in ('atletas', 'atualizados'):
                        resumo[k] += parcial[k]
                    resumo['erros'] += parcial['erros']
        else:
            raise CommandError('Use --csv ARQUIVO ou --api-football.')
        for erro in resumo['erros']:
            self.stderr.write(self.style.WARNING(erro))
        self.stdout.write(self.style.SUCCESS(f"{resumo['atletas']} registros novos, {resumo['atualizados']} atualizados."))
