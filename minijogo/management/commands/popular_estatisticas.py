from django.core.management.base import BaseCommand
from minijogo.models import EstatisticaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com os jogadores mais aleatórios e heróis cult do futebol.'

    def handle(self, *args, **kwargs):
        jogadores_data = [
            # ATACANTES
            {"nome": "Flávio Caça-Rato", "clube": "Santa Cruz", "posicao": "ATA", "gols": 42, "assistencias": 10, "cartoes_amarelos": 35, "cartoes_vermelhos": 4, "jogos": 210},
            {"nome": "Zizao", "clube": "Corinthians", "posicao": "ATA", "gols": 0, "assistencias": 2, "cartoes_amarelos": 1, "cartoes_vermelhos": 0, "jogos": 5},
            {"nome": "Colin Kazim-Richards", "clube": "Corinthians", "posicao": "ATA", "gols": 55, "assistencias": 25, "cartoes_amarelos": 65, "cartoes_vermelhos": 6, "jogos": 390},
            {"nome": "Maxi Biancucchi", "clube": "Vitória", "posicao": "ATA", "gols": 68, "assistencias": 30, "cartoes_amarelos": 40, "cartoes_vermelhos": 2, "jogos": 280},
            {"nome": "Santiago El Tanque Silva", "clube": "Boca Juniors", "posicao": "ATA", "gols": 180, "assistencias": 40, "cartoes_amarelos": 115, "cartoes_vermelhos": 12, "jogos": 550},
            {"nome": "Ribamar", "clube": "Vasco da Gama", "posicao": "ATA", "gols": 32, "assistencias": 12, "cartoes_amarelos": 25, "cartoes_vermelhos": 1, "jogos": 215},
            
            # MEIO-CAMPISTAS
            {"nome": "Perdigão", "clube": "Internacional", "posicao": "MEI", "gols": 18, "assistencias": 35, "cartoes_amarelos": 85, "cartoes_vermelhos": 5, "jogos": 320},
            {"nome": "Matías Defederico", "clube": "Corinthians", "posicao": "MEI", "gols": 25, "assistencias": 32, "cartoes_amarelos": 20, "cartoes_vermelhos": 1, "jogos": 200},
            {"nome": "Valdívia (PokoPika)", "clube": "Internacional", "posicao": "MEI", "gols": 45, "assistencias": 30, "cartoes_amarelos": 45, "cartoes_vermelhos": 2, "jogos": 310},
            {"nome": "Douglas (Maestro Pifador)", "clube": "Grêmio", "posicao": "MEI", "gols": 85, "assistencias": 160, "cartoes_amarelos": 70, "cartoes_vermelhos": 3, "jogos": 580},
            {"nome": "Carlos Alberto", "clube": "Porto", "posicao": "MEI", "gols": 60, "assistencias": 45, "cartoes_amarelos": 120, "cartoes_vermelhos": 15, "jogos": 410},

            # LATERAIS
            {"nome": "Pablo Armero", "clube": "Palmeiras", "posicao": "LAT", "gols": 15, "assistencias": 55, "cartoes_amarelos": 65, "cartoes_vermelhos": 5, "jogos": 390},
            {"nome": "Egídio", "clube": "Cruzeiro", "posicao": "LAT", "gols": 18, "assistencias": 75, "cartoes_amarelos": 105, "cartoes_vermelhos": 8, "jogos": 520},
            {"nome": "Anderson Pico", "clube": "Flamengo", "posicao": "LAT", "gols": 12, "assistencias": 20, "cartoes_amarelos": 50, "cartoes_vermelhos": 3, "jogos": 250},
            {"nome": "Bruno Cortez", "clube": "Grêmio", "posicao": "LAT", "gols": 8, "assistencias": 35, "cartoes_amarelos": 85, "cartoes_vermelhos": 4, "jogos": 490},

            # ZAGUEIROS
            {"nome": "Paulão (Desmaio)", "clube": "Internacional", "posicao": "ZAG", "gols": 22, "assistencias": 5, "cartoes_amarelos": 110, "cartoes_vermelhos": 9, "jogos": 460},
            {"nome": "Bressan", "clube": "Grêmio", "posicao": "ZAG", "gols": 8, "assistencias": 3, "cartoes_amarelos": 65, "cartoes_vermelhos": 7, "jogos": 280},
            {"nome": "Frickson Erazo", "clube": "Atlético-MG", "posicao": "ZAG", "gols": 5, "assistencias": 2, "cartoes_amarelos": 55, "cartoes_vermelhos": 5, "jogos": 290},
            {"nome": "Victor Ramos", "clube": "Vitória", "posicao": "ZAG", "gols": 20, "assistencias": 4, "cartoes_amarelos": 125, "cartoes_vermelhos": 11, "jogos": 350},
            
            # GOLEIROS
            {"nome": "Robert Kidiaba", "clube": "Mazembe", "posicao": "GOL", "gols": 0, "assistencias": 0, "cartoes_amarelos": 15, "cartoes_vermelhos": 0, "jogos": 450},
            {"nome": "Alex Muralha", "clube": "Flamengo", "posicao": "GOL", "gols": 0, "assistencias": 0, "cartoes_amarelos": 35, "cartoes_vermelhos": 3, "jogos": 320},
            {"nome": "Lauro", "clube": "Ponte Preta", "posicao": "GOL", "gols": 3, "assistencias": 0, "cartoes_amarelos": 40, "cartoes_vermelhos": 4, "jogos": 410},
            {"nome": "Felipe (Mão de Alface)", "clube": "Corinthians", "posicao": "GOL", "gols": 0, "assistencias": 1, "cartoes_amarelos": 50, "cartoes_vermelhos": 5, "jogos": 390},
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

        self.stdout.write(self.style.SUCCESS(f'Sucesso! {cadastrados} jogadores completamente aleatórios criados e {atualizados} atualizados.'))
