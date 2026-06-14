from django.core.management.base import BaseCommand
from minijogo.models import ElencoHistorico, CartaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com uma NOVA mistura de times lendários, comuns e memes para o Draft X1'

    def handle(self, *args, **kwargs):
        dados_elencos = {
            # =================== TIMES COMUNS / SÉRIE B (OVR 70 - 75) ===================
            "Vila Nova 2024": [
                ("Dênis Júnior", "goleiro", 73),
                ("Elias", "linha", 71),
                ("Quintero", "linha", 72),
                ("Anderson Conceição", "linha", 73),
                ("Eric", "linha", 70),
                ("Ralf", "linha", 74),
                ("Cristiano", "linha", 71),
                ("Igor Henrique", "linha", 72),
                ("Alesson", "linha", 74),
                ("Juan Christian", "linha", 73),
                ("Henrique Almeida", "linha", 73),
            ],
            "Sport Recife 2024": [
                ("Caíque França", "goleiro", 74),
                ("Pedro Lima", "linha", 75),
                ("Rafael Thyere", "linha", 74),
                ("Luciano Castán", "linha", 73),
                ("Felipinho", "linha", 72),
                ("Felipe", "linha", 73),
                ("Fabricio Domínguez", "linha", 74),
                ("Lucas Lima", "linha", 76),
                ("Chrystian Barletta", "linha", 75),
                ("Romarinho", "linha", 74),
                ("Gustavo Coutinho", "linha", 75),
            ],

            # =================== TIMES MÉDIOS / ALTERNATIVOS (OVR 75 - 84) ===================
            "Al Nassr 2024": [
                ("Ospina", "goleiro", 80),
                ("Al-Ghannam", "linha", 76),
                ("Laporte", "linha", 85),
                ("Alamri", "linha", 77),
                ("Telles", "linha", 80),
                ("Brozovic", "linha", 84),
                ("Otávio", "linha", 84),
                ("Talisca", "linha", 83),
                ("Mané", "linha", 84),
                ("Ghareeb", "linha", 77),
                ("Cristiano Ronaldo", "linha", 88),
            ],
            "Athletic Bilbao 2024": [
                ("Unai Simón", "goleiro", 84),
                ("De Marcos", "linha", 80),
                ("Vivian", "linha", 81),
                ("Yeray", "linha", 80),
                ("Yuri Berchiche", "linha", 79),
                ("Vesga", "linha", 78),
                ("Sancet", "linha", 82),
                ("Iñaki Williams", "linha", 81),
                ("Nico Williams", "linha", 83),
                ("Guruzeta", "linha", 79),
                ("Berenguer", "linha", 78),
            ],
            "Fluminense 2008": [
                ("Fernando Henrique", "goleiro", 81),
                ("Gabriel", "linha", 80),
                ("Thiago Silva", "linha", 86),
                ("Luiz Alberto", "linha", 82),
                ("Junior Cesar", "linha", 81),
                ("Ygor", "linha", 79),
                ("Arouca", "linha", 81),
                ("Conca", "linha", 85),
                ("Thiago Neves", "linha", 87),
                ("Cícero", "linha", 83),
                ("Washington", "linha", 84),
            ],

            # =================== TIMES LENDÁRIOS / CLÁSSICOS (OVR 85 - 90+) ===================
            "Inter de Milão 2010": [
                ("Júlio César", "goleiro", 89),
                ("Maicon", "linha", 90),
                ("Lúcio", "linha", 89),
                ("Samuel", "linha", 88),
                ("Zanetti", "linha", 89),
                ("Cambiasso", "linha", 87),
                ("Thiago Motta", "linha", 86),
                ("Sneijder", "linha", 90),
                ("Eto'o", "linha", 88),
                ("Pandev", "linha", 85),
                ("Diego Milito", "linha", 89),
            ],
            "Corinthians 2000": [
                ("Dida", "goleiro", 87),
                ("Índio", "linha", 79),
                ("Fábio Luciano", "linha", 83),
                ("Adílson", "linha", 82),
                ("Kléber", "linha", 81),
                ("Vampeta", "linha", 86),
                ("Rincón", "linha", 85),
                ("Marcelinho Carioca", "linha", 88),
                ("Ricardinho", "linha", 87),
                ("Edílson", "linha", 88),
                ("Luizão", "linha", 87),
            ],
            "Boca Juniors 2000": [
                ("Córdoba", "goleiro", 86),
                ("Ibarra", "linha", 84),
                ("Bermúdez", "linha", 85),
                ("Samuel", "linha", 84),
                ("Arruabarrena", "linha", 82),
                ("Traverso", "linha", 80),
                ("Serna", "linha", 83),
                ("Basualdo", "linha", 82),
                ("Riquelme", "linha", 90),
                ("Delgado", "linha", 83),
                ("Palermo", "linha", 87),
            ],
            "Arsenal 2004 (Invincibles)": [
                ("Lehmann", "goleiro", 87),
                ("Lauren", "linha", 84),
                ("Sol Campbell", "linha", 89),
                ("Kolo Touré", "linha", 86),
                ("Ashley Cole", "linha", 88),
                ("Gilberto Silva", "linha", 86),
                ("Patrick Vieira", "linha", 91),
                ("Ljungberg", "linha", 86),
                ("Pires", "linha", 88),
                ("Bergkamp", "linha", 90),
                ("Thierry Henry", "linha", 94),
            ],

            # =================== OS TIMES MEME / HORRÍVEIS (OVR 48 - 60) ===================
            "San Marino 2024": [
                ("Aldo Simoncini", "goleiro", 58),
                ("D'Addario", "linha", 55),
                ("Rossi", "linha", 54),
                ("Cevoli", "linha", 53),
                ("Tosi", "linha", 55),
                ("Golinucci", "linha", 56),
                ("Mularoni", "linha", 55),
                ("Battistini", "linha", 54),
                ("Lazzari", "linha", 56),
                ("Berardi", "linha", 57),
                ("Nanni", "linha", 58),
            ],
            "Taiti 2013 (Copa das Confederações)": [
                ("Roche", "goleiro", 52),
                ("Simon", "linha", 48),
                ("Ludivion", "linha", 49),
                ("Vallar", "linha", 50),
                ("Lemaire", "linha", 49),
                ("Carine", "linha", 48),
                ("Bourebare", "linha", 50),
                ("A. Tehau", "linha", 51),
                ("L. Tehau", "linha", 51),
                ("J. Tehau", "linha", 52),
                ("Vahirua", "linha", 55),
            ]
        }

        self.stdout.write(self.style.WARNING('Limpando times antigos...'))
        ElencoHistorico.objects.all().delete() # Isso garante que a lista velha seja apagada

        self.stdout.write(self.style.WARNING('Iniciando o cadastro dos novos Elencos...'))

        total_times = 0
        total_jogadores = 0

        for nome_time, jogadores in dados_elencos.items():
            elenco = ElencoHistorico.objects.create(nome=nome_time)
            total_times += 1
            
            for j_nome, j_posicao, j_over in jogadores:
                CartaJogador.objects.create(
                    nome=j_nome,
                    elenco=elenco,
                    posicao=j_posicao,
                    over=j_over
                )
                total_jogadores += 1

        self.stdout.write(self.style.SUCCESS(f'🎉 FEITO! {total_times} times e {total_jogadores} jogadores foram adicionados!'))