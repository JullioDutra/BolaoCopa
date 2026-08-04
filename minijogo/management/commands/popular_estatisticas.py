from django.core.management.base import BaseCommand
from minijogo.models import EstatisticaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com cartas de Lendas do Futebol Mundial para o minijogo.'

    def handle(self, *args, **kwargs):
        jogadores_data = [
            # ATACANTES
            {"nome": "Pelé", "clube": "Santos", "posicao": "ATA", "gols": 767, "assistencias": 340, "cartoes_amarelos": 15, "cartoes_vermelhos": 0, "jogos": 831},
            {"nome": "Ronaldo Fenômeno", "clube": "Real Madrid", "posicao": "ATA", "gols": 414, "assistencias": 104, "cartoes_amarelos": 35, "cartoes_vermelhos": 2, "jogos": 616},
            {"nome": "Romário", "clube": "Vasco da Gama", "posicao": "ATA", "gols": 772, "assistencias": 150, "cartoes_amarelos": 80, "cartoes_vermelhos": 10, "jogos": 994},
            {"nome": "Ferenc Puskás", "clube": "Real Madrid", "posicao": "ATA", "gols": 746, "assistencias": 120, "cartoes_amarelos": 10, "cartoes_vermelhos": 1, "jogos": 754},
            {"nome": "Johan Cruyff", "clube": "Ajax", "posicao": "ATA", "gols": 405, "assistencias": 180, "cartoes_amarelos": 35, "cartoes_vermelhos": 3, "jogos": 716},
            {"nome": "Garrincha", "clube": "Botafogo", "posicao": "ATA", "gols": 245, "assistencias": 110, "cartoes_amarelos": 12, "cartoes_vermelhos": 1, "jogos": 614},
            
            # MEIO-CAMPISTAS
            {"nome": "Diego Maradona", "clube": "Napoli", "posicao": "MEI", "gols": 345, "assistencias": 240, "cartoes_amarelos": 50, "cartoes_vermelhos": 4, "jogos": 680},
            {"nome": "Zinedine Zidane", "clube": "Real Madrid", "posicao": "MEI", "gols": 156, "assistencias": 119, "cartoes_amarelos": 65, "cartoes_vermelhos": 14, "jogos": 795},
            {"nome": "Ronaldinho Gaúcho", "clube": "Barcelona", "posicao": "MEI", "gols": 299, "assistencias": 214, "cartoes_amarelos": 70, "cartoes_vermelhos": 7, "jogos": 719},
            {"nome": "Zico", "clube": "Flamengo", "posicao": "MEI", "gols": 525, "assistencias": 250, "cartoes_amarelos": 40, "cartoes_vermelhos": 2, "jogos": 769},
            {"nome": "Andrés Iniesta", "clube": "Barcelona", "posicao": "MEI", "gols": 93, "assistencias": 190, "cartoes_amarelos": 65, "cartoes_vermelhos": 0, "jogos": 1016},
            {"nome": "Michel Platini", "clube": "Juventus", "posicao": "MEI", "gols": 353, "assistencias": 150, "cartoes_amarelos": 30, "cartoes_vermelhos": 1, "jogos": 652},

            # LATERAIS
            {"nome": "Roberto Carlos", "clube": "Real Madrid", "posicao": "LAT", "gols": 113, "assistencias": 125, "cartoes_amarelos": 130, "cartoes_vermelhos": 10, "jogos": 945},
            {"nome": "Cafu", "clube": "Milan", "posicao": "LAT", "gols": 25, "assistencias": 100, "cartoes_amarelos": 110, "cartoes_vermelhos": 6, "jogos": 800},
            {"nome": "Carlos Alberto Torres", "clube": "Santos", "posicao": "LAT", "gols": 60, "assistencias": 75, "cartoes_amarelos": 40, "cartoes_vermelhos": 3, "jogos": 740},
            {"nome": "Philipp Lahm", "clube": "Bayern Munich", "posicao": "LAT", "gols": 22, "assistencias": 77, "cartoes_amarelos": 48, "cartoes_vermelhos": 0, "jogos": 765},

            # ZAGUEIROS
            {"nome": "Paolo Maldini", "clube": "Milan", "posicao": "ZAG", "gols": 33, "assistencias": 43, "cartoes_amarelos": 87, "cartoes_vermelhos": 3, "jogos": 902},
            {"nome": "Franz Beckenbauer", "clube": "Bayern Munich", "posicao": "ZAG", "gols": 109, "assistencias": 75, "cartoes_amarelos": 40, "cartoes_vermelhos": 0, "jogos": 820},
            {"nome": "Fabio Cannavaro", "clube": "Juventus", "posicao": "ZAG", "gols": 16, "assistencias": 10, "cartoes_amarelos": 115, "cartoes_vermelhos": 8, "jogos": 690},
            {"nome": "Franco Baresi", "clube": "Milan", "posicao": "ZAG", "gols": 33, "assistencias": 24, "cartoes_amarelos": 50, "cartoes_vermelhos": 4, "jogos": 719},
            {"nome": "Carles Puyol", "clube": "Barcelona", "posicao": "ZAG", "gols": 24, "assistencias": 16, "cartoes_amarelos": 140, "cartoes_vermelhos": 4, "jogos": 682},
            
            # GOLEIROS
            {"nome": "Lev Yashin", "clube": "Dynamo Moscow", "posicao": "GOL", "gols": 0, "assistencias": 0, "cartoes_amarelos": 5, "cartoes_vermelhos": 0, "jogos": 326},
            {"nome": "Gianluigi Buffon", "clube": "Juventus", "posicao": "GOL", "gols": 0, "assistencias": 1, "cartoes_amarelos": 40, "cartoes_vermelhos": 5, "jogos": 1151},
            {"nome": "Oliver Kahn", "clube": "Bayern Munich", "posicao": "GOL", "gols": 0, "assistencias": 12, "cartoes_amarelos": 45, "cartoes_vermelhos": 3, "jogos": 780},
            {"nome": "Rogério Ceni", "clube": "São Paulo", "posicao": "GOL", "gols": 131, "assistencias": 0, "cartoes_amarelos": 60, "cartoes_vermelhos": 4, "jogos": 1237},
            {"nome": "Gordon Banks", "clube": "Leicester City", "posicao": "GOL", "gols": 0, "assistencias": 0, "cartoes_amarelos": 2, "cartoes_vermelhos": 0, "jogos": 678},
        ]

        cadastrados = 0
        atualizados = 0

        for dados in jogadores_data:
            jogador, created = EstatisticaJogador.objects.update_or_create(
                nome=dados['nome'],
                defaults={
                    'clube': dados['clube'],
                    'posicao': dados['posicao'],
                    'gols': dados['gols'],
                    'assistencias': dados['assistencias'],
                    'cartoes_amarelos': dados['cartoes_amarelos'],
                    'cartoes_vermelhos': dados['cartoes_vermelhos'],
                    'jogos': dados['jogos'],
                    'ativo': True
                }
            )
            if created:
                cadastrados += 1
            else:
                atualizados += 1

        self.stdout.write(self.style.SUCCESS(f'Sucesso! {cadastrados} lendas criadas e {atualizados} atualizadas.'))
