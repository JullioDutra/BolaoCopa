from django.core.management.base import BaseCommand
from minijogo.models import ElencoHistorico, CartaJogador

class Command(BaseCommand):
    help = 'Popula o banco de dados com uma NOVA leva focada em zebras, piores campanhas e esquadrões históricos'

    def handle(self, *args, **kwargs):
        dados_elencos = {
            
            # ====================================================================
            # OS PIORES DOS PIORES (OVR 50 - 74) - REBAIXADOS E FOLCLÓRICOS
            # ====================================================================
            "Íbis 1980 (O Pior do Mundo)": [
                ("Jorge", "goleiro", 52), ("Toninho", "linha", 50), ("Valdir", "linha", 51),
                ("Gena", "linha", 50), ("Almir", "linha", 53), ("Cícero", "linha", 51),
                ("Batoré", "linha", 52), ("Celso", "linha", 50), ("Nado", "linha", 54),
                ("Mauro Shampoo", "linha", 58), ("Rinaldo", "linha", 51),
            ],
            "América-RN 2007 (Pior campanha BR)": [
                ("Sérgio", "goleiro", 68), ("Carlos Eduardo", "linha", 65), ("Robson", "linha", 66),
                ("Rogélio", "linha", 65), ("Ney Santos", "linha", 67), ("Marquinhos Mossoró", "linha", 68),
                ("Leandro Sena", "linha", 69), ("Reinaldo", "linha", 67), ("Souza", "linha", 71),
                ("Geovani", "linha", 66), ("Washington", "linha", 68),
            ],
            "Derby County 2008 (Pior campanha PL)": [
                ("Roy Carroll", "goleiro", 70), ("Tyrone Mears", "linha", 67), ("Claude Davis", "linha", 69),
                ("Darren Moore", "linha", 68), ("Andy Todd", "linha", 66), ("Robbie Savage", "linha", 72),
                ("Stephen Pearson", "linha", 70), ("Giles Barnes", "linha", 69), ("Eddie Lewis", "linha", 68),
                ("Kenny Miller", "linha", 71), ("Emanuel Villa", "linha", 69),
            ],
            "Chapecoense 2021 (Pior Pontuação)": [
                ("Keiller", "goleiro", 73), ("Matheus Ribeiro", "linha", 68), ("Ignácio", "linha", 69),
                ("Joílson", "linha", 68), ("Busanello", "linha", 70), ("Moisés Ribeiro", "linha", 67),
                ("Anderson Leite", "linha", 69), ("Denner", "linha", 68), ("Mike", "linha", 69),
                ("Bruno Silva", "linha", 71), ("Anselmo Ramon", "linha", 72),
            ],
            "Corinthians 2007 (Rebaixado)": [
                ("Felipe", "goleiro", 77), ("Iran", "linha", 68), ("Fábio Ferreira", "linha", 67),
                ("Betão", "linha", 71), ("Everton", "linha", 68), ("Bruno Octávio", "linha", 69),
                ("Moradei", "linha", 68), ("Vampeta", "linha", 72), ("Carlos Alberto", "linha", 73),
                ("Dentinho", "linha", 74), ("Finazzi", "linha", 73),
            ],
            "Palmeiras 2012 (Rebaixado)": [
                ("Bruno", "goleiro", 70), ("Artur", "linha", 68), ("Maurício Ramos", "linha", 71),
                ("Thiago Heleno", "linha", 70), ("Juninho", "linha", 71), ("Henrique", "linha", 74),
                ("Marcos Assunção", "linha", 78), ("Valdivia", "linha", 79), ("Mazinho", "linha", 69),
                ("Luan", "linha", 70), ("Barcos", "linha", 81),
            ],
            "Vasco da Gama 2015 (Rebaixado)": [
                ("Martin Silva", "goleiro", 79), ("Madson", "linha", 71), ("Luan", "linha", 74),
                ("Rodrigo", "linha", 73), ("Julio Cesar", "linha", 71), ("Guiñazú", "linha", 73),
                ("Serginho", "linha", 69), ("Andrezinho", "linha", 74), ("Nenê", "linha", 78),
                ("Jorge Henrique", "linha", 72), ("Leandrão", "linha", 68),
            ],
            "Cruzeiro 2019 (Rebaixado)": [
                ("Fábio", "goleiro", 81), ("Edílson", "linha", 72), ("Dedé", "linha", 76),
                ("Leo", "linha", 74), ("Egídio", "linha", 71), ("Henrique", "linha", 73),
                ("Ariel Cabral", "linha", 71), ("Thiago Neves", "linha", 74), ("Robinho", "linha", 73),
                ("Marquinhos Gabriel", "linha", 72), ("Fred", "linha", 74),
            ],
            "Paraná Clube 2018 (Rebaixado)": [
                ("Richard", "goleiro", 72), ("Júnior", "linha", 67), ("Jesiel", "linha", 68),
                ("René Santos", "linha", 66), ("Igor", "linha", 67), ("Leandro Vilela", "linha", 68),
                ("Alex Santana", "linha", 71), ("Nadson", "linha", 69), ("Silvinho", "linha", 68),
                ("Carlos", "linha", 67), ("Rafael Grampola", "linha", 68),
            ],
            "Náutico 2013 (Rebaixado)": [
                ("Ricardo Berna", "goleiro", 71), ("Auremir", "linha", 68), ("Jean Rolt", "linha", 67),
                ("Leandro Amaro", "linha", 68), ("Bruno Collaço", "linha", 69), ("Elicarlos", "linha", 70),
                ("Derley", "linha", 71), ("Martinez", "linha", 72), ("Tiago Real", "linha", 69),
                ("Maikon Leite", "linha", 72), ("Olivera", "linha", 70),
            ],
            "Botafogo 2020 (Rebaixado)": [
                ("Gatito Fernández", "goleiro", 78), ("Kevin", "linha", 68), ("Marcelo Benevenuto", "linha", 72),
                ("Kanu", "linha", 73), ("Victor Luis", "linha", 72), ("Caio Alexandre", "linha", 74),
                ("Honda", "linha", 75), ("Bruno Nazário", "linha", 71), ("Rhuan", "linha", 67),
                ("Kalou", "linha", 73), ("Pedro Raul", "linha", 73),
            ],

            # ====================================================================
            # TIMES MÉDIOS, SURPRESAS E HERÓIS (OVR 75 - 84)
            # ====================================================================
            "Paulista de Jundiaí 2005 (Copa do Brasil)": [
                ("Rafael Bracali", "goleiro", 79), ("Lucas", "linha", 76), ("Anderson", "linha", 75),
                ("Dema", "linha", 75), ("Julinho", "linha", 76), ("Amaral", "linha", 78),
                ("Fábio Gomes", "linha", 76), ("Cristian", "linha", 79), ("Mossoró", "linha", 81),
                ("Márcio Richardes", "linha", 77), ("Léo", "linha", 76),
            ],
            "Santo André 2004 (Copa do Brasil)": [
                ("Júlio César", "goleiro", 78), ("Dedimar", "linha", 75), ("Alex", "linha", 75),
                ("Gabriel", "linha", 76), ("Da Guia", "linha", 75), ("Dirceu", "linha", 76),
                ("Ramalho", "linha", 77), ("Élvis", "linha", 78), ("Romerito", "linha", 79),
                ("Sandro Gaúcho", "linha", 80), ("Makanaki", "linha", 78),
            ],
            "Sport Recife 2008 (Copa do Brasil)": [
                ("Magrão", "goleiro", 82), ("Luisinho Neto", "linha", 76), ("Igor", "linha", 77),
                ("Durval", "linha", 80), ("Dutra", "linha", 78), ("Daniel Paulista", "linha", 77),
                ("Sandro Goiano", "linha", 78), ("Romerito", "linha", 79), ("Carlinhos Bala", "linha", 81),
                ("Leandro Machado", "linha", 78), ("Enílton", "linha", 77),
            ],
            "Juventude 1999 (Copa do Brasil)": [
                ("Emerson", "goleiro", 78), ("Marcos Teixeira", "linha", 75), ("Picoli", "linha", 76),
                ("Capone", "linha", 77), ("Edson", "linha", 75), ("Roberto", "linha", 76),
                ("Lauro", "linha", 77), ("Flávio", "linha", 78), ("Mabília", "linha", 77),
                ("Maurício", "linha", 77), ("Christian", "linha", 80),
            ],
            "São Caetano 2002 (Vice Libertadores)": [
                ("Silvio Luiz", "goleiro", 82), ("Russo", "linha", 78), ("Daniel", "linha", 79),
                ("Dininho", "linha", 81), ("Rubens Cardoso", "linha", 78), ("Marcos Senna", "linha", 83),
                ("Adãozinho", "linha", 79), ("Anaílson", "linha", 80), ("Ailton", "linha", 78),
                ("Somália", "linha", 81), ("Magrão", "linha", 82),
            ],
            "Criciúma 1991 (Copa do Brasil)": [
                ("Alexandre", "goleiro", 78), ("Sarandi", "linha", 75), ("Vilmar", "linha", 76),
                ("Altair", "linha", 75), ("Itá", "linha", 77), ("Roberto Cavalo", "linha", 78),
                ("Grizzo", "linha", 77), ("Zé Roberto", "linha", 76), ("Jairo Lenzi", "linha", 79),
                ("Gelson", "linha", 77), ("Soares", "linha", 78),
            ],
            "Portuguesa 2011 (A Barcelusa)": [
                ("Weverton", "goleiro", 82), ("Luis Ricardo", "linha", 78), ("Rogério", "linha", 77),
                ("Renato", "linha", 77), ("Marcelo Cordeiro", "linha", 79), ("Boquita", "linha", 76),
                ("Guilherme", "linha", 78), ("Marco Antônio", "linha", 80), ("Ananias", "linha", 79),
                ("Edno", "linha", 81), ("Henrique", "linha", 78),
            ],
            "Fortaleza 2023 (Vice Sul-Americana)": [
                ("João Ricardo", "goleiro", 81), ("Tinga", "linha", 80), ("Brítez", "linha", 79),
                ("Titi", "linha", 79), ("Bruno Pacheco", "linha", 80), ("Zé Welison", "linha", 79),
                ("Caio Alexandre", "linha", 81), ("Pochettino", "linha", 80), ("Yago Pikachu", "linha", 82),
                ("Guilherme", "linha", 80), ("Lucero", "linha", 82),
            ],
            "Goiás 2005 (Libertadores)": [
                ("Harlei", "goleiro", 83), ("Paulo Baier", "linha", 84), ("André Leone", "linha", 78),
                ("Júlio Santos", "linha", 77), ("Jadílson", "linha", 80), ("Cléber Gaúcho", "linha", 79),
                ("Rodrigo Tabata", "linha", 81), ("Danilo Portugal", "linha", 78), ("Roni", "linha", 81),
                ("Souza", "linha", 82), ("Jorge Mutamba", "linha", 77),
            ],
            "Guarani 1978 (Brasileirão)": [
                ("Neneca", "goleiro", 82), ("Mauro", "linha", 78), ("Gomes", "linha", 79),
                ("Edson", "linha", 78), ("Miranda", "linha", 78), ("Zé Carlos", "linha", 80),
                ("Renato", "linha", 81), ("Zenon", "linha", 84), ("Capitão", "linha", 80),
                ("Careca", "linha", 85), ("Bozó", "linha", 80),
            ],
            "Paysandu 2002 (Copa dos Campeões)": [
                ("Marcão", "goleiro", 78), ("Marcos", "linha", 76), ("Gino", "linha", 77),
                ("Sérgio", "linha", 75), ("Luís Fernando", "linha", 76), ("Sandro", "linha", 78),
                ("Vandick", "linha", 77), ("Vélber", "linha", 79), ("Jóbson", "linha", 81),
                ("Iarley", "linha", 83), ("Vanderson", "linha", 80),
            ],
            "Chapecoense 2016 (Eternos)": [
                ("Danilo", "goleiro", 83), ("Gimenez", "linha", 78), ("Thiego", "linha", 80),
                ("Neto", "linha", 79), ("Dener", "linha", 78), ("Josimar", "linha", 77),
                ("Cleber Santana", "linha", 81), ("Gil", "linha", 78), ("Ananias", "linha", 81),
                ("Tiaguinho", "linha", 79), ("Bruno Rangel", "linha", 82),
            ],
            "Leicester City 2016 (O Milagre)": [
                ("Schmeichel", "goleiro", 85), ("Simpson", "linha", 80), ("Wes Morgan", "linha", 83),
                ("Huth", "linha", 82), ("Fuchs", "linha", 81), ("Kanté", "linha", 88),
                ("Drinkwater", "linha", 82), ("Albrighton", "linha", 81), ("Mahrez", "linha", 87),
                ("Vardy", "linha", 88), ("Okazaki", "linha", 83),
            ],

            # ====================================================================
            # OS BONS E LENDÁRIOS (OVR 84 - 95)
            # ====================================================================
            "São Paulo 1992 (Mundial)": [
                ("Zetti", "goleiro", 89), ("Cafu", "linha", 90), ("Antônio Carlos", "linha", 87),
                ("Ronaldão", "linha", 86), ("Ronaldo Luís", "linha", 85), ("Pintado", "linha", 85),
                ("Toninho Cerezo", "linha", 88), ("Raí", "linha", 92), ("Palhinha", "linha", 87),
                ("Müller", "linha", 89), ("Elivélton", "linha", 86),
            ],
            "Fluminense 2012 (Brasileirão)": [
                ("Diego Cavalieri", "goleiro", 86), ("Bruno", "linha", 81), ("Gum", "linha", 82),
                ("Leandro Euzébio", "linha", 81), ("Carlinhos", "linha", 83), ("Edinho", "linha", 81),
                ("Jean", "linha", 84), ("Deco", "linha", 88), ("Thiago Neves", "linha", 87),
                ("Wellington Nem", "linha", 85), ("Fred", "linha", 89),
            ],
            "Botafogo 1995 (Brasileirão)": [
                ("Wagner", "goleiro", 85), ("Wilson Goiano", "linha", 82), ("Wilson Gottardo", "linha", 85),
                ("Gonçalves", "linha", 84), ("André Silva", "linha", 81), ("Jamir", "linha", 82),
                ("Leandro Ávila", "linha", 83), ("Beto", "linha", 84), ("Sérgio Manoel", "linha", 85),
                ("Donizete", "linha", 87), ("Túlio Maravilha", "linha", 89),
            ],
            "Vasco da Gama 2000 (Mercosul)": [
                ("Helton", "goleiro", 86), ("Clébson", "linha", 82), ("Odvan", "linha", 84),
                ("Mauro Galvão", "linha", 87), ("Jorginho Paulista", "linha", 83), ("Paulo Miranda", "linha", 83),
                ("Nasa", "linha", 82), ("Juninho Paulista", "linha", 89), ("Juninho Pernambucano", "linha", 90),
                ("Euller", "linha", 87), ("Romário", "linha", 93),
            ],
            "Santos 2002 (Brasileirão)": [
                ("Fábio Costa", "goleiro", 84), ("Maurinho", "linha", 82), ("Alex", "linha", 86),
                ("Preto", "linha", 80), ("Léo", "linha", 85), ("Paulo Almeida", "linha", 82),
                ("Renato", "linha", 86), ("Elano", "linha", 85), ("Diego", "linha", 88),
                ("Robinho", "linha", 89), ("Alberto", "linha", 82),
            ],
            "Corinthians 1999 (Brasileirão)": [
                ("Dida", "goleiro", 90), ("Índio", "linha", 82), ("João Carlos", "linha", 84),
                ("Márcio Costa", "linha", 83), ("Kléber", "linha", 85), ("Vampeta", "linha", 87),
                ("Rincón", "linha", 88), ("Ricardinho", "linha", 87), ("Marcelinho Carioca", "linha", 90),
                ("Edílson", "linha", 89), ("Luizão", "linha", 88),
            ],
            "Cruzeiro 2013 (Brasileirão)": [
                ("Fábio", "goleiro", 88), ("Ceará", "linha", 82), ("Dedé", "linha", 87),
                ("Bruno Rodrigo", "linha", 83), ("Egídio", "linha", 82), ("Nilton", "linha", 84),
                ("Lucas Silva", "linha", 83), ("Éverton Ribeiro", "linha", 89), ("Ricardo Goulart", "linha", 87),
                ("Willian", "linha", 84), ("Borges", "linha", 85),
            ],
            "Palmeiras 2020 (Libertadores)": [
                ("Weverton", "goleiro", 88), ("Marcos Rocha", "linha", 83), ("Luan", "linha", 82),
                ("Gustavo Gómez", "linha", 87), ("Viña", "linha", 83), ("Danilo", "linha", 83),
                ("Zé Rafael", "linha", 83), ("Raphael Veiga", "linha", 86), ("Gabriel Menino", "linha", 82),
                ("Rony", "linha", 84), ("Luiz Adriano", "linha", 84),
            ],
            "Athletico Paranaense 2001 (BR)": [
                ("Flávio", "goleiro", 85), ("Alessandro", "linha", 82), ("Gustavo", "linha", 83),
                ("Nem", "linha", 84), ("Rogério Corrêa", "linha", 82), ("Fabiano", "linha", 81),
                ("Cocito", "linha", 80), ("Kleberson", "linha", 87), ("Souza", "linha", 83),
                ("Alex Mineiro", "linha", 88), ("Kléber", "linha", 85),
            ],
            "Flamengo 1981 (Mundial)": [
                ("Raul", "goleiro", 87), ("Leandro", "linha", 91), ("Marinho", "linha", 86),
                ("Mozer", "linha", 87), ("Júnior", "linha", 92), ("Andrade", "linha", 88),
                ("Adílio", "linha", 87), ("Zico", "linha", 95), ("Tita", "linha", 86),
                ("Nunes", "linha", 87), ("Lico", "linha", 85),
            ],
            "Atlético Mineiro 2021 (Brasileirão)": [
                ("Everson", "goleiro", 84), ("Mariano", "linha", 82), ("Nathan Silva", "linha", 83),
                ("Junior Alonso", "linha", 84), ("Guilherme Arana", "linha", 86), ("Allan", "linha", 83),
                ("Jair", "linha", 82), ("Zaracho", "linha", 84), ("Nacho Fernández", "linha", 85),
                ("Keno", "linha", 83), ("Hulk", "linha", 89),
            ],
            "River Plate 2018 (Libertadores)": [
                ("Armani", "goleiro", 84), ("Montiel", "linha", 83), ("Maidana", "linha", 82),
                ("Pinola", "linha", 82), ("Casco", "linha", 81), ("Enzo Pérez", "linha", 84),
                ("Ponzio", "linha", 83), ("Palacios", "linha", 83), ("Pity Martínez", "linha", 86),
                ("Pratto", "linha", 84), ("Borré", "linha", 83),
            ],
            "Espanha 2010 (Copa do Mundo)": [
                ("Casillas", "goleiro", 92), ("Sergio Ramos", "linha", 89), ("Puyol", "linha", 91),
                ("Piqué", "linha", 88), ("Capdevila", "linha", 85), ("Busquets", "linha", 87),
                ("Xabi Alonso", "linha", 89), ("Xavi", "linha", 92), ("Iniesta", "linha", 93),
                ("Pedro", "linha", 87), ("David Villa", "linha", 89),
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
