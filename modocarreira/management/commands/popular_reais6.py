from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from modocarreira.models import ServidorConfig, Campeonato, Clube, Avatar
import random

class Command(BaseCommand):
    help = 'Popula a base de dados com Campeonatos e Jogadores REAIS e ATUAIS de 11 ligas internacionais (v3 - edição máxima).'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('A abrir o mapa-múndi do futebol para o Metaverso (v3 - quase todas as ligas completas)...'))

        config = ServidorConfig.objects.first()
        if not config:
            self.stdout.write(self.style.ERROR('Por favor, corra primeiro o "popular_carreira" para criar o servidor.'))
            return

        # ==========================================
        # BASE DE DADOS REAL — 11 Ligas Internacionais (temporada 2025/26 - 2026)
        # Não é o elenco completo (18-20 titulares) como no Brasileirão: aqui
        # trazemos os clubes mais relevantes de cada liga com os jogadores
        # reais mais em evidência (astros e titulares confirmados), verificados
        # via pesquisa. Ligas com times menos midiáticos (ex: Paraguai) têm
        # menos nomes confirmados — está sinalizado nos comentários.
        # ==========================================
        ligas = {
            'Liga Profesional Argentina': {
                'codigo': 'ARG', 'clubes': {
                    'River Plate': {'sigla': 'RIV', 'prestigio': 88, 'orcamento': 900000, 'jogadores': [
                        ('Franco Armani', 'GK', 78), ('Gonzalo Montiel', 'RB', 79), ('Lucas Martínez Quarta', 'CB', 79),
                        ('Marcos Acuña', 'LB', 80), ('Aníbal Moreno', 'DM', 78), ('Fausto Vera', 'CM', 78),
                        ('Sebastián Driussi', 'AM', 81), ('Kendry Páez', 'AM', 78), ('Facundo Colidio', 'ST', 78),
                    ]},
                    'Boca Juniors': {'sigla': 'BOC', 'prestigio': 87, 'orcamento': 850000, 'jogadores': [
                        ('Leandro Paredes', 'DM', 82), ('Miguel Merentiel', 'ST', 80), ('Adam Bareiro', 'ST', 78),
                        ('Edinson Cavani', 'ST', 80),
                    ]},
                    'Racing Club': {'sigla': 'RAC', 'prestigio': 82, 'orcamento': 550000, 'jogadores': [
                        ('Valentín Carboni', 'AM', 79), ('Matko Miljevic', 'ST', 76),
                    ]},
                    'Estudiantes de La Plata': {'sigla': 'EST', 'prestigio': 80, 'orcamento': 480000, 'jogadores': [
                        ('Fernando Muslera', 'GK', 78),
                    ]},
                    'Rosario Central': {'sigla': 'ROS', 'prestigio': 80, 'orcamento': 460000, 'jogadores': [
                        ('Ángel Di María', 'AM', 85), ('Jeremías Ledesma', 'GK', 76), ('Gastón Ávila', 'CB', 77),
                        ('Jaminton Campaz', 'RW', 78),
                    ]},
                    'Independiente': {'sigla': 'IND', 'prestigio': 81, 'orcamento': 480000, 'jogadores': [
                        ('Rodrigo Rey', 'GK', 76), ('Gabriel Ávalos', 'ST', 79), ('Federico Mancuello', 'CM', 77),
                        ('Iván Marcone', 'DM', 77),
                    ]},
                    'Huracán': {'sigla': 'HUR', 'prestigio': 76, 'orcamento': 320000, 'jogadores': [
                        ('Hernán Galíndez', 'GK', 76), ('Jordy Caicedo', 'ST', 76),
                    ]},
                    'San Lorenzo': {'sigla': 'SLO', 'prestigio': 78, 'orcamento': 350000, 'jogadores': [
                        ('Orlando Gil', 'DM', 75),
                    ]},
                    'Vélez Sarsfield': {'sigla': 'VEL', 'prestigio': 79, 'orcamento': 380000, 'jogadores': [
                        ('Álvaro Montero', 'GK', 78),
                    ]},
                    'Talleres': {'sigla': 'TAL', 'prestigio': 78, 'orcamento': 340000, 'jogadores': [
                        ('Alejandro Maidana', 'CB', 75),
                    ]},
                    'Lanús': {'sigla': 'LAN', 'prestigio': 76, 'orcamento': 300000, 'jogadores': [
                        ('José Canale', 'CM', 74),
                    ]},
                    "Newell's Old Boys": {'sigla': 'NWB', 'prestigio': 75, 'orcamento': 290000, 'jogadores': [
                        ('Ignacio Malcorra', 'AM', 74),
                    ]},
                    'Argentinos Juniors': {'sigla': 'ARG', 'prestigio': 74, 'orcamento': 270000, 'jogadores': [
                        ('Alan Lescano', 'CM', 72),
                    ]},
                    'Defensa y Justicia': {'sigla': 'DYJ', 'prestigio': 72, 'orcamento': 250000, 'jogadores': [
                        ('Lucas Rodríguez', 'RW', 74),
                    ]},
                    'Godoy Cruz': {'sigla': 'GOD', 'prestigio': 71, 'orcamento': 230000, 'jogadores': [
                        ('José Rodríguez', 'CM', 72),
                    ]},
                    'Platense': {'sigla': 'PLA', 'prestigio': 70, 'orcamento': 220000, 'jogadores': [
                        ('Bruno Pittón', 'LB', 71),
                    ]},
                }
            },
            'Primera División Paraguay': {
                # NOTA: liga com pouquíssima cobertura de imprensa internacional;
                # poucos jogadores confirmados nominalmente nas fontes disponíveis.
                'codigo': 'PAR', 'clubes': {
                    'Cerro Porteño': {'sigla': 'CER', 'prestigio': 68, 'orcamento': 180000, 'jogadores': [
                        ('Robert Piris Da Motta', 'DM', 74),
                    ]},
                    'Olimpia': {'sigla': 'OLI', 'prestigio': 68, 'orcamento': 175000, 'jogadores': [
                        ('Richard Sánchez', 'AM', 74),
                    ]},
                    'Libertad': {'sigla': 'LIB', 'prestigio': 65, 'orcamento': 150000, 'jogadores': [
                        ('Federico Carrizo', 'AM', 73),
                    ]},
                    'Guaraní': {'sigla': 'GUA', 'prestigio': 60, 'orcamento': 120000, 'jogadores': [
                        ('Blas Armoa', 'LW', 74),
                    ]},
                    'Nacional': {'sigla': 'NAC', 'prestigio': 62, 'orcamento': 130000, 'jogadores': [
                        ('Fabián Franco', 'ST', 73), ('Richard Prieto', 'CM', 72), ('Ignacio Bailone', 'AM', 73),
                        ('Matías Almeida', 'CB', 71),
                    ]},
                    'Sportivo Luqueño': {'sigla': 'LUQ', 'prestigio': 58, 'orcamento': 110000, 'jogadores': [
                        ('Alfredo Aguilar', 'GK', 71), ('Giovanni Bogado', 'AM', 72), ('Aldo Maíz', 'CM', 70),
                    ]},
                    'Sportivo Ameliano': {'sigla': 'AME', 'prestigio': 55, 'orcamento': 95000, 'jogadores': [
                        ('Luis Ayala', 'CM', 69),
                    ]},
                    'Sportivo Trinidense': {'sigla': 'TRI', 'prestigio': 54, 'orcamento': 90000, 'jogadores': [
                        ('Ángel Cardozo Lucena', 'ST', 71),
                    ]},
                }
            },
            'La Liga (Espanha)': {
                'codigo': 'ESP', 'clubes': {
                    'Real Madrid': {'sigla': 'RMA', 'prestigio': 96, 'orcamento': 2200000, 'jogadores': [
                        ('Thibaut Courtois', 'GK', 89), ('Éder Militão', 'CB', 85), ('Dean Huijsen', 'CB', 83),
                        ('Trent Alexander-Arnold', 'RB', 86), ('Federico Valverde', 'CM', 88), ('Jude Bellingham', 'AM', 90),
                        ('Vinícius Júnior', 'LW', 91), ('Rodrygo', 'RW', 86), ('Kylian Mbappé', 'ST', 93),
                    ]},
                    'Barcelona': {'sigla': 'BAR', 'prestigio': 95, 'orcamento': 2000000, 'jogadores': [
                        ('Joan García', 'GK', 82), ('Ronald Araújo', 'CB', 85), ('Pau Cubarsí', 'CB', 84),
                        ('Alejandro Balde', 'LB', 84), ('Pedri', 'CM', 89), ('Gavi', 'CM', 85),
                        ('Raphinha', 'LW', 89), ('Lamine Yamal', 'RW', 91), ('Ferran Torres', 'ST', 82),
                    ]},
                    'Atlético de Madrid': {'sigla': 'ATM', 'prestigio': 89, 'orcamento': 1100000, 'jogadores': [
                        ('Jan Oblak', 'GK', 87), ('José María Giménez', 'CB', 83), ('Koke', 'CM', 82),
                        ('Antoine Griezmann', 'AM', 87), ('Julián Álvarez', 'ST', 88), ('Alex Baena', 'AM', 82),
                    ]},
                    'Athletic Bilbao': {'sigla': 'ATH', 'prestigio': 82, 'orcamento': 400000, 'jogadores': [
                        ('Unai Simón', 'GK', 84), ('Nico Williams', 'LW', 86), ('Iñaki Williams', 'ST', 82),
                        ('Oihan Sancet', 'AM', 82),
                    ]},
                    'Real Sociedad': {'sigla': 'RSO', 'prestigio': 79, 'orcamento': 320000, 'jogadores': [
                        ('Mikel Oyarzabal', 'ST', 84), ('Take Kubo', 'RW', 83), ('Ander Barrenetxea', 'LW', 79),
                    ]},
                    'Villarreal': {'sigla': 'VIL', 'prestigio': 78, 'orcamento': 300000, 'jogadores': [
                        ('Ayoze Pérez', 'ST', 80), ('Yeremy Pino', 'RW', 79),
                    ]},
                    'Real Betis': {'sigla': 'BET', 'prestigio': 77, 'orcamento': 280000, 'jogadores': [
                        ('Isco', 'AM', 81), ('Antony', 'RW', 80),
                    ]},
                    'Sevilla': {'sigla': 'SEV', 'prestigio': 76, 'orcamento': 260000, 'jogadores': [
                        ('Isaac Romero', 'ST', 77), ('Djibril Sow', 'CM', 78),
                    ]},
                    'Valencia': {'sigla': 'VAL', 'prestigio': 75, 'orcamento': 240000, 'jogadores': [
                        ('Hugo Duro', 'ST', 77), ('Javi Guerra', 'CM', 78),
                    ]},
                    'Girona': {'sigla': 'GIR', 'prestigio': 74, 'orcamento': 230000, 'jogadores': [
                        ('Yangel Herrera', 'CM', 78), ('Miguel Gutiérrez', 'LB', 78),
                    ]},
                    'Celta de Vigo': {'sigla': 'CEL', 'prestigio': 74, 'orcamento': 220000, 'jogadores': [
                        ('Iago Aspas', 'ST', 82), ('Williot Swedberg', 'AM', 76),
                    ]},
                    'Osasuna': {'sigla': 'OSA', 'prestigio': 71, 'orcamento': 180000, 'jogadores': [
                        ('Ante Budimir', 'ST', 79),
                    ]},
                    'RCD Mallorca': {'sigla': 'MLL', 'prestigio': 70, 'orcamento': 170000, 'jogadores': [
                        ('Vedat Muriqi', 'ST', 78),
                    ]},
                    'Getafe': {'sigla': 'GET', 'prestigio': 70, 'orcamento': 170000, 'jogadores': [
                        ('Borja Mayoral', 'ST', 78),
                    ]},
                    'Rayo Vallecano': {'sigla': 'RAY', 'prestigio': 71, 'orcamento': 175000, 'jogadores': [
                        ('Isi Palazón', 'RW', 79),
                    ]},
                    'RCD Espanyol': {'sigla': 'RCDE', 'prestigio': 68, 'orcamento': 150000, 'jogadores': [
                        ('Javi Puado', 'ST', 76),
                    ]},
                    'Deportivo Alavés': {'sigla': 'ALA', 'prestigio': 68, 'orcamento': 150000, 'jogadores': [
                        ('Kike García', 'ST', 74),
                    ]},
                    'Real Oviedo': {'sigla': 'OVI', 'prestigio': 63, 'orcamento': 110000, 'jogadores': [
                        ('Santiago Colombatto', 'CM', 73),
                    ]},
                    'Elche CF': {'sigla': 'ELC', 'prestigio': 62, 'orcamento': 105000, 'jogadores': [
                        ('André Silva', 'ST', 74),
                    ]},
                    'Levante UD': {'sigla': 'LEV', 'prestigio': 62, 'orcamento': 105000, 'jogadores': [
                        ('Iván Romero', 'RW', 73),
                    ]},
                }
            },
            'Serie A (Itália)': {
                'codigo': 'ITA', 'clubes': {
                    'Inter de Milão': {'sigla': 'INT', 'prestigio': 92, 'orcamento': 1300000, 'jogadores': [
                        ('Yann Sommer', 'GK', 85), ('Alessandro Bastoni', 'CB', 87), ('Federico Dimarco', 'LB', 84),
                        ('Hakan Çalhanoğlu', 'DM', 86), ('Nicolò Barella', 'CM', 87), ('Lautaro Martínez', 'ST', 89),
                        ('Marcus Thuram', 'ST', 87),
                    ]},
                    'Juventus': {'sigla': 'JUV', 'prestigio': 90, 'orcamento': 1100000, 'jogadores': [
                        ('Michele Di Gregorio', 'GK', 82), ('Gleison Bremer', 'CB', 85), ('Teun Koopmeiners', 'CM', 82),
                        ('Kenan Yıldız', 'AM', 84), ('Jonathan David', 'ST', 82),
                    ]},
                    'AC Milan': {'sigla': 'MIL', 'prestigio': 90, 'orcamento': 1000000, 'jogadores': [
                        ('Mike Maignan', 'GK', 87), ('Rafael Leão', 'LW', 86), ('Christian Pulisic', 'RW', 84),
                        ('Gonçalo Ramos', 'ST', 83),
                    ]},
                    'Napoli': {'sigla': 'NAP', 'prestigio': 89, 'orcamento': 900000, 'jogadores': [
                        ('Alex Meret', 'GK', 82), ('Giovanni Di Lorenzo', 'RB', 82), ('Scott McTominay', 'CM', 84),
                        ('Kevin De Bruyne', 'AM', 88), ('Romelu Lukaku', 'ST', 83),
                    ]},
                    'Atalanta': {'sigla': 'ATA', 'prestigio': 84, 'orcamento': 500000, 'jogadores': [
                        ('Marten de Roon', 'DM', 79), ('Ademola Lookman', 'RW', 85), ('Charles De Ketelaere', 'AM', 82),
                    ]},
                    'AS Roma': {'sigla': 'ROM', 'prestigio': 83, 'orcamento': 480000, 'jogadores': [
                        ('Paulo Dybala', 'AM', 85), ('Artem Dovbyk', 'ST', 80),
                    ]},
                    'Fiorentina': {'sigla': 'FIO', 'prestigio': 78, 'orcamento': 320000, 'jogadores': [
                        ('Moise Kean', 'ST', 81), ('Albert Guðmundsson', 'AM', 79),
                    ]},
                    'Bologna': {'sigla': 'BOL', 'prestigio': 79, 'orcamento': 300000, 'jogadores': [
                        ('Riccardo Orsolini', 'RW', 81), ('Santiago Castro', 'ST', 78),
                    ]},
                    'Torino': {'sigla': 'TOR', 'prestigio': 75, 'orcamento': 250000, 'jogadores': [
                        ('Nikola Vlašić', 'AM', 78),
                    ]},
                    'Lazio': {'sigla': 'LAZ', 'prestigio': 82, 'orcamento': 400000, 'jogadores': [
                        ('Mattia Zaccagni', 'LW', 81), ('Valentín Castellanos', 'ST', 79),
                    ]},
                    'Como': {'sigla': 'COM', 'prestigio': 74, 'orcamento': 260000, 'jogadores': [
                        ('Nico Paz', 'AM', 82), ('Álvaro Morata', 'ST', 80), ('Martin Baturina', 'AM', 78),
                    ]},
                    'Parma': {'sigla': 'PARM', 'prestigio': 71, 'orcamento': 200000, 'jogadores': [
                        ('Patrick Cutrone', 'ST', 76), ('Mattia Viviani', 'CM', 72),
                    ]},
                    'Genoa': {'sigla': 'GEN', 'prestigio': 70, 'orcamento': 190000, 'jogadores': [
                        ('Morten Frendrup', 'CM', 76),
                    ]},
                    'Cagliari': {'sigla': 'CAG', 'prestigio': 69, 'orcamento': 180000, 'jogadores': [
                        ('Andrea Belotti', 'ST', 76), ('Sebastiano Esposito', 'ST', 76),
                    ]},
                    'Hellas Verona': {'sigla': 'VER', 'prestigio': 66, 'orcamento': 150000, 'jogadores': [
                        ('Josh Bowie', 'ST', 72),
                    ]},
                    'Udinese': {'sigla': 'UDI', 'prestigio': 73, 'orcamento': 220000, 'jogadores': [
                        ('Nicolò Zaniolo', 'AM', 78),
                    ]},
                    'Lecce': {'sigla': 'LEC', 'prestigio': 65, 'orcamento': 140000, 'jogadores': [
                        ('Walid Cheddira', 'ST', 74),
                    ]},
                    'Sassuolo': {'sigla': 'SAS', 'prestigio': 68, 'orcamento': 170000, 'jogadores': [
                        ('Domenico Berardi', 'RW', 79),
                    ]},
                    'Pisa': {'sigla': 'PIS', 'prestigio': 63, 'orcamento': 130000, 'jogadores': [
                        ('Raúl Albiol', 'CB', 74), ('Juan Cuadrado', 'RW', 74), ('M\'Bala Nzola', 'ST', 74),
                    ]},
                    'Cremonese': {'sigla': 'CRE', 'prestigio': 60, 'orcamento': 110000, 'jogadores': [
                        ('Ciro Immobile', 'ST', 76),
                    ]},
                }
            },
            'Bundesliga (Alemanha)': {
                'codigo': 'GER', 'clubes': {
                    'Bayern de Munique': {'sigla': 'FCB', 'prestigio': 94, 'orcamento': 1400000, 'jogadores': [
                        ('Manuel Neuer', 'GK', 85), ('Dayot Upamecano', 'CB', 85), ('Jonathan Tah', 'CB', 85), ('Joshua Kimmich', 'CM', 88),
                        ('Jamal Musiala', 'AM', 90), ('Michael Olise', 'RW', 87), ('Luis Díaz', 'LW', 87),
                        ('Harry Kane', 'ST', 91),
                    ]},
                    'Bayer Leverkusen': {'sigla': 'B04', 'prestigio': 86, 'orcamento': 650000, 'jogadores': [
                        ('Mark Flekken', 'GK', 79), ('Jarell Quansah', 'CB', 79), ('Malik Tillman', 'AM', 80), ('Patrik Schick', 'ST', 84),
                    ]},
                    'Borussia Dortmund': {'sigla': 'BVB', 'prestigio': 86, 'orcamento': 600000, 'jogadores': [
                        ('Gregor Kobel', 'GK', 85), ('Nico Schlotterbeck', 'CB', 82), ('Julian Brandt', 'AM', 82),
                        ('Karim Adeyemi', 'RW', 81), ('Serhou Guirassy', 'ST', 84),
                    ]},
                    'RB Leipzig': {'sigla': 'RBL', 'prestigio': 82, 'orcamento': 500000, 'jogadores': [
                        ('Castello Lukeba', 'CB', 80), ('Lois Openda', 'ST', 83),
                    ]},
                    'Eintracht Frankfurt': {'sigla': 'SGE', 'prestigio': 78, 'orcamento': 380000, 'jogadores': [
                        ('Jonathan Burkardt', 'ST', 79), ('Can Uzun', 'AM', 78), ('Ritsu Doan', 'RW', 79),
                    ]},
                    'VfB Stuttgart': {'sigla': 'VFB', 'prestigio': 77, 'orcamento': 350000, 'jogadores': [
                        ('Deniz Undav', 'ST', 82), ('Chris Führich', 'RW', 79),
                    ]},
                    'VfL Wolfsburg': {'sigla': 'WOB', 'prestigio': 73, 'orcamento': 260000, 'jogadores': [
                        ('Jonas Wind', 'ST', 79),
                    ]},
                    'SC Freiburg': {'sigla': 'SCF', 'prestigio': 74, 'orcamento': 270000, 'jogadores': [
                        ('Vincenzo Grifo', 'AM', 79),
                    ]},
                    'Werder Bremen': {'sigla': 'SVW', 'prestigio': 72, 'orcamento': 240000, 'jogadores': [
                        ('Marvin Ducksch', 'ST', 78),
                    ]},
                    'Borussia Mönchengladbach': {'sigla': 'BMG', 'prestigio': 73, 'orcamento': 250000, 'jogadores': [
                        ('Alassane Pléa', 'ST', 78),
                    ]},
                    'Hamburger SV': {'sigla': 'HSV', 'prestigio': 68, 'orcamento': 180000, 'jogadores': [
                        ('Robert Glatzel', 'ST', 75),
                    ]},
                    '1. FC Köln': {'sigla': 'KOE', 'prestigio': 66, 'orcamento': 160000, 'jogadores': [
                        ('Damion Downs', 'ST', 73),
                    ]},
                    '1. FSV Mainz 05': {'sigla': 'M05', 'prestigio': 71, 'orcamento': 200000, 'jogadores': [
                        ('Jae-sung Lee', 'AM', 76),
                    ]},
                    'TSG Hoffenheim': {'sigla': 'TSG', 'prestigio': 69, 'orcamento': 190000, 'jogadores': [
                        ('Andrej Kramarić', 'ST', 78),
                    ]},
                    'FC St. Pauli': {'sigla': 'STP', 'prestigio': 64, 'orcamento': 140000, 'jogadores': [
                        ('Elias Saad', 'RW', 72),
                    ]},
                    'Union Berlin': {'sigla': 'FCU', 'prestigio': 70, 'orcamento': 195000, 'jogadores': [
                        ('Rani Khedira', 'CM', 74),
                    ]},
                    'FC Augsburg': {'sigla': 'FCA', 'prestigio': 65, 'orcamento': 150000, 'jogadores': [
                        ('Alexis Claude-Maurice', 'AM', 73),
                    ]},
                }
            },
            'Primeira Liga (Portugal)': {
                'codigo': 'POR', 'clubes': {
                    'Benfica': {'sigla': 'SLB', 'prestigio': 87, 'orcamento': 500000, 'jogadores': [
                        ('Anatoliy Trubin', 'GK', 83), ('António Silva', 'CB', 82), ('Álvaro Carreras', 'LB', 82),
                        ('Kerem Aktürkoğlu', 'LW', 79), ('Vangelis Pavlidis', 'ST', 81),
                    ]},
                    'FC Porto': {'sigla': 'FCP', 'prestigio': 86, 'orcamento': 460000, 'jogadores': [
                        ('Diogo Costa', 'GK', 86), ('Pepê', 'RW', 79), ('Rodrigo Mora', 'AM', 78),
                    ]},
                    'Sporting CP': {'sigla': 'SCP', 'prestigio': 86, 'orcamento': 450000, 'jogadores': [
                        ('Geny Catamo', 'RW', 78), ('Francisco Trincão', 'LW', 80), ('Ousmane Diomandé', 'CB', 80),
                    ]},
                    'SC Braga': {'sigla': 'BRA', 'prestigio': 78, 'orcamento': 250000, 'jogadores': [
                        ('Roger Fernandes', 'ST', 76),
                    ]},
                    'Vitória de Guimarães': {'sigla': 'VSC', 'prestigio': 73, 'orcamento': 180000, 'jogadores': [
                        ('Tiago Silva', 'CB', 74),
                    ]},
                    'Gil Vicente': {'sigla': 'GIL', 'prestigio': 68, 'orcamento': 140000, 'jogadores': [
                        ('Rodrigo Pinheiro', 'ST', 73),
                    ]},
                    'Estoril Praia': {'sigla': 'EST', 'prestigio': 67, 'orcamento': 135000, 'jogadores': [
                        ('André Franco', 'AM', 72),
                    ]},
                    'Moreirense': {'sigla': 'MOR', 'prestigio': 63, 'orcamento': 110000, 'jogadores': [
                        ('Ricardo Mangas', 'LB', 71),
                    ]},
                    'FC Arouca': {'sigla': 'ARO', 'prestigio': 62, 'orcamento': 105000, 'jogadores': [
                        ('Rafael Barbosa', 'RW', 70),
                    ]},
                    'Casa Pia AC': {'sigla': 'CPA', 'prestigio': 61, 'orcamento': 100000, 'jogadores': [
                        ('Erick Pulga', 'AM', 71),
                    ]},
                    'Famalicão': {'sigla': 'FAM', 'prestigio': 63, 'orcamento': 110000, 'jogadores': [
                        ('Gonçalo Silva', 'CM', 70),
                    ]},
                    'Rio Ave': {'sigla': 'RAV', 'prestigio': 60, 'orcamento': 95000, 'jogadores': [
                        ('Anderson Silva', 'ST', 69),
                    ]},
                }
            },
            'Saudi Pro League (Arábia Saudita)': {
                'codigo': 'KSA', 'clubes': {
                    'Al-Nassr': {'sigla': 'NAS', 'prestigio': 85, 'orcamento': 900000, 'jogadores': [
                        ('Cristiano Ronaldo', 'ST', 88), ('João Félix', 'AM', 84), ('Sadio Mané', 'LW', 82),
                        ('Kingsley Coman', 'RW', 82),
                    ]},
                    'Al-Hilal': {'sigla': 'HIL', 'prestigio': 87, 'orcamento': 950000, 'jogadores': [
                        ('Bento', 'GK', 80), ('Rúben Neves', 'CM', 84),
                    ]},
                    'Al-Ittihad': {'sigla': 'ITT', 'prestigio': 84, 'orcamento': 850000, 'jogadores': [
                        ('Karim Benzema', 'ST', 85), ('Fabinho', 'DM', 81),
                    ]},
                    'Al-Ahli': {'sigla': 'AHL', 'prestigio': 83, 'orcamento': 800000, 'jogadores': [
                        ('Ivan Toney', 'ST', 83), ('Franck Kessié', 'CM', 81),
                    ]},
                    'Al-Taawoun': {'sigla': 'TAA', 'prestigio': 72, 'orcamento': 350000, 'jogadores': [
                        ('Roger Martínez', 'ST', 78),
                    ]},
                    'Al-Qadsiah': {'sigla': 'QAD', 'prestigio': 73, 'orcamento': 400000, 'jogadores': [
                        ('Julian Quiñones', 'ST', 81),
                    ]},
                    'Al-Ettifaq': {'sigla': 'ETT', 'prestigio': 74, 'orcamento': 380000, 'jogadores': [
                        ('Moussa Dembélé', 'ST', 76),
                    ]},
                    'Al-Khaleej': {'sigla': 'KHA', 'prestigio': 70, 'orcamento': 300000, 'jogadores': [
                        ('Joshua King', 'ST', 77),
                    ]},
                    'Damac': {'sigla': 'DAM', 'prestigio': 66, 'orcamento': 220000, 'jogadores': [
                        ('Fábio Martins', 'RW', 74),
                    ]},
                    'Al-Fateh': {'sigla': 'FAT', 'prestigio': 62, 'orcamento': 180000, 'jogadores': [
                        ('Sergio León', 'ST', 71),
                    ]},
                    'Al-Fayha': {'sigla': 'FAY', 'prestigio': 60, 'orcamento': 160000, 'jogadores': [
                        ('Romarinho', 'RW', 71),
                    ]},
                    'Al-Riyadh': {'sigla': 'RIY', 'prestigio': 61, 'orcamento': 170000, 'jogadores': [
                        ('Kevin', 'AM', 71),
                    ]},
                    'Al-Shabab': {'sigla': 'SHA', 'prestigio': 68, 'orcamento': 280000, 'jogadores': [
                        ('Cristian Guanca', 'RW', 72),
                    ]},
                    'Neom SC': {'sigla': 'NEO', 'prestigio': 65, 'orcamento': 250000, 'jogadores': [
                        ('Robert Firmino', 'ST', 76),
                    ]},
                }
            },
            'Ligue 1 (França)': {
                'codigo': 'FRA', 'clubes': {
                    'Paris Saint-Germain': {'sigla': 'PSG', 'prestigio': 93, 'orcamento': 1600000, 'jogadores': [
                        ('Lucas Chevalier', 'GK', 83), ('Achraf Hakimi', 'RB', 87), ('Marquinhos', 'CB', 86),
                        ('Illia Zabarnyi', 'CB', 80), ('Vitinha', 'CM', 86), ('Ousmane Dembélé', 'RW', 90),
                        ('Khvicha Kvaratskhelia', 'LW', 87), ('Bradley Barcola', 'LW', 83),
                    ]},
                    'Olympique de Marseille': {'sigla': 'OM', 'prestigio': 83, 'orcamento': 450000, 'jogadores': [
                        ('Mason Greenwood', 'RW', 83), ('Pierre-Emerick Aubameyang', 'ST', 81),
                    ]},
                    'AS Monaco': {'sigla': 'ASM', 'prestigio': 81, 'orcamento': 420000, 'jogadores': [
                        ('Folarin Balogun', 'ST', 79), ('Takumi Minamino', 'AM', 78),
                    ]},
                    'Lille': {'sigla': 'LIL', 'prestigio': 78, 'orcamento': 300000, 'jogadores': [
                        ('Edon Zhegrova', 'RW', 79),
                    ]},
                    'Olympique Lyonnais': {'sigla': 'OL', 'prestigio': 79, 'orcamento': 320000, 'jogadores': [
                        ('Alexandre Lacazette', 'ST', 80),
                    ]},
                    'OGC Nice': {'sigla': 'NIC', 'prestigio': 75, 'orcamento': 250000, 'jogadores': [
                        ('Terem Moffi', 'ST', 79),
                    ]},
                    'Stade Rennais': {'sigla': 'REN', 'prestigio': 76, 'orcamento': 270000, 'jogadores': [
                        ('Amine Gouiri', 'ST', 79),
                    ]},
                    'RC Strasbourg': {'sigla': 'STR', 'prestigio': 72, 'orcamento': 220000, 'jogadores': [
                        ('Emanuel Emegha', 'ST', 77),
                    ]},
                    'FC Nantes': {'sigla': 'NAN', 'prestigio': 68, 'orcamento': 180000, 'jogadores': [
                        ('Mostafa Mohamed', 'ST', 76),
                    ]},
                    'Stade Brestois': {'sigla': 'BRE', 'prestigio': 69, 'orcamento': 190000, 'jogadores': [
                        ('Pierre Lees-Melou', 'CM', 76),
                    ]},
                    'RC Lens': {'sigla': 'LEN', 'prestigio': 76, 'orcamento': 260000, 'jogadores': [
                        ('Neil El Aynaoui', 'CM', 76),
                    ]},
                    'Toulouse FC': {'sigla': 'TFC', 'prestigio': 70, 'orcamento': 190000, 'jogadores': [
                        ('Aron Dønnum', 'LW', 74),
                    ]},
                    'Le Havre AC': {'sigla': 'HAC', 'prestigio': 65, 'orcamento': 150000, 'jogadores': [
                        ('Josué Casimir', 'ST', 71),
                    ]},
                    'Angers SCO': {'sigla': 'ANG', 'prestigio': 64, 'orcamento': 140000, 'jogadores': [
                        ('Esteban Lepaul', 'ST', 73),
                    ]},
                    'AJ Auxerre': {'sigla': 'AUX', 'prestigio': 64, 'orcamento': 140000, 'jogadores': [
                        ('Gauthier Hein', 'RW', 72),
                    ]},
                    'FC Lorient': {'sigla': 'LOR', 'prestigio': 62, 'orcamento': 120000, 'jogadores': [
                        ('Bamba Dang', 'ST', 71),
                    ]},
                    'Paris FC': {'sigla': 'PFC', 'prestigio': 63, 'orcamento': 150000, 'jogadores': [
                        ('Kevin Trapp', 'GK', 77),
                    ]},
                    'FC Metz': {'sigla': 'MET', 'prestigio': 60, 'orcamento': 110000, 'jogadores': [
                        ('Georges Mikautadze', 'ST', 76),
                    ]},
                }
            },
            'Premier League (Inglaterra)': {
                'codigo': 'ENG', 'clubes': {
                    'Liverpool': {'sigla': 'LIV', 'prestigio': 95, 'orcamento': 1900000, 'jogadores': [
                        ('Alisson Becker', 'GK', 88), ('Virgil van Dijk', 'CB', 88), ('Ibrahima Konaté', 'CB', 84),
                        ('Jeremie Frimpong', 'RB', 82), ('Mohamed Salah', 'RW', 90), ('Florian Wirtz', 'AM', 88),
                        ('Alexander Isak', 'ST', 88), ('Hugo Ekitiké', 'ST', 83),
                    ]},
                    'Manchester City': {'sigla': 'MCI', 'prestigio': 95, 'orcamento': 1900000, 'jogadores': [
                        ('Gianluigi Donnarumma', 'GK', 88), ('Rúben Dias', 'CB', 87), ('Rodri', 'DM', 89),
                        ('Phil Foden', 'AM', 87), ('Omar Marmoush', 'RW', 82), ('Erling Haaland', 'ST', 92),
                    ]},
                    'Arsenal': {'sigla': 'ARS', 'prestigio': 92, 'orcamento': 1300000, 'jogadores': [
                        ('David Raya', 'GK', 85), ('William Saliba', 'CB', 87), ('Martín Zubimendi', 'DM', 83),
                        ('Declan Rice', 'CM', 87), ('Bukayo Saka', 'RW', 89), ('Martin Ødegaard', 'AM', 87),
                        ('Viktor Gyökeres', 'ST', 86),
                    ]},
                    'Manchester United': {'sigla': 'MUN', 'prestigio': 87, 'orcamento': 1200000, 'jogadores': [
                        ('Senne Lammens', 'GK', 78), ('Bruno Fernandes', 'AM', 87), ('Casemiro', 'DM', 81),
                        ('Bryan Mbeumo', 'RW', 84), ('Matheus Cunha', 'ST', 82), ('Benjamin Šeško', 'ST', 80),
                    ]},
                    'Chelsea': {'sigla': 'CHE', 'prestigio': 87, 'orcamento': 1100000, 'jogadores': [
                        ('Robert Sánchez', 'GK', 80), ('Moisés Caicedo', 'DM', 85), ('Enzo Fernández', 'CM', 85),
                        ('Cole Palmer', 'AM', 87), ('João Pedro', 'ST', 82),
                    ]},
                    'Newcastle United': {'sigla': 'NEW', 'prestigio': 84, 'orcamento': 750000, 'jogadores': [
                        ('Nick Pope', 'GK', 82), ('Bruno Guimarães', 'CM', 85), ('Sandro Tonali', 'CM', 83),
                        ('Anthony Gordon', 'LW', 82), ('Nick Woltemade', 'ST', 79),
                    ]},
                    'Tottenham Hotspur': {'sigla': 'TOT', 'prestigio': 83, 'orcamento': 700000, 'jogadores': [
                        ('Micky van de Ven', 'CB', 82), ('Xavi Simons', 'AM', 84), ('Dominic Solanke', 'ST', 80),
                    ]},
                    'Aston Villa': {'sigla': 'AVL', 'prestigio': 80, 'orcamento': 550000, 'jogadores': [
                        ('Morgan Rogers', 'AM', 82),
                    ]},
                    'Brighton & Hove Albion': {'sigla': 'BHA', 'prestigio': 79, 'orcamento': 480000, 'jogadores': [
                        ('Kaoru Mitoma', 'LW', 82), ('Georginio Rutter', 'AM', 81),
                    ]},
                    'Brentford': {'sigla': 'BRF', 'prestigio': 76, 'orcamento': 380000, 'jogadores': [
                        ('Jordan Henderson', 'CM', 78), ('Igor Thiago', 'ST', 79),
                    ]},
                    'Crystal Palace': {'sigla': 'CRY', 'prestigio': 77, 'orcamento': 400000, 'jogadores': [
                        ('Jean-Philippe Mateta', 'ST', 80),
                    ]},
                    'Everton': {'sigla': 'EVE', 'prestigio': 76, 'orcamento': 400000, 'jogadores': [
                        ('Iliman Ndiaye', 'AM', 80), ('Jack Grealish', 'AM', 84),
                    ]},
                    'Fulham': {'sigla': 'FUL', 'prestigio': 74, 'orcamento': 350000, 'jogadores': [
                        ('Rodrigo Muniz', 'ST', 78),
                    ]},
                    'West Ham United': {'sigla': 'WHU', 'prestigio': 76, 'orcamento': 400000, 'jogadores': [
                        ('Lucas Paquetá', 'AM', 82), ('Jarrod Bowen', 'RW', 83),
                    ]},
                    'Wolverhampton Wanderers': {'sigla': 'WOL', 'prestigio': 73, 'orcamento': 340000, 'jogadores': [
                        ('André', 'CM', 78),
                    ]},
                    'AFC Bournemouth': {'sigla': 'BOU', 'prestigio': 77, 'orcamento': 380000, 'jogadores': [
                        ('Evanilson', 'ST', 80),
                    ]},
                    'Nottingham Forest': {'sigla': 'NFO', 'prestigio': 78, 'orcamento': 420000, 'jogadores': [
                        ('Morgan Gibbs-White', 'AM', 82), ('Chris Wood', 'ST', 80),
                    ]},
                    'Sunderland': {'sigla': 'SUN', 'prestigio': 70, 'orcamento': 280000, 'jogadores': [
                        ('Wilson Isidor', 'ST', 76), ('Granit Xhaka', 'CM', 83),
                    ]},
                    'Leeds United': {'sigla': 'LEE', 'prestigio': 72, 'orcamento': 300000, 'jogadores': [
                        ('Lukas Nmecha', 'ST', 75),
                    ]},
                    'Burnley': {'sigla': 'BUR', 'prestigio': 68, 'orcamento': 260000, 'jogadores': [
                        ('Zian Flemming', 'AM', 74),
                    ]},
                }
            },
            'Eredivisie (Holanda)': {
                # NOTA: PSV e Ajax têm cobertura internacional menor sobre
                # jogadores individuais confirmados; menos nomes por clube aqui.
                'codigo': 'NED', 'clubes': {
                    'Feyenoord': {'sigla': 'FEY', 'prestigio': 78, 'orcamento': 300000, 'jogadores': [
                        ('Ayase Ueda', 'ST', 81), ('Casper Tengstedt', 'ST', 76), ('Sem Steijn', 'CM', 78),
                        ('Luciano Valente', 'AM', 77), ('Anis Hadj Moussa', 'LW', 78), ('Jordan Bos', 'LB', 76),
                        ('Anel Ahmedhodzic', 'CB', 78), ('Gernot Trauner', 'CB', 76),
                    ]},
                    'PSV Eindhoven': {'sigla': 'PSV', 'prestigio': 82, 'orcamento': 340000, 'jogadores': [
                        ('Ismael Saibari', 'AM', 79), ('Guus Til', 'CM', 78), ('Joey Veerman', 'CM', 79),
                    ]},
                    'Ajax': {'sigla': 'AJA', 'prestigio': 80, 'orcamento': 300000, 'jogadores': [
                        ('Kenneth Taylor', 'CM', 78), ('Bertrand Traoré', 'RW', 77),
                    ]},
                    'AZ Alkmaar': {'sigla': 'AZ', 'prestigio': 74, 'orcamento': 220000, 'jogadores': [
                        ('Troy Parrott', 'ST', 78),
                    ]},
                    'FC Twente': {'sigla': 'TWE', 'prestigio': 73, 'orcamento': 200000, 'jogadores': [
                        ('Sam Lammers', 'ST', 76),
                    ]},
                    'FC Utrecht': {'sigla': 'UTR', 'prestigio': 70, 'orcamento': 180000, 'jogadores': [
                        ('Isac Lidberg', 'ST', 74),
                    ]},
                    'Sparta Rotterdam': {'sigla': 'SPA', 'prestigio': 66, 'orcamento': 140000, 'jogadores': [
                        ('Mica Pinto', 'RB', 71),
                    ]},
                    'Go Ahead Eagles': {'sigla': 'GAE', 'prestigio': 64, 'orcamento': 120000, 'jogadores': [
                        ('Dean James', 'AM', 70),
                    ]},
                    'sc Heerenveen': {'sigla': 'HEE', 'prestigio': 62, 'orcamento': 110000, 'jogadores': [
                        ('Sydney van Hooijdonk', 'ST', 71),
                    ]},
                    'NEC Nijmegen': {'sigla': 'NEC', 'prestigio': 61, 'orcamento': 105000, 'jogadores': [
                        ('Elayis Tavşan', 'AM', 71),
                    ]},
                    'Fortuna Sittard': {'sigla': 'FOR', 'prestigio': 59, 'orcamento': 95000, 'jogadores': [
                        ('Jasper Dahlhaus', 'ST', 68),
                    ]},
                    'FC Groningen': {'sigla': 'GRO', 'prestigio': 60, 'orcamento': 100000, 'jogadores': [
                        ('Thomas van den Belt', 'CM', 68),
                    ]},
                }
            },
            'MLS (Estados Unidos)': {
                'codigo': 'USA', 'clubes': {
                    'Inter Miami CF': {'sigla': 'MIA', 'prestigio': 90, 'orcamento': 700000, 'jogadores': [
                        ('Lionel Messi', 'AM', 92), ('Rodrigo De Paul', 'CM', 84), ('Germán Berterame', 'ST', 78),
                        ('Sergio Reguilón', 'LB', 76), ('Tadeo Allende', 'ST', 77),
                    ]},
                    'LAFC': {'sigla': 'LAFC', 'prestigio': 84, 'orcamento': 500000, 'jogadores': [
                        ('Son Heung-min', 'ST', 85), ('Denis Bouanga', 'ST', 82), ('Stephen Eustáquio', 'CM', 78),
                        ('Aaron Long', 'CB', 74),
                    ]},
                    'Vancouver Whitecaps': {'sigla': 'VAN', 'prestigio': 78, 'orcamento': 350000, 'jogadores': [
                        ('Thomas Müller', 'AM', 82), ('Sebastian Berhalter', 'CM', 74),
                    ]},
                    'Nashville SC': {'sigla': 'NSH', 'prestigio': 74, 'orcamento': 280000, 'jogadores': [
                        ('Hany Mukhtar', 'AM', 80), ('Andy Nájar', 'RB', 74),
                    ]},
                    'Chicago Fire FC': {'sigla': 'CHI', 'prestigio': 72, 'orcamento': 260000, 'jogadores': [
                        ('Hugo Cuypers', 'ST', 78), ('Mbekezeli Mbokazi', 'CB', 73),
                    ]},
                    'Minnesota United': {'sigla': 'MIN', 'prestigio': 71, 'orcamento': 250000, 'jogadores': [
                        ('James Rodríguez', 'AM', 82),
                    ]},
                    'San Jose Earthquakes': {'sigla': 'SJ', 'prestigio': 68, 'orcamento': 220000, 'jogadores': [
                        ('Timo Werner', 'ST', 79),
                    ]},
                    'Austin FC': {'sigla': 'ATX', 'prestigio': 69, 'orcamento': 230000, 'jogadores': [
                        ('Facundo Torres', 'RW', 78),
                    ]},
                    'Seattle Sounders': {'sigla': 'SEA', 'prestigio': 76, 'orcamento': 300000, 'jogadores': [
                        ('Cristian Roldán', 'CM', 77), ('Jordan Morris', 'ST', 76),
                    ]},
                    'LA Galaxy': {'sigla': 'LAG', 'prestigio': 78, 'orcamento': 340000, 'jogadores': [
                        ('Riqui Puig', 'CM', 80), ('Gabriel Pec', 'LW', 77),
                    ]},
                    'Columbus Crew': {'sigla': 'CLB', 'prestigio': 77, 'orcamento': 320000, 'jogadores': [
                        ('Cucho Hernández', 'ST', 81),
                    ]},
                    'FC Cincinnati': {'sigla': 'CIN', 'prestigio': 75, 'orcamento': 290000, 'jogadores': [
                        ('Evander', 'AM', 82),
                    ]},
                    'Philadelphia Union': {'sigla': 'PHI', 'prestigio': 74, 'orcamento': 270000, 'jogadores': [
                        ('Cavan Sullivan', 'AM', 74),
                    ]},
                    'Real Salt Lake': {'sigla': 'RSL', 'prestigio': 70, 'orcamento': 230000, 'jogadores': [
                        ('Zavier Gozo', 'CM', 73),
                    ]},
                    'Atlanta United': {'sigla': 'ATL', 'prestigio': 76, 'orcamento': 300000, 'jogadores': [
                        ('Emmanuel Latte Lath', 'ST', 79),
                    ]},
                    'Orlando City': {'sigla': 'ORL', 'prestigio': 74, 'orcamento': 270000, 'jogadores': [
                        ('Martín Ojeda', 'AM', 77),
                    ]},
                    'New York City FC': {'sigla': 'NYC', 'prestigio': 73, 'orcamento': 260000, 'jogadores': [
                        ('Alonso Martínez', 'ST', 76),
                    ]},
                    'Charlotte FC': {'sigla': 'CLT', 'prestigio': 72, 'orcamento': 250000, 'jogadores': [
                        ('Tim Ream', 'CB', 74),
                    ]},
                    'Houston Dynamo': {'sigla': 'HOU', 'prestigio': 70, 'orcamento': 220000, 'jogadores': [
                        ('Ezequiel Ponce', 'ST', 75),
                    ]},
                    'Portland Timbers': {'sigla': 'POR', 'prestigio': 71, 'orcamento': 230000, 'jogadores': [
                        ('Felipe Mora', 'ST', 75), ('Diego Chará', 'DM', 74),
                    ]},
                }
            },
        }

        with transaction.atomic():
            user_bot, _ = User.objects.get_or_create(username='cbf_oficial', defaults={'email': 'cbf@cartolandia.com'})
            if not user_bot.password:
                user_bot.set_password('senha_segura_123')
                user_bot.save()

            clubes_criados = 0
            jogadores_criados = 0

            for nome_liga, dados_liga in ligas.items():
                codigo = dados_liga['codigo']
                Campeonato.objects.get_or_create(nome=nome_liga, temporada=config.temporada_atual, tipo='liga', divisao=codigo)

                for nome_clube, info in dados_liga['clubes'].items():
                    clube, criado = Clube.objects.get_or_create(
                        nome=nome_clube,
                        defaults={
                            'sigla': info['sigla'],
                            'divisao': codigo,
                            'orcamento': info['orcamento'],
                            'prestigio_reputacao': info['prestigio']
                        }
                    )
                    if criado:
                        clubes_criados += 1

                    for nome_jogador, posicao, ovr in info['jogadores']:
                        if posicao in ['GK', 'CB', 'DM', 'LB', 'RB']:
                            arq = 'xerife'
                        elif posicao in ['CM', 'AM']:
                            arq = 'maestro'
                        elif posicao in ['ST']:
                            arq = 'matador'
                        elif posicao in ['RW', 'LW']:
                            arq = 'motorzinho'
                        else:
                            arq = 'motorzinho'

                        if not Avatar.objects.filter(nome_camisa=nome_jogador, clube_atual=clube).exists():
                            username_jogador = f"{nome_jogador.replace(' ', '').lower()}_{info['sigla'].lower()}"
                            user_jogador, _ = User.objects.get_or_create(username=username_jogador)

                            Avatar.objects.create(
                                usuario=user_jogador,
                                nome_camisa=nome_jogador,
                                arquetipo=arq,
                                posicao_preferida=posicao,
                                clube_atual=clube,
                                temporada_nascimento=config.temporada_atual,
                                idade_inicial=random.randint(19, 37),
                                teto_potencial_oculto=ovr + random.randint(0, 4),
                                fisico=ovr - 2,
                                tecnica=ovr,
                                inteligencia=ovr + 2,
                                media_fama=ovr,
                                salario_rodada=int(ovr * 800),
                                pontos_acao_diarios=1
                            )
                            jogadores_criados += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n SUCESSO! {len(ligas)} campeonatos internacionais, {clubes_criados} clubes e {jogadores_criados} craques mundiais chegaram ao Metaverso!'
        ))
        self.stdout.write('Agora dá pra tirar o Mbappé do Real Madrid ou o Messi do Inter Miami no seu Modo Carreira!')
