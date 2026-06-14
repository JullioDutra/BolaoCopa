from django.core.management.base import BaseCommand
from minijogo.models import ElencoHistorico, CartaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com elencos históricos e jogadores para o Draft'

    def handle(self, *args, **kwargs):
        # Dicionário com os times e jogadores (Nome, Posição, Over)
        dados_elencos = {
            "Flamengo 2019": [
                ("Diego Alves", "goleiro", 85),
                ("Rafinha", "linha", 83),
                ("Rodrigo Caio", "linha", 84),
                ("Pablo Marí", "linha", 83),
                ("Filipe Luís", "linha", 86),
                ("Gerson", "linha", 85),
                ("Willian Arão", "linha", 83),
                ("Éverton Ribeiro", "linha", 87),
                ("De Arrascaeta", "linha", 88),
                ("Bruno Henrique", "linha", 88),
                ("Gabigol", "linha", 89),
            ],
            "Grêmio 2017": [
                ("Marcelo Grohe", "goleiro", 87),
                ("Edílson", "linha", 82),
                ("Pedro Geromel", "linha", 88),
                ("Kannemann", "linha", 86),
                ("Bruno Cortez", "linha", 81),
                ("Arthur", "linha", 86),
                ("Maicon", "linha", 84),
                ("Ramiro", "linha", 82),
                ("Luan", "linha", 89),
                ("Fernandinho", "linha", 81),
                ("Lucas Barrios", "linha", 83),
            ],
            "Santos 2011": [
                ("Rafael Cabral", "goleiro", 83),
                ("Danilo", "linha", 84),
                ("Edu Dracena", "linha", 85),
                ("Durval", "linha", 82),
                ("Léo", "linha", 81),
                ("Arouca", "linha", 84),
                ("Elano", "linha", 86),
                ("Ganso", "linha", 88),
                ("Neymar", "linha", 92),
                ("Borges", "linha", 85),
                ("Zé Eduardo", "linha", 80),
            ],
            "São Paulo 2005": [
                ("Rogério Ceni", "goleiro", 91),
                ("Cicinho", "linha", 87),
                ("Diego Lugano", "linha", 88),
                ("Fabão", "linha", 84),
                ("Júnior", "linha", 85),
                ("Mineiro", "linha", 86),
                ("Josué", "linha", 86),
                ("Danilo", "linha", 87),
                ("Amoroso", "linha", 88),
                ("Aloísio Chulapa", "linha", 84),
                ("Luizão", "linha", 85),
            ]
        }

        self.stdout.write(self.style.WARNING('Iniciando o cadastro de Elencos e Jogadores...'))

        total_jogadores = 0

        for nome_time, jogadores in dados_elencos.items():
            # Cria ou pega o time
            elenco, created = ElencoHistorico.objects.get_or_create(nome=nome_time)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Elenco criado: {nome_time}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Elenco {nome_time} já existe, adicionando jogadores...'))

            # Adiciona os jogadores ao time
            for j_nome, j_posicao, j_over in jogadores:
                jogador, j_created = CartaJogador.objects.get_or_create(
                    nome=j_nome,
                    elenco=elenco,
                    defaults={'posicao': j_posicao, 'over': j_over}
                )
                
                if j_created:
                    total_jogadores += 1

        self.stdout.write(self.style.SUCCESS(f'🎉 Sucesso! {total_jogadores} novos jogadores foram adicionados ao Draft!'))