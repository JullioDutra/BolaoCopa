from django.core.management.base import BaseCommand
from minijogo.models import EstatisticaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com cartas de jogadores famosos para o minijogo.'

    def handle(self, *args, **kwargs):
        jogadores_data = [
            # ATACANTES
            {"nome": "Lionel Messi", "clube": "Inter Miami", "posicao": "ATA", "gols": 821, "assistencias": 361, "cartoes_amarelos": 90, "cartoes_vermelhos": 3, "jogos": 1045},
            {"nome": "Cristiano Ronaldo", "clube": "Al Nassr", "posicao": "ATA", "gols": 860, "assistencias": 240, "cartoes_amarelos": 110, "cartoes_vermelhos": 11, "jogos": 1190},
            {"nome": "Neymar Jr", "clube": "Al Hilal", "posicao": "ATA", "gols": 436, "assistencias": 250, "cartoes_amarelos": 130, "cartoes_vermelhos": 12, "jogos": 710},
            {"nome": "Kylian Mbappé", "clube": "Paris Saint-Germain", "posicao": "ATA", "gols": 290, "assistencias": 120, "cartoes_amarelos": 45, "cartoes_vermelhos": 3, "jogos": 390},
            {"nome": "Erling Haaland", "clube": "Manchester City", "posicao": "ATA", "gols": 220, "assistencias": 45, "cartoes_amarelos": 20, "cartoes_vermelhos": 1, "jogos": 270},
            {"nome": "Vinícius Júnior", "clube": "Real Madrid", "posicao": "ATA", "gols": 85, "assistencias": 70, "cartoes_amarelos": 40, "cartoes_vermelhos": 1, "jogos": 280},
            
            # MEIO-CAMPISTAS
            {"nome": "Kevin De Bruyne", "clube": "Manchester City", "posicao": "MEI", "gols": 140, "assistencias": 285, "cartoes_amarelos": 55, "cartoes_vermelhos": 2, "jogos": 650},
            {"nome": "Luka Modric", "clube": "Real Madrid", "posicao": "MEI", "gols": 95, "assistencias": 150, "cartoes_amarelos": 90, "cartoes_vermelhos": 2, "jogos": 850},
            {"nome": "Toni Kroos", "clube": "Real Madrid", "posicao": "MEI", "gols": 70, "assistencias": 160, "cartoes_amarelos": 85, "cartoes_vermelhos": 1, "jogos": 780},
            {"nome": "Bruno Fernandes", "clube": "Manchester United", "posicao": "MEI", "gols": 160, "assistencias": 145, "cartoes_amarelos": 80, "cartoes_vermelhos": 2, "jogos": 520},
            {"nome": "Jude Bellingham", "clube": "Real Madrid", "posicao": "MEI", "gols": 45, "assistencias": 35, "cartoes_amarelos": 40, "cartoes_vermelhos": 1, "jogos": 220},

            # LATERAIS
            {"nome": "Marcelo", "clube": "Fluminense", "posicao": "LAT", "gols": 45, "assistencias": 110, "cartoes_amarelos": 95, "cartoes_vermelhos": 5, "jogos": 700},
            {"nome": "Trent Alexander-Arnold", "clube": "Liverpool", "posicao": "LAT", "gols": 20, "assistencias": 80, "cartoes_amarelos": 40, "cartoes_vermelhos": 0, "jogos": 290},
            {"nome": "Dani Alves", "clube": "Aposentado", "posicao": "LAT", "gols": 60, "assistencias": 170, "cartoes_amarelos": 160, "cartoes_vermelhos": 12, "jogos": 950},
            {"nome": "Alphonso Davies", "clube": "Bayern Munich", "posicao": "LAT", "gols": 25, "assistencias": 45, "cartoes_amarelos": 25, "cartoes_vermelhos": 2, "jogos": 210},

            # ZAGUEIROS
            {"nome": "Sergio Ramos", "clube": "Sevilla", "posicao": "ZAG", "gols": 133, "assistencias": 42, "cartoes_amarelos": 240, "cartoes_vermelhos": 29, "jogos": 950},
            {"nome": "Virgil van Dijk", "clube": "Liverpool", "posicao": "ZAG", "gols": 50, "assistencias": 25, "cartoes_amarelos": 35, "cartoes_vermelhos": 3, "jogos": 550},
            {"nome": "Marquinhos", "clube": "Paris Saint-Germain", "posicao": "ZAG", "gols": 40, "assistencias": 15, "cartoes_amarelos": 55, "cartoes_vermelhos": 3, "jogos": 520},
            {"nome": "Thiago Silva", "clube": "Chelsea", "posicao": "ZAG", "gols": 45, "assistencias": 15, "cartoes_amarelos": 70, "cartoes_vermelhos": 4, "jogos": 800},
            
            # GOLEIROS
            {"nome": "Manuel Neuer", "clube": "Bayern Munich", "posicao": "GOL", "gols": 0, "assistencias": 7, "cartoes_amarelos": 20, "cartoes_vermelhos": 0, "jogos": 820},
            {"nome": "Alisson Becker", "clube": "Liverpool", "posicao": "GOL", "gols": 1, "assistencias": 3, "cartoes_amarelos": 10, "cartoes_vermelhos": 1, "jogos": 450},
            {"nome": "Ederson", "clube": "Manchester City", "posicao": "GOL", "gols": 0, "assistencias": 4, "cartoes_amarelos": 25, "cartoes_vermelhos": 2, "jogos": 420},
            {"nome": "Thibaut Courtois", "clube": "Real Madrid", "posicao": "GOL", "gols": 0, "assistencias": 1, "cartoes_amarelos": 15, "cartoes_vermelhos": 2, "jogos": 650},
        ]

        cadastrados = 0
        atualizados = 0

        for dados in jogadores_data:
            # Usa update_or_create para não duplicar se você rodar o comando mais de uma vez
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

        self.stdout.write(self.style.SUCCESS(f'Sucesso! {cadastrados} jogadores criados e {atualizados} atualizados.'))
