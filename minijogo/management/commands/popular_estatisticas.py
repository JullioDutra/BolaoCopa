from django.core.management.base import BaseCommand
from minijogo.models import EstatisticaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com cartas de jogadores do Brasileirão para o minijogo.'

    def handle(self, *args, **kwargs):
        jogadores_data = [
            # ATACANTES
            {"nome": "Pedro", "clube": "Flamengo", "posicao": "ATA", "gols": 135, "assistencias": 35, "cartoes_amarelos": 20, "cartoes_vermelhos": 1, "jogos": 280},
            {"nome": "Hulk", "clube": "Atlético-MG", "posicao": "ATA", "gols": 395, "assistencias": 190, "cartoes_amarelos": 145, "cartoes_vermelhos": 10, "jogos": 780},
            {"nome": "Pablo Vegetti", "clube": "Vasco da Gama", "posicao": "ATA", "gols": 95, "assistencias": 20, "cartoes_amarelos": 45, "cartoes_vermelhos": 4, "jogos": 260},
            {"nome": "Jonathan Calleri", "clube": "São Paulo", "posicao": "ATA", "gols": 125, "assistencias": 35, "cartoes_amarelos": 60, "cartoes_vermelhos": 5, "jogos": 350},
            {"nome": "Estêvão", "clube": "Palmeiras", "posicao": "ATA", "gols": 15, "assistencias": 10, "cartoes_amarelos": 5, "cartoes_vermelhos": 0, "jogos": 40},
            {"nome": "Yuri Alberto", "clube": "Corinthians", "posicao": "ATA", "gols": 85, "assistencias": 25, "cartoes_amarelos": 40, "cartoes_vermelhos": 3, "jogos": 270},
            
            # MEIO-CAMPISTAS
            {"nome": "Giorgian De Arrascaeta", "clube": "Flamengo", "posicao": "MEI", "gols": 115, "assistencias": 150, "cartoes_amarelos": 65, "cartoes_vermelhos": 2, "jogos": 490},
            {"nome": "Raphael Veiga", "clube": "Palmeiras", "posicao": "MEI", "gols": 105, "assistencias": 55, "cartoes_amarelos": 45, "cartoes_vermelhos": 3, "jogos": 380},
            {"nome": "Alan Patrick", "clube": "Internacional", "posicao": "MEI", "gols": 75, "assistencias": 80, "cartoes_amarelos": 50, "cartoes_vermelhos": 5, "jogos": 450},
            {"nome": "Matheus Pereira", "clube": "Cruzeiro", "posicao": "MEI", "gols": 45, "assistencias": 65, "cartoes_amarelos": 55, "cartoes_vermelhos": 3, "jogos": 270},
            {"nome": "Rodrigo Garro", "clube": "Corinthians", "posicao": "MEI", "gols": 30, "assistencias": 45, "cartoes_amarelos": 35, "cartoes_vermelhos": 2, "jogos": 190},
            {"nome": "Gerson", "clube": "Flamengo", "posicao": "MEI", "gols": 35, "assistencias": 45, "cartoes_amarelos": 90, "cartoes_vermelhos": 6, "jogos": 380},

            # LATERAIS
            {"nome": "Guilherme Arana", "clube": "Atlético-MG", "posicao": "LAT", "gols": 35, "assistencias": 60, "cartoes_amarelos": 70, "cartoes_vermelhos": 5, "jogos": 380},
            {"nome": "Fagner", "clube": "Corinthians", "posicao": "LAT", "gols": 20, "assistencias": 85, "cartoes_amarelos": 180, "cartoes_vermelhos": 14, "jogos": 750},
            {"nome": "Marcos Rocha", "clube": "Palmeiras", "posicao": "LAT", "gols": 35, "assistencias": 110, "cartoes_amarelos": 120, "cartoes_vermelhos": 6, "jogos": 710},
            {"nome": "Ayrton Lucas", "clube": "Flamengo", "posicao": "LAT", "gols": 18, "assistencias": 35, "cartoes_amarelos": 45, "cartoes_vermelhos": 1, "jogos": 290},

            # ZAGUEIROS
            {"nome": "Gustavo Gómez", "clube": "Palmeiras", "posicao": "ZAG", "gols": 40, "assistencias": 10, "cartoes_amarelos": 110, "cartoes_vermelhos": 7, "jogos": 450},
            {"nome": "Thiago Silva", "clube": "Fluminense", "posicao": "ZAG", "gols": 45, "assistencias": 15, "cartoes_amarelos": 70, "cartoes_vermelhos": 4, "jogos": 800},
            {"nome": "Walter Kannemann", "clube": "Grêmio", "posicao": "ZAG", "gols": 10, "assistencias": 8, "cartoes_amarelos": 155, "cartoes_vermelhos": 12, "jogos": 420},
            {"nome": "Léo Pereira", "clube": "Flamengo", "posicao": "ZAG", "gols": 25, "assistencias": 12, "cartoes_amarelos": 75, "cartoes_vermelhos": 5, "jogos": 320},
            {"nome": "Murilo", "clube": "Palmeiras", "posicao": "ZAG", "gols": 22, "assistencias": 8, "cartoes_amarelos": 45, "cartoes_vermelhos": 4, "jogos": 230},
            
            # GOLEIROS
            {"nome": "Weverton", "clube": "Palmeiras", "posicao": "GOL", "gols": 0, "assistencias": 2, "cartoes_amarelos": 45, "cartoes_vermelhos": 2, "jogos": 650},
            {"nome": "Léo Jardim", "clube": "Vasco da Gama", "posicao": "GOL", "gols": 0, "assistencias": 0, "cartoes_amarelos": 15, "cartoes_vermelhos": 1, "jogos": 240},
            {"nome": "Cássio", "clube": "Cruzeiro", "posicao": "GOL", "gols": 0, "assistencias": 4, "cartoes_amarelos": 55, "cartoes_vermelhos": 5, "jogos": 780},
            {"nome": "João Ricardo", "clube": "Fortaleza", "posicao": "GOL", "gols": 0, "assistencias": 1, "cartoes_amarelos": 30, "cartoes_vermelhos": 1, "jogos": 460},
            {"nome": "Agustín Rossi", "clube": "Flamengo", "posicao": "GOL", "gols": 0, "assistencias": 1, "cartoes_amarelos": 25, "cartoes_vermelhos": 1, "jogos": 310},
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

        self.stdout.write(self.style.SUCCESS(f'Sucesso! {cadastrados} jogadores do Brasileirão criados e {atualizados} atualizados.'))
