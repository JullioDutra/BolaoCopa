from django.core.management.base import BaseCommand
from minijogo.models import ElencoHistorico, CartaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com uma NOVA leva focada na Cartolândia, bizarrices, zebras e esquadrões lendários'

    def handle(self, *args, **kwargs):
        dados_elencos = {
            
            # ====================================================================
            # O TIME DA RESENHA (A COMUNIDADE)
            # ====================================================================
            "Cartolândia FC (A Resenha)": [
                ("PV", "goleiro", 58), ("Matheus", "linha", 71), ("Mark", "linha", 60),
                ("Elves", "linha", 72), ("Pedro", "linha", 57), ("Marcos", "linha", 63),
                ("Fael", "linha", 52), ("Rony", "linha", 73), ("Diogo", "linha", 58),
                ("Arthur", "linha", 59), ("William", "linha", 70),
            ],

            # ====================================================================
            # OS PIORES DOS PIORES (OVR 40 - 70) - FOLCLÓRICOS E DESASTRES
            # ====================================================================
            "Samoa Americana 2001 (A Goleada 31-0)": [
                ("Salapu", "goleiro", 40), ("Luvu", "linha", 42), ("Fatu", "linha", 41),
                ("Sili", "linha", 40), ("Leututu", "linha", 43), ("Sinapati", "linha", 41),
                ("Mulipola", "linha", 42), ("Malu", "linha", 40), ("Savea", "linha", 44),
                ("Feagiai", "linha", 41), ("Immin", "linha", 40),
            ],
            "Taiti 2013 (Copa das Confederações)": [
                ("Roche", "goleiro", 55), ("Simon", "linha", 52), ("Ludivion", "linha", 54),
                ("Vallar", "linha", 53), ("Lemaire", "linha", 51), ("Aitamai", "linha", 50),
                ("Bourebare", "linha", 52), ("Carine", "linha", 50), ("Tehau", "linha", 55),
                ("Chong Hue", "linha", 54), ("Vahirua", "linha", 58),
            ],
            "Fluminense 1999 (Série C)": [
                ("Diogo", "goleiro", 68), ("Flávio", "linha", 65), ("Alexandre", "linha", 66),
                ("Emerson", "linha", 64), ("Paulo Roberto", "linha", 65), ("Roberto Brum", "linha", 67),
                ("Marcão", "linha", 68), ("Yan", "linha", 69), ("Roger", "linha", 71),
                ("Roni", "linha", 72), ("Magno Alves", "linha", 73),
            ],

            # ====================================================================
            # ZEBRAS E HERÓIS IMPROVÁVEIS (OVR 75 - 84)
            # ====================================================================
            "Grécia 2004 (Zebra da Euro)": [
                ("Nikopolidis", "goleiro", 82), ("Seitaridis", "linha", 79), ("Dellas", "linha", 81),
                ("Kapsis", "linha", 80), ("Fyssas", "linha", 78), ("Zagorakis", "linha", 83),
                ("Basinas", "linha", 82), ("Katsouranis", "linha", 80), ("Giannakopoulos", "linha", 79),
                ("Karagounis", "linha", 84), ("Charisteas", "linha", 83),
            ],
            "Once Caldas 2004 (Zebra da Libertadores)": [
                ("Henao", "goleiro", 81), ("Rojas", "linha", 76), ("Vanegas", "linha", 77),
                ("Cataño", "linha", 78), ("García", "linha", 76), ("Velásquez", "linha", 75),
                ("Viáfara", "linha", 79), ("Soto", "linha", 80), ("Valentierra", "linha", 82),
                ("Agudelo", "linha", 77), ("Alcázar", "linha", 79),
            ],
            "Costa Rica 2014 (A Surpresa da Copa)": [
                ("Keylor Navas", "goleiro", 84), ("Gamboa", "linha", 78), ("Duarte", "linha", 79),
                ("González", "linha", 79), ("Umaña", "linha", 78), ("Díaz", "linha", 77),
                ("Borges", "linha", 80), ("Tejeda", "linha", 79), ("Bolaños", "linha", 78),
                ("Bryan Ruiz", "linha", 83), ("Joel Campbell", "linha", 82),
            ],

            # ====================================================================
            # OS BONS E LENDÁRIOS (OVR 85 - 98)
            # ====================================================================
            "Barcelona 2011 (O Tiki-Taka)": [
                ("Víctor Valdés", "goleiro", 88), ("Dani Alves", "linha", 87), ("Piqué", "linha", 89),
                ("Puyol", "linha", 91), ("Abidal", "linha", 86), ("Busquets", "linha", 89),
                ("Xavi", "linha", 94), ("Iniesta", "linha", 93), ("Pedro", "linha", 87),
                ("Messi", "linha", 98), ("David Villa", "linha", 89),
            ],
            "Arsenal 2004 (Os Invencíveis)": [
                ("Lehmann", "goleiro", 88), ("Lauren", "linha", 85), ("Kolo Touré", "linha", 86),
                ("Sol Campbell", "linha", 88), ("Ashley Cole", "linha", 89), ("Gilberto Silva", "linha", 87),
                ("Vieira", "linha", 91), ("Ljungberg", "linha", 86), ("Pires", "linha", 87),
                ("Bergkamp", "linha", 89), ("Thierry Henry", "linha", 94),
            ],
            "Santos 2011 (Meninos da Vila)": [
                ("Rafael", "goleiro", 83), ("Danilo", "linha", 82), ("Edu Dracena", "linha", 84),
                ("Durval", "linha", 83), ("Léo", "linha", 84), ("Arouca", "linha", 85),
                ("Henrique", "linha", 82), ("Elano", "linha", 86), ("Ganso", "linha", 87),
                ("Neymar", "linha", 92), ("Borges", "linha", 84),
            ],
            "Milan 2005 (Esquadrão Lenda)": [
                ("Dida", "goleiro", 90), ("Cafu", "linha", 92), ("Stam", "linha", 89),
                ("Nesta", "linha", 91), ("Maldini", "linha", 93), ("Pirlo", "linha", 92),
                ("Gattuso", "linha", 91), ("Seedorf", "linha", 90), ("Kaká", "linha", 93),
                ("Shevchenko", "linha", 91), ("Crespo", "linha", 90),
            ],
            "Real Madrid 2017 (Tricampeão Europeu)": [
                ("Keylor Navas", "goleiro", 88), ("Carvajal", "linha", 86), ("Varane", "linha", 87),
                ("Sergio Ramos", "linha", 92), ("Marcelo", "linha", 89), ("Casemiro", "linha", 88),
                ("Kroos", "linha", 90), ("Modric", "linha", 91), ("Isco", "linha", 89),
                ("Benzema", "linha", 88), ("Cristiano Ronaldo", "linha", 96),
            ]
        }

        self.stdout.write(self.style.WARNING('Limpando times antigos...'))
        ElencoHistorico.objects.all().delete()

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
