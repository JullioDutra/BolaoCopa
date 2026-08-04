from django.core.management.base import BaseCommand
from minijogo.models import EstatisticaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com cartas de jogadores medianos, folclóricos e operários com ótimos números.'

    def handle(self, *args, **kwargs):
        jogadores_data = [
            # ATACANTES
            {"nome": "Obina", "clube": "Flamengo", "posicao": "ATA", "gols": 118, "assistencias": 25, "cartoes_amarelos": 45, "cartoes_vermelhos": 4, "jogos": 412},
            {"nome": "Deyverson", "clube": "Atlético-MG", "posicao": "ATA", "gols": 92, "assistencias": 21, "cartoes_amarelos": 75, "cartoes_vermelhos": 8, "jogos": 345},
            {"nome": "Hernane Brocador", "clube": "Flamengo", "posicao": "ATA", "gols": 145, "assistencias": 28, "cartoes_amarelos": 30, "cartoes_vermelhos": 2, "jogos": 430},
            {"nome": "Borges", "clube": "Santos", "posicao": "ATA", "gols": 182, "assistencias": 35, "cartoes_amarelos": 65, "cartoes_vermelhos": 5, "jogos": 485},
            {"nome": "Alecsandro (Alecgol)", "clube": "Vasco da Gama", "posicao": "ATA", "gols": 178, "assistencias": 42, "cartoes_amarelos": 55, "cartoes_vermelhos": 3, "jogos": 510},
            {"nome": "Souza Caveirão", "clube": "Bahia", "posicao": "ATA", "gols": 135, "assistencias": 20, "cartoes_amarelos": 70, "cartoes_vermelhos": 9, "jogos": 420},
            
            # MEIO-CAMPISTAS
            {"nome": "Diego Souza", "clube": "Grêmio", "posicao": "MEI", "gols": 205, "assistencias": 115, "cartoes_amarelos": 120, "cartoes_vermelhos": 11, "jogos": 780},
            {"nome": "Yago Pikachu", "clube": "Fortaleza", "posicao": "MEI", "gols": 135, "assistencias": 80, "cartoes_amarelos": 75, "cartoes_vermelhos": 4, "jogos": 590},
            {"nome": "Cícero", "clube": "Fluminense", "posicao": "MEI", "gols": 110, "assistencias": 55, "cartoes_amarelos": 85, "cartoes_vermelhos": 3, "jogos": 620},
            {"nome": "Márcio Araújo", "clube": "Flamengo", "posicao": "MEI", "gols": 12, "assistencias": 22, "cartoes_amarelos": 105, "cartoes_vermelhos": 2, "jogos": 680},
            {"nome": "Thiago Galhardo", "clube": "Internacional", "posicao": "MEI", "gols": 95, "assistencias": 45, "cartoes_amarelos": 75, "cartoes_vermelhos": 6, "jogos": 410},

            # LATERAIS
            {"nome": "Reinaldo (Kingnaldo)", "clube": "São Paulo", "posicao": "LAT", "gols": 38, "assistencias": 68, "cartoes_amarelos": 115, "cartoes_vermelhos": 5, "jogos": 540},
            {"nome": "Rodinei", "clube": "Flamengo", "posicao": "LAT", "gols": 10, "assistencias": 45, "cartoes_amarelos": 85, "cartoes_vermelhos": 4, "jogos": 420},
            {"nome": "Nino Paraíba", "clube": "Bahia", "posicao": "LAT", "gols": 15, "assistencias": 40, "cartoes_amarelos": 135, "cartoes_vermelhos": 8, "jogos": 650},
            {"nome": "Apodi", "clube": "Chapecoense", "posicao": "LAT", "gols": 30, "assistencias": 25, "cartoes_amarelos": 90, "cartoes_vermelhos": 6, "jogos": 510},
            {"nome": "Pará", "clube": "Santos", "posicao": "LAT", "gols": 4, "assistencias": 35, "cartoes_amarelos": 110, "cartoes_vermelhos": 7, "jogos": 580},

            # ZAGUEIROS
            {"nome": "Réver", "clube": "Atlético-MG", "posicao": "ZAG", "gols": 42, "assistencias": 12, "cartoes_amarelos": 85, "cartoes_vermelhos": 4, "jogos": 550},
            {"nome": "Antônio Carlos", "clube": "Botafogo", "posicao": "ZAG", "gols": 38, "assistencias": 8, "cartoes_amarelos": 95, "cartoes_vermelhos": 6, "jogos": 480},
            {"nome": "Rodrigo", "clube": "Vasco da Gama", "posicao": "ZAG", "gols": 35, "assistencias": 10, "cartoes_amarelos": 140, "cartoes_vermelhos": 14, "jogos": 520},
            {"nome": "Domingos", "clube": "Santos", "posicao": "ZAG", "gols": 5, "assistencias": 3, "cartoes_amarelos": 160, "cartoes_vermelhos": 18, "jogos": 390},
            
            # GOLEIROS
            {"nome": "Márcio", "clube": "Atlético-GO", "posicao": "GOL", "gols": 34, "assistencias": 0, "cartoes_amarelos": 45, "cartoes_vermelhos": 3, "jogos": 530},
            {"nome": "Fábio Costa", "clube": "Santos", "posicao": "GOL", "gols": 0, "assistencias": 2, "cartoes_amarelos": 95, "cartoes_vermelhos": 8, "jogos": 580},
            {"nome": "Denis", "clube": "São Paulo", "posicao": "GOL", "gols": 0, "assistencias": 1, "cartoes_amarelos": 25, "cartoes_vermelhos": 2, "jogos": 250},
            {"nome": "Vanderlei", "clube": "Santos", "posicao": "GOL", "gols": 0, "assistencias": 1, "cartoes_amarelos": 30, "cartoes_vermelhos": 1, "jogos": 620},
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

        self.stdout.write(self.style.SUCCESS(f'Sucesso! {cadastrados} jogadores folclóricos criados e {atualizados} atualizados.'))
