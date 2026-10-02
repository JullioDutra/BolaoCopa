"""
Importa times e jogadores para a busca/comparativos.

Exemplos:
    python manage.py importar_futebol --fonte internos          # usa o que o site já tem (recomendado primeiro)
    python manage.py importar_futebol --fonte football-data     # Brasileirão (precisa FOOTBALL_DATA_TOKEN)
    python manage.py importar_futebol --fonte football-data --competicao PL
    python manage.py importar_futebol --fonte espn              # sem chave
    python manage.py importar_futebol --fonte thesportsdb --buscar "Flamengo"
    python manage.py importar_futebol --fonte api-football --buscar "Palmeiras"
    python manage.py importar_futebol --fonte arquivo --arquivo meus_times.csv
CSV: time,pais,liga,jogador,posicao,numero,nascimento,nacionalidade,overall,valor_mercado
"""
from django.core.management.base import BaseCommand, CommandError

from futebol import importar


class Command(BaseCommand):
    help = "Popula o banco de times/jogadores usado na pesquisa e nos comparativos."

    def add_arguments(self, parser):
        parser.add_argument('--fonte', required=True,
                            choices=['internos', 'football-data', 'api-football', 'thesportsdb', 'espn', 'arquivo'])
        parser.add_argument('--competicao', default='BSA', help="football-data: BSA (Brasileirão), PL, PD, CL...")
        parser.add_argument('--liga-espn', default='bra.1', help="ESPN: bra.1, eng.1, esp.1, conmebol.libertadores...")
        parser.add_argument('--buscar', help="thesportsdb/api-football: nome do time")
        parser.add_argument('--arquivo', help="Caminho de um .json ou .csv")

    def handle(self, *args, **o):
        fonte = o['fonte']
        if fonte == 'internos':
            resumo = importar.importar_internos()
        elif fonte == 'arquivo':
            if not o['arquivo']:
                raise CommandError("Informe --arquivo caminho.csv|json")
            resumo = importar.importar_arquivo(o['arquivo'])
        else:
            resumo = importar.importar_provedor(fonte, competicao=o['competicao'], liga_espn=o['liga_espn'], busca=o['buscar'])
        for erro in resumo['erros']:
            self.stderr.write(self.style.WARNING(erro))
        self.stdout.write(self.style.SUCCESS(
            f"{resumo['times']} times novos, {resumo['atletas']} jogadores novos, {resumo['atualizados']} atualizados."))
        if resumo['erros'] and not (resumo['times'] or resumo['atletas'] or resumo['atualizados']):
            raise CommandError("Nada foi importado (veja os avisos acima).")
