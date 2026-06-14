from django.core.management.base import BaseCommand
from minijogo.models import ElencoHistorico, CartaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com uma mistura de times lendários e times COMUNS/FRACOS para o Draft X1'

    def handle(self, *args, **kwargs):
        dados_elencos = {
            # =================== TIMES COMUNS / MÉDIOS (OVR 70 - 78) ===================
            "Criciúma 2024": [
                ("Gustavo", "goleiro", 74),
                ("Claudinho", "linha", 72),
                ("Rodrigo", "linha", 73),
                ("Wilker Ángel", "linha", 72),
                ("Marcelo Hermes", "linha", 71),
                ("Barreto", "linha", 73),
                ("Higor Meritão", "linha", 72),
                ("Fellipe Mateus", "linha", 74),
                ("Matheusinho", "linha", 75),
                ("Bolasie", "linha", 76),
                ("Arthur Caíke", "linha", 73),
            ],
            "Juventude 2024": [
                ("Gabriel", "goleiro", 74),
                ("João Lucas", "linha", 72),
                ("Danilo Boza", "linha", 73),
                ("Zé Marcos", "linha", 72),
                ("Alan Ruschel", "linha", 74),
                ("Jadson", "linha", 73),
                ("Jean Carlos", "linha", 75),
                ("Nenê", "linha", 76),
                ("Lucas Barbosa", "linha", 74),
                ("Erick Farias", "linha", 73),
                ("Gilberto", "linha", 75),
            ],
            "Vitória 2024": [
                ("Lucas Arcanjo", "goleiro", 75),
                ("Zeca", "linha", 73),
                ("Camutanga", "linha", 74),
                ("Wagner Leonardo", "linha", 74),
                ("PK", "linha", 72),
                ("Willian Oliveira", "linha", 73),
                ("Dudu", "linha", 72),
                ("Matheuzinho", "linha", 76),
                ("Osvaldo", "linha", 75),
                ("Iury Castilho", "linha", 73),
                ("Alerrandro", "linha", 74),
            ],
            "Cuiabá 2024": [
                ("Walter", "goleiro", 77),
                ("Matheus Alexandre", "linha", 73),
                ("Marllon", "linha", 74),
                ("Empereur", "linha", 74),
                ("Ramon", "linha", 72),
                ("Lucas Mineiro", "linha", 73),
                ("Fernando Sobral", "linha", 74),
                ("Denilson", "linha", 72),
                ("Clayson", "linha", 75),
                ("Derik Lacerda", "linha", 73),
                ("Isidro Pitta", "linha", 76),
            ],
            "Luton Town 2024 (ING)": [
                ("Kaminski", "goleiro", 75),
                ("Kaboré", "linha", 74),
                ("Mengi", "linha", 73),
                ("Lockyer", "linha", 74),
                ("Bell", "linha", 74),
                ("Nakamba", "linha", 75),
                ("Barkley", "linha", 78),
                ("Doughty", "linha", 74),
                ("Chong", "linha", 76),
                ("Morris", "linha", 77),
                ("Adebayo", "linha", 76),
            ],

            # =================== TIMES BONS / FORTES (OVR 78 - 85) ===================
            "Vasco 2024": [
                ("Léo Jardim", "goleiro", 80),
                ("Paulo Henrique", "linha", 76),
                ("Maicon", "linha", 77),
                ("Léo", "linha", 75),
                ("Lucas Piton", "linha", 78),
                ("Sforza", "linha", 76),
                ("Hugo Moura", "linha", 77),
                ("Payet", "linha", 82),
                ("Adson", "linha", 76),
                ("David", "linha", 75),
                ("Vegetti", "linha", 81),
            ],
            "Bayer Leverkusen 2024": [
                ("Hradecky", "goleiro", 86),
                ("Frimpong", "linha", 85),
                ("Tah", "linha", 84),
                ("Tapsoba", "linha", 85),
                ("Grimaldo", "linha", 86),
                ("Xhaka", "linha", 86),
                ("Palacios", "linha", 85),
                ("Hofmann", "linha", 85),
                ("Wirtz", "linha", 88),
                ("Schick", "linha", 86),
                ("Boniface", "linha", 84),
            ],
            
            # =================== TIMES LENDÁRIOS / RAROS (OVR 85 - 90+) ===================
            "Real Madrid 2024": [
                ("Courtois", "goleiro", 90),
                ("Carvajal", "linha", 86),
                ("Rüdiger", "linha", 88),
                ("Militão", "linha", 87),
                ("Mendy", "linha", 84),
                ("Tchouaméni", "linha", 87),
                ("Kroos", "linha", 89),
                ("Valverde", "linha", 88),
                ("Bellingham", "linha", 91),
                ("Rodrygo", "linha", 87),
                ("Vini Jr", "linha", 91),
            ],
            "Manchester City 2023": [
                ("Ederson", "goleiro", 89),
                ("Kyle Walker", "linha", 86),
                ("Rúben Dias", "linha", 88),
                ("Akanji", "linha", 86),
                ("Aké", "linha", 85),
                ("Rodri", "linha", 89),
                ("Gündogan", "linha", 87),
                ("De Bruyne", "linha", 92),
                ("Bernardo Silva", "linha", 89),
                ("Grealish", "linha", 87),
                ("Haaland", "linha", 92),
            ],

            # =================== O TIME MEME (OVR 50 - 60) ===================
            "Íbis 2000 (Pior do Mundo)": [
                ("Jailson", "goleiro", 55),
                ("Carlinhos", "linha", 52),
                ("Zezinho", "linha", 50),
                ("Beto", "linha", 51),
                ("Rato", "linha", 53),
                ("Tonho", "linha", 54),
                ("Zé", "linha", 52),
                ("Chiquinho", "linha", 55),
                ("Mauro Shampoo", "linha", 59),
                ("Vavá", "linha", 53),
                ("Garrinchinha", "linha", 56),
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