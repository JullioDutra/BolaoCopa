from django.core.management.base import BaseCommand
from minijogo.models import ElencoHistorico, CartaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com elencos históricos épicos e jogadores para o Draft X1'

    def handle(self, *args, **kwargs):
        # Dicionário GIGANTE com os maiores times da história (Nome, Posição, Over)
        dados_elencos = {
            # =================== TIMES BRASILEIROS ===================
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
            "Corinthians 2012": [
                ("Cássio", "goleiro", 88),
                ("Alessandro", "linha", 82),
                ("Chicão", "linha", 85),
                ("Leandro Castán", "linha", 84),
                ("Fábio Santos", "linha", 84),
                ("Ralf", "linha", 85),
                ("Paulinho", "linha", 87),
                ("Danilo", "linha", 86),
                ("Alex", "linha", 83),
                ("Emerson Sheik", "linha", 88),
                ("Paolo Guerrero", "linha", 89),
            ],
            "Palmeiras 2020": [
                ("Weverton", "goleiro", 87),
                ("Marcos Rocha", "linha", 83),
                ("Gustavo Gómez", "linha", 88),
                ("Luan", "linha", 83),
                ("Matías Viña", "linha", 84),
                ("Danilo", "linha", 83),
                ("Zé Rafael", "linha", 84),
                ("Raphael Veiga", "linha", 87),
                ("Dudu", "linha", 88),
                ("Rony", "linha", 86),
                ("Luiz Adriano", "linha", 83),
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
            "Cruzeiro 2003": [
                ("Gomes", "goleiro", 85),
                ("Maurinho", "linha", 82),
                ("Cris", "linha", 86),
                ("Edu Dracena", "linha", 84),
                ("Leandro", "linha", 83),
                ("Maldonado", "linha", 85),
                ("Augusto Recife", "linha", 82),
                ("Wendell", "linha", 84),
                ("Alex", "linha", 92),
                ("Aristizábal", "linha", 87),
                ("Deivid", "linha", 86),
            ],
            "Internacional 2006": [
                ("Clemer", "goleiro", 86),
                ("Ceará", "linha", 82),
                ("Índio", "linha", 88),
                ("Fabiano Eller", "linha", 84),
                ("Rubens Cardoso", "linha", 81),
                ("Edinho", "linha", 83),
                ("Tinga", "linha", 87),
                ("Alex", "linha", 86),
                ("Fernandão", "linha", 89),
                ("Iarley", "linha", 84),
                ("Alexandre Pato", "linha", 85),
            ],
            "Vasco 1998": [
                ("Carlos Germano", "goleiro", 87),
                ("Vágner", "linha", 82),
                ("Odvan", "linha", 86),
                ("Mauro Galvão", "linha", 87),
                ("Felipe", "linha", 86),
                ("Nasa", "linha", 82),
                ("Luisinho", "linha", 83),
                ("Juninho Pernambucano", "linha", 90),
                ("Pedrinho", "linha", 88),
                ("Donizete", "linha", 86),
                ("Luizão", "linha", 87),
            ],

            # =================== TIMES INTERNACIONAIS ===================
            "Barcelona 2015": [
                ("Ter Stegen", "goleiro", 88),
                ("Dani Alves", "linha", 89),
                ("Piqué", "linha", 88),
                ("Mascherano", "linha", 86),
                ("Jordi Alba", "linha", 87),
                ("Busquets", "linha", 88),
                ("Rakitic", "linha", 87),
                ("Iniesta", "linha", 90),
                ("Messi", "linha", 98),
                ("Suárez", "linha", 93),
                ("Neymar", "linha", 94),
            ],
            "Real Madrid 2017": [
                ("Keylor Navas", "goleiro", 88),
                ("Carvajal", "linha", 87),
                ("Sergio Ramos", "linha", 91),
                ("Varane", "linha", 89),
                ("Marcelo", "linha", 89),
                ("Casemiro", "linha", 88),
                ("Kroos", "linha", 89),
                ("Modric", "linha", 91),
                ("Isco", "linha", 88),
                ("Cristiano Ronaldo", "linha", 97),
                ("Benzema", "linha", 91),
            ],
            "Milan 2007": [
                ("Dida", "goleiro", 87),
                ("Oddo", "linha", 83),
                ("Nesta", "linha", 91),
                ("Maldini", "linha", 92),
                ("Jankulovski", "linha", 82),
                ("Gattuso", "linha", 88),
                ("Ambrosini", "linha", 85),
                ("Pirlo", "linha", 90),
                ("Seedorf", "linha", 89),
                ("Kaká", "linha", 95),
                ("Filippo Inzaghi", "linha", 88),
            ],
            "Bayern de Munique 2013": [
                ("Neuer", "goleiro", 90),
                ("Lahm", "linha", 90),
                ("Boateng", "linha", 86),
                ("Dante", "linha", 84),
                ("Alaba", "linha", 87),
                ("Javi Martínez", "linha", 85),
                ("Schweinsteiger", "linha", 89),
                ("Thomas Müller", "linha", 88),
                ("Robben", "linha", 89),
                ("Ribéry", "linha", 90),
                ("Lewandowski", "linha", 89),
            ],
            "Manchester United 2008": [
                ("Van der Sar", "goleiro", 88),
                ("Wes Brown", "linha", 83),
                ("Rio Ferdinand", "linha", 90),
                ("Vidic", "linha", 89),
                ("Evra", "linha", 87),
                ("Carrick", "linha", 86),
                ("Scholes", "linha", 88),
                ("Giggs", "linha", 87),
                ("Cristiano Ronaldo", "linha", 94),
                ("Rooney", "linha", 90),
                ("Tevez", "linha", 89),
            ],
            "Arsenal 2004 (Invincibles)": [
                ("Lehmann", "goleiro", 88),
                ("Lauren", "linha", 84),
                ("Sol Campbell", "linha", 89),
                ("Kolo Touré", "linha", 86),
                ("Ashley Cole", "linha", 88),
                ("Gilberto Silva", "linha", 86),
                ("Patrick Vieira", "linha", 91),
                ("Ljungberg", "linha", 87),
                ("Pires", "linha", 88),
                ("Bergkamp", "linha", 90),
                ("Thierry Henry", "linha", 94),
            ],
            "Boca Juniors 2007": [
                ("Caranta", "goleiro", 82),
                ("Ibarra", "linha", 84),
                ("Cata Díaz", "linha", 83),
                ("Morel Rodríguez", "linha", 82),
                ("Clemente Rodríguez", "linha", 81),
                ("Ledesma", "linha", 80),
                ("Banega", "linha", 83),
                ("Neri Cardozo", "linha", 81),
                ("Riquelme", "linha", 93),
                ("Palacio", "linha", 86),
                ("Palermo", "linha", 87),
            ],

            # =================== SELEÇÕES LENDÁRIAS ===================
            "Brasil 2002": [
                ("Marcos", "goleiro", 89),
                ("Cafu", "linha", 92),
                ("Lúcio", "linha", 88),
                ("Roque Júnior", "linha", 86),
                ("Edmílson", "linha", 85),
                ("Roberto Carlos", "linha", 93),
                ("Gilberto Silva", "linha", 86),
                ("Kléberson", "linha", 84),
                ("Ronaldinho Gaúcho", "linha", 94),
                ("Rivaldo", "linha", 95),
                ("Ronaldo Fenômeno", "linha", 98),
            ]
        }

        self.stdout.write(self.style.WARNING('Iniciando o cadastro de Elencos e Jogadores Lendários...'))

        total_times = 0
        total_jogadores = 0

        for nome_time, jogadores in dados_elencos.items():
            # Cria ou pega o time
            elenco, created = ElencoHistorico.objects.get_or_create(nome=nome_time)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'🏆 Elenco Cadastrado: {nome_time}'))
                total_times += 1
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Elenco {nome_time} já existe no banco. Sincronizando cartas...'))

            # Adiciona os jogadores ao time
            for j_nome, j_posicao, j_over in jogadores:
                jogador, j_created = CartaJogador.objects.get_or_create(
                    nome=j_nome,
                    elenco=elenco,
                    defaults={'posicao': j_posicao, 'over': j_over}
                )
                
                if j_created:
                    total_jogadores += 1

        self.stdout.write(self.style.SUCCESS(f'🎉 MAGNÍFICO! {total_times} novos times e {total_jogadores} novas cartas foram adicionadas ao Draft!'))