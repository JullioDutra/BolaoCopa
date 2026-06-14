from django.core.management.base import BaseCommand
from minijogo.models import ElencoHistorico, CartaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com uma NOVA leva focada em zebras, piores campanhas e esquadrões históricos'

    def handle(self, *args, **kwargs):
        dados_elencos = {
            # =================== OS PIORES DOS PIORES (OVR 60 - 70) ===================
            "América-RN 2007 (Pior campanha do BR)": [
                ("Andrey", "goleiro", 68),
                ("Carlos Eduardo", "linha", 65),
                ("Machado", "linha", 66),
                ("Rogélio", "linha", 65),
                ("Berg", "linha", 67),
                ("Marquinhos", "linha", 68),
                ("Leandro Sena", "linha", 69),
                ("Souza", "linha", 71),
                ("Geovane", "linha", 66),
                ("Aranda", "linha", 65),
                ("Reinaldo", "linha", 67),
            ],
            "Derby County 2008 (Pior campanha PL)": [
                ("Roy Carroll", "goleiro", 70),
                ("Tyrone Mears", "linha", 67),
                ("Claude Davis", "linha", 69),
                ("Darren Moore", "linha", 68),
                ("Andy Todd", "linha", 66),
                ("Robbie Savage", "linha", 72),
                ("Stephen Pearson", "linha", 70),
                ("Giles Barnes", "linha", 69),
                ("Eddie Lewis", "linha", 68),
                ("Kenny Miller", "linha", 71),
                ("Emanuel Villa", "linha", 69),
            ],

            # =================== TIMES SURPRESA E HERÓIS (OVR 78 - 84) ===================
            "Goiás 2005 (Libertadores)": [
                ("Harlei", "goleiro", 81),
                ("Paulo Baier", "linha", 85),
                ("Rodrigo", "linha", 82),
                ("Aldo", "linha", 80),
                ("Jadílson", "linha", 81),
                ("Cléber", "linha", 79),
                ("Josué", "linha", 84),
                ("Romerito", "linha", 81),
                ("Jorge Wagner", "linha", 83),
                ("Souza", "linha", 84),
                ("Dimba", "linha", 82),
            ],
            "Paysandu 2002 (Copa dos Campeões)": [
                ("Marcão", "goleiro", 78),
                ("Marcos", "linha", 76),
                ("Gino", "linha", 77),
                ("Sérgio", "linha", 75),
                ("Luís Fernando", "linha", 76),
                ("Sandro", "linha", 78),
                ("Vandick", "linha", 77),
                ("Vélber", "linha", 79),
                ("Jóbson", "linha", 81),
                ("Iarley", "linha", 83),
                ("Vanderson", "linha", 80),
            ],
            "Chapecoense 2016 (Eternos)": [
                ("Danilo", "goleiro", 83),
                ("Gimenez", "linha", 78),
                ("Thiego", "linha", 80),
                ("Neto", "linha", 79),
                ("Dener", "linha", 78),
                ("Josimar", "linha", 77),
                ("Cleber Santana", "linha", 81),
                ("Gil", "linha", 78),
                ("Ananias", "linha", 81),
                ("Tiaguinho", "linha", 79),
                ("Bruno Rangel", "linha", 82),
            ],
            "Leicester City 2016 (O Milagre)": [
                ("Schmeichel", "goleiro", 85),
                ("Simpson", "linha", 80),
                ("Wes Morgan", "linha", 83),
                ("Huth", "linha", 82),
                ("Fuchs", "linha", 81),
                ("Kanté", "linha", 88),
                ("Drinkwater", "linha", 82),
                ("Albrighton", "linha", 81),
                ("Mahrez", "linha", 87),
                ("Vardy", "linha", 88),
                ("Okazaki", "linha", 83),
            ],

            # =================== LENDÁRIOS DA AMÉRICA DO SUL (OVR 83 - 92) ===================
            "São Paulo 1992 (Mundial)": [
                ("Zetti", "goleiro", 88),
                ("Cafu", "linha", 89),
                ("Antônio Carlos", "linha", 85),
                ("Ronaldão", "linha", 86),
                ("Ronaldo Luís", "linha", 84),
                ("Pintado", "linha", 85),
                ("Toninho Cerezo", "linha", 87),
                ("Raí", "linha", 92),
                ("Palhinha", "linha", 86),
                ("Müller", "linha", 88),
                ("Macedo", "linha", 84),
            ],
            "Atlético Mineiro 2021": [
                ("Everson", "goleiro", 84),
                ("Mariano", "linha", 82),
                ("Nathan Silva", "linha", 83),
                ("Junior Alonso", "linha", 84),
                ("Guilherme Arana", "linha", 86),
                ("Allan", "linha", 83),
                ("Jair", "linha", 82),
                ("Zaracho", "linha", 84),
                ("Nacho Fernández", "linha", 85),
                ("Keno", "linha", 83),
                ("Hulk", "linha", 89),
            ],
            "River Plate 2018 (Libertadores)": [
                ("Armani", "goleiro", 84),
                ("Montiel", "linha", 83),
                ("Maidana", "linha", 82),
                ("Pinola", "linha", 82),
                ("Casco", "linha", 81),
                ("Enzo Pérez", "linha", 84),
                ("Ponzio", "linha", 83),
                ("Palacios", "linha", 83),
                ("Pity Martínez", "linha", 86),
                ("Pratto", "linha", 84),
                ("Borré", "linha", 83),
            ],

            # =================== LENDÁRIOS DA EUROPA (OVR 88 - 95) ===================
            "Espanha 2010 (Copa do Mundo)": [
                ("Casillas", "goleiro", 92),
                ("Sergio Ramos", "linha", 89),
                ("Puyol", "linha", 91),
                ("Piqué", "linha", 88),
                ("Capdevila", "linha", 85),
                ("Busquets", "linha", 87),
                ("Xabi Alonso", "linha", 89),
                ("Xavi", "linha", 92),
                ("Iniesta", "linha", 93),
                ("Pedro", "linha", 87),
                ("David Villa", "linha", 89),
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