from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Povoa o banco de dados centralizado de Clubes, Jogadores e Desafios (MEGA LOTE COMPLETO 1 ao 6)'

    def handle(self, *args, **kwargs):
        # ==========================================
        # TODOS OS ELENCOS (LOTES 1 ao 6)
        # ==========================================
        elencos = [
            # --- LOTE 1 ---
            {
                "titulo": "Palmeiras 1999 (Libertadores)",
                "jogadores": [
                    {"nome": "Marcos", "posicao": "Goleiro"}, {"nome": "Arce", "posicao": "Lateral Direito"},
                    {"nome": "Júnior Baiano", "posicao": "Zagueiro"}, {"nome": "Roque Júnior", "posicao": "Zagueiro"},
                    {"nome": "Júnior", "posicao": "Lateral Esquerdo"}, {"nome": "César Sampaio", "posicao": "Volante"},
                    {"nome": "Rogério", "posicao": "Volante"}, {"nome": "Zinho", "posicao": "Meia"},
                    {"nome": "Alex", "posicao": "Meia-Atacante"}, {"nome": "Paulo Nunes", "posicao": "Atacante"},
                    {"nome": "Oséas", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Vasco 2000 (Mercosul)",
                "jogadores": [
                    {"nome": "Hélton", "posicao": "Goleiro"}, {"nome": "Clébson", "posicao": "Lateral Direito"},
                    {"nome": "Odvan", "posicao": "Zagueiro"}, {"nome": "Júnior Baiano", "posicao": "Zagueiro"},
                    {"nome": "Jorginho Paulista", "posicao": "Lateral Esquerdo"}, {"nome": "Jorginho", "posicao": "Volante"},
                    {"nome": "Juninho Pernambucano", "posicao": "Meia"}, {"nome": "Juninho Paulista", "posicao": "Meia-Atacante"},
                    {"nome": "Euller", "posicao": "Atacante"}, {"nome": "Romário", "posicao": "Centroavante"},
                    {"nome": "Edmundo", "posicao": "Atacante"},
                ]
            },
            {
                "titulo": "Cruzeiro 2003 (Tríplice Coroa)",
                "jogadores": [
                    {"nome": "Gomes", "posicao": "Goleiro"}, {"nome": "Maurinho", "posicao": "Lateral Direito"},
                    {"nome": "Cris", "posicao": "Zagueiro"}, {"nome": "Edu Dracena", "posicao": "Zagueiro"},
                    {"nome": "Leandro", "posicao": "Lateral Esquerdo"}, {"nome": "Augusto Recife", "posicao": "Volante"},
                    {"nome": "Maldonado", "posicao": "Volante"}, {"nome": "Wendell", "posicao": "Meia"},
                    {"nome": "Alex", "posicao": "Meia-Atacante"}, {"nome": "Aristizábal", "posicao": "Atacante"},
                    {"nome": "Deivid", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "São Paulo 1992 (Mundial)",
                "jogadores": [
                    {"nome": "Zetti", "posicao": "Goleiro"}, {"nome": "Cafu", "posicao": "Lateral Direito"},
                    {"nome": "Antônio Carlos", "posicao": "Zagueiro"}, {"nome": "Ronaldão", "posicao": "Zagueiro"},
                    {"nome": "Ronaldo Luís", "posicao": "Lateral Esquerdo"}, {"nome": "Pintado", "posicao": "Volante"},
                    {"nome": "Toninho Cerezo", "posicao": "Volante"}, {"nome": "Raí", "posicao": "Meia-Atacante"},
                    {"nome": "Müller", "posicao": "Atacante"}, {"nome": "Palhinha", "posicao": "Segundo Atacante"},
                    {"nome": "Macedo", "posicao": "Atacante"},
                ]
            },
            {
                "titulo": "Santos 2011 (Libertadores)",
                "jogadores": [
                    {"nome": "Rafael Cabral", "posicao": "Goleiro"}, {"nome": "Danilo", "posicao": "Lateral Direito"},
                    {"nome": "Edu Dracena", "posicao": "Zagueiro"}, {"nome": "Durval", "posicao": "Zagueiro"},
                    {"nome": "Léo", "posicao": "Lateral Esquerdo"}, {"nome": "Arouca", "posicao": "Volante"},
                    {"nome": "Adriano", "posicao": "Volante"}, {"nome": "Elano", "posicao": "Meia"},
                    {"nome": "Ganso", "posicao": "Meia-Atacante"}, {"nome": "Neymar", "posicao": "Ponta Esquerda"},
                    {"nome": "Borges", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Milan 2005 (A Lenda Europeia)",
                "jogadores": [
                    {"nome": "Dida", "posicao": "Goleiro"}, {"nome": "Cafu", "posicao": "Lateral Direito"},
                    {"nome": "Stam", "posicao": "Zagueiro"}, {"nome": "Nesta", "posicao": "Zagueiro"},
                    {"nome": "Maldini", "posicao": "Lateral Esquerdo"}, {"nome": "Pirlo", "posicao": "Volante"},
                    {"nome": "Gattuso", "posicao": "Meia Central"}, {"nome": "Seedorf", "posicao": "Meia Esquerda"},
                    {"nome": "Kaká", "posicao": "Meia-Atacante"}, {"nome": "Shevchenko", "posicao": "Atacante"},
                    {"nome": "Crespo", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Internazionale 2010 (Tríplice Coroa)",
                "jogadores": [
                    {"nome": "Júlio César", "posicao": "Goleiro"}, {"nome": "Maicon", "posicao": "Lateral Direito"},
                    {"nome": "Lúcio", "posicao": "Zagueiro"}, {"nome": "Samuel", "posicao": "Zagueiro"},
                    {"nome": "Zanetti", "posicao": "Lateral Esquerdo"}, {"nome": "Cambiasso", "posicao": "Volante"},
                    {"nome": "Thiago Motta", "posicao": "Meia Central"}, {"nome": "Sneijder", "posicao": "Meia-Atacante"},
                    {"nome": "Eto'o", "posicao": "Ponta Direita"}, {"nome": "Pandev", "posicao": "Ponta Esquerda"},
                    {"nome": "Milito", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Itália 2006 (Copa do Mundo)",
                "jogadores": [
                    {"nome": "Buffon", "posicao": "Goleiro"}, {"nome": "Zambrotta", "posicao": "Lateral Direito"},
                    {"nome": "Cannavaro", "posicao": "Zagueiro"}, {"nome": "Materazzi", "posicao": "Zagueiro"},
                    {"nome": "Grosso", "posicao": "Lateral Esquerdo"}, {"nome": "Gattuso", "posicao": "Volante"},
                    {"nome": "Pirlo", "posicao": "Volante"}, {"nome": "Camoranesi", "posicao": "Meia Direita"},
                    {"nome": "Perrotta", "posicao": "Meia Esquerda"}, {"nome": "Totti", "posicao": "Meia-Atacante"},
                    {"nome": "Luca Toni", "posicao": "Centroavante"},
                ]
            },
            
            # --- LOTE 2 ---
            {
                "titulo": "Real Madrid 2002/03 (Os Galácticos)",
                "jogadores": [
                    {"nome": "Casillas", "posicao": "Goleiro"}, {"nome": "Michel Salgado", "posicao": "Lateral Direito"},
                    {"nome": "Fernando Hierro", "posicao": "Zagueiro"}, {"nome": "Iván Helguera", "posicao": "Zagueiro"},
                    {"nome": "Roberto Carlos", "posicao": "Lateral Esquerdo"}, {"nome": "Claude Makélélé", "posicao": "Volante"},
                    {"nome": "Luís Figo", "posicao": "Meia Direita"}, {"nome": "Zinedine Zidane", "posicao": "Meia Central"},
                    {"nome": "Guti", "posicao": "Meia Esquerda"}, {"nome": "Raúl", "posicao": "Segundo Atacante"},
                    {"nome": "Ronaldo", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Fluminense 2012 (Tetra Brasileiro)",
                "jogadores": [
                    {"nome": "Diego Cavalieri", "posicao": "Goleiro"}, {"nome": "Bruno", "posicao": "Lateral Direito"},
                    {"nome": "Gum", "posicao": "Zagueiro"}, {"nome": "Leandro Euzébio", "posicao": "Zagueiro"},
                    {"nome": "Carlinhos", "posicao": "Lateral Esquerdo"}, {"nome": "Edinho", "posicao": "Volante"},
                    {"nome": "Jean", "posicao": "Volante"}, {"nome": "Deco", "posicao": "Meia"},
                    {"nome": "Thiago Neves", "posicao": "Meia-Atacante"}, {"nome": "Wellington Nem", "posicao": "Atacante"},
                    {"nome": "Fred", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Grêmio 2017 (Tri da Libertadores)",
                "jogadores": [
                    {"nome": "Marcelo Grohe", "posicao": "Goleiro"}, {"nome": "Edílson", "posicao": "Lateral Direito"},
                    {"nome": "Pedro Geromel", "posicao": "Zagueiro"}, {"nome": "Walter Kannemann", "posicao": "Zagueiro"},
                    {"nome": "Bruno Cortez", "posicao": "Lateral Esquerdo"}, {"nome": "Michel", "posicao": "Volante"},
                    {"nome": "Arthur", "posicao": "Volante"}, {"nome": "Ramiro", "posicao": "Meia Direita"},
                    {"nome": "Luan", "posicao": "Meia-Atacante"}, {"nome": "Fernandinho", "posicao": "Ponta Esquerda"},
                    {"nome": "Lucas Barrios", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Boca Juniors 2007 (Libertadores)",
                "jogadores": [
                    {"nome": "Mauricio Caranta", "posicao": "Goleiro"}, {"nome": "Hugo Ibarra", "posicao": "Lateral Direito"},
                    {"nome": "Cata Díaz", "posicao": "Zagueiro"}, {"nome": "Claudio Morel", "posicao": "Zagueiro"},
                    {"nome": "Clemente Rodríguez", "posicao": "Lateral Esquerdo"}, {"nome": "Pablo Ledesma", "posicao": "Volante"},
                    {"nome": "Éver Banega", "posicao": "Volante"}, {"nome": "Neri Cardozo", "posicao": "Meia"},
                    {"nome": "Juan Román Riquelme", "posicao": "Meia-Atacante"}, {"nome": "Rodrigo Palacio", "posicao": "Atacante"},
                    {"nome": "Martín Palermo", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Flamengo 2019 (A Máquina de Jesus)",
                "jogadores": [
                    {"nome": "Diego Alves", "posicao": "Goleiro"}, {"nome": "Rafinha", "posicao": "Lateral Direito"},
                    {"nome": "Rodrigo Caio", "posicao": "Zagueiro"}, {"nome": "Pablo Marí", "posicao": "Zagueiro"},
                    {"nome": "Filipe Luís", "posicao": "Lateral Esquerdo"}, {"nome": "Willian Arão", "posicao": "Volante"},
                    {"nome": "Gerson", "posicao": "Meia"}, {"nome": "Éverton Ribeiro", "posicao": "Meia Direita"},
                    {"nome": "De Arrascaeta", "posicao": "Meia Esquerda"}, {"nome": "Bruno Henrique", "posicao": "Atacante"},
                    {"nome": "Gabriel Barbosa", "posicao": "Centroavante"},
                ]
            },

            # --- LOTE 3 ---
            {
                "titulo": "Chelsea 2012 (Milagre de Munique)",
                "jogadores": [
                    {"nome": "Petr Cech", "posicao": "Goleiro"}, {"nome": "Bosingwa", "posicao": "Lateral Direito"},
                    {"nome": "David Luiz", "posicao": "Zagueiro"}, {"nome": "Gary Cahill", "posicao": "Zagueiro"},
                    {"nome": "Ashley Cole", "posicao": "Lateral Esquerdo"}, {"nome": "Mikel", "posicao": "Volante"},
                    {"nome": "Frank Lampard", "posicao": "Meia Central"}, {"nome": "Salomon Kalou", "posicao": "Ponta Direita"},
                    {"nome": "Juan Mata", "posicao": "Meia-Atacante"}, {"nome": "Ryan Bertrand", "posicao": "Ponta Esquerda"},
                    {"nome": "Didier Drogba", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Bayern de Munique 2013 (Tríplice Coroa)",
                "jogadores": [
                    {"nome": "Manuel Neuer", "posicao": "Goleiro"}, {"nome": "Philipp Lahm", "posicao": "Lateral Direito"},
                    {"nome": "Jerome Boateng", "posicao": "Zagueiro"}, {"nome": "Dante", "posicao": "Zagueiro"},
                    {"nome": "David Alaba", "posicao": "Lateral Esquerdo"}, {"nome": "Javi Martínez", "posicao": "Volante"},
                    {"nome": "Schweinsteiger", "posicao": "Meia Central"}, {"nome": "Arjen Robben", "posicao": "Ponta Direita"},
                    {"nome": "Thomas Müller", "posicao": "Meia-Atacante"}, {"nome": "Franck Ribéry", "posicao": "Ponta Esquerda"},
                    {"nome": "Mario Mandzukic", "posicao": "Centroavante"},
                ]
            },

            # --- LOTE 4 ---
            {
                "titulo": "São Paulo 2005 (Mundial de Clubes)",
                "jogadores": [
                    {"nome": "Rogério Ceni", "posicao": "Goleiro"}, {"nome": "Cicinho", "posicao": "Ala Direito"},
                    {"nome": "Fabão", "posicao": "Zagueiro"}, {"nome": "Lugano", "posicao": "Zagueiro"},
                    {"nome": "Edcarlos", "posicao": "Zagueiro"}, {"nome": "Júnior", "posicao": "Ala Esquerdo"},
                    {"nome": "Mineiro", "posicao": "Volante"}, {"nome": "Josué", "posicao": "Volante"},
                    {"nome": "Danilo", "posicao": "Meia-Atacante"}, {"nome": "Amoroso", "posicao": "Atacante"},
                    {"nome": "Aloísio", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Corinthians 2012 (Mundial de Clubes)",
                "jogadores": [
                    {"nome": "Cássio", "posicao": "Goleiro"}, {"nome": "Alessandro", "posicao": "Lateral Direito"},
                    {"nome": "Chicão", "posicao": "Zagueiro"}, {"nome": "Paulo André", "posicao": "Zagueiro"},
                    {"nome": "Fábio Santos", "posicao": "Lateral Esquerdo"}, {"nome": "Ralf", "posicao": "Volante"},
                    {"nome": "Paulinho", "posicao": "Volante"}, {"nome": "Danilo", "posicao": "Meia"},
                    {"nome": "Jorge Henrique", "posicao": "Ponta Direita"}, {"nome": "Emerson Sheik", "posicao": "Ponta Esquerda"},
                    {"nome": "Paolo Guerrero", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Barcelona 2014/15 (O Trio MSN)",
                "jogadores": [
                    {"nome": "Ter Stegen", "posicao": "Goleiro"}, {"nome": "Daniel Alves", "posicao": "Lateral Direito"},
                    {"nome": "Piqué", "posicao": "Zagueiro"}, {"nome": "Mascherano", "posicao": "Zagueiro"},
                    {"nome": "Jordi Alba", "posicao": "Lateral Esquerdo"}, {"nome": "Busquets", "posicao": "Volante"},
                    {"nome": "Rakitic", "posicao": "Meia Central"}, {"nome": "Iniesta", "posicao": "Meia Central"},
                    {"nome": "Messi", "posicao": "Ponta Direita"}, {"nome": "Neymar", "posicao": "Ponta Esquerda"},
                    {"nome": "Luis Suárez", "posicao": "Centroavante"}
                ]
            },

            # --- LOTE 5 ---
            {
                "titulo": "Corinthians 2000 (Mundial de Clubes)",
                "jogadores": [
                    {"nome": "Dida", "posicao": "Goleiro"}, {"nome": "Índio", "posicao": "Lateral Direito"},
                    {"nome": "Adilson", "posicao": "Zagueiro"}, {"nome": "Fábio Luciano", "posicao": "Zagueiro"},
                    {"nome": "Kléber", "posicao": "Lateral Esquerdo"}, {"nome": "Vampeta", "posicao": "Volante"},
                    {"nome": "Freddy Rincón", "posicao": "Volante"}, {"nome": "Marcelinho Carioca", "posicao": "Meia Direita"},
                    {"nome": "Ricardinho", "posicao": "Meia Esquerda"}, {"nome": "Edílson", "posicao": "Atacante"},
                    {"nome": "Luizão", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Internacional 2006 (Mundial de Clubes)",
                "jogadores": [
                    {"nome": "Clemer", "posicao": "Goleiro"}, {"nome": "Ceará", "posicao": "Lateral Direito"},
                    {"nome": "Índio", "posicao": "Zagueiro"}, {"nome": "Fabiano Eller", "posicao": "Zagueiro"},
                    {"nome": "Rubens Cardoso", "posicao": "Lateral Esquerdo"}, {"nome": "Edinho", "posicao": "Volante"},
                    {"nome": "Wellington Monteiro", "posicao": "Volante"}, {"nome": "Alex", "posicao": "Meia"},
                    {"nome": "Fernandão", "posicao": "Meia-Atacante"}, {"nome": "Iarley", "posicao": "Segundo Atacante"},
                    {"nome": "Alexandre Pato", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Santos 2002 (Meninos da Vila)",
                "jogadores": [
                    {"nome": "Fábio Costa", "posicao": "Goleiro"}, {"nome": "Maurinho", "posicao": "Lateral Direito"},
                    {"nome": "Alex", "posicao": "Zagueiro"}, {"nome": "André Luís", "posicao": "Zagueiro"},
                    {"nome": "Léo", "posicao": "Lateral Esquerdo"}, {"nome": "Paulo Almeida", "posicao": "Volante"},
                    {"nome": "Renato", "posicao": "Volante"}, {"nome": "Elano", "posicao": "Meia"},
                    {"nome": "Diego", "posicao": "Meia-Atacante"}, {"nome": "Robinho", "posicao": "Atacante"},
                    {"nome": "Alberto", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "São Caetano 2002 (Vice da Libertadores)",
                "jogadores": [
                    {"nome": "Silvio Luiz", "posicao": "Goleiro"}, {"nome": "Russo", "posicao": "Lateral Direito"},
                    {"nome": "Dininho", "posicao": "Zagueiro"}, {"nome": "Daniel", "posicao": "Zagueiro"},
                    {"nome": "Rubens Cardoso", "posicao": "Lateral Esquerdo"}, {"nome": "Marcos Senna", "posicao": "Volante"},
                    {"nome": "Adãozinho", "posicao": "Volante"}, {"nome": "Ailton", "posicao": "Meia"},
                    {"nome": "Anaílson", "posicao": "Meia-Atacante"}, {"nome": "Somália", "posicao": "Atacante"},
                    {"nome": "Brandão", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Espanha 2010 (Campeã do Mundo)",
                "jogadores": [
                    {"nome": "Casillas", "posicao": "Goleiro"}, {"nome": "Sergio Ramos", "posicao": "Lateral Direito"},
                    {"nome": "Piqué", "posicao": "Zagueiro"}, {"nome": "Puyol", "posicao": "Zagueiro"},
                    {"nome": "Capdevila", "posicao": "Lateral Esquerdo"}, {"nome": "Busquets", "posicao": "Volante"},
                    {"nome": "Xabi Alonso", "posicao": "Volante"}, {"nome": "Xavi", "posicao": "Meia Central"},
                    {"nome": "Iniesta", "posicao": "Meia Esquerda"}, {"nome": "Pedro", "posicao": "Ponta Direita"},
                    {"nome": "David Villa", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "França 1998 (Campeã do Mundo)",
                "jogadores": [
                    {"nome": "Barthez", "posicao": "Goleiro"}, {"nome": "Thuram", "posicao": "Lateral Direito"},
                    {"nome": "Blanc", "posicao": "Zagueiro"}, {"nome": "Desailly", "posicao": "Zagueiro"},
                    {"nome": "Lizarazu", "posicao": "Lateral Esquerdo"}, {"nome": "Deschamps", "posicao": "Volante"},
                    {"nome": "Karembeu", "posicao": "Meia Central"}, {"nome": "Petit", "posicao": "Meia Central"},
                    {"nome": "Zidane", "posicao": "Meia-Atacante"}, {"nome": "Djorkaeff", "posicao": "Segundo Atacante"},
                    {"nome": "Guivarc'h", "posicao": "Centroavante"}
                ]
            },

            # --- LOTE 6 ---
            {
                "titulo": "Leicester City 2015/16 (O Milagre da Premier)",
                "jogadores": [
                    {"nome": "Kasper Schmeichel", "posicao": "Goleiro"}, {"nome": "Danny Simpson", "posicao": "Lateral Direito"},
                    {"nome": "Wes Morgan", "posicao": "Zagueiro"}, {"nome": "Robert Huth", "posicao": "Zagueiro"},
                    {"nome": "Christian Fuchs", "posicao": "Lateral Esquerdo"}, {"nome": "N'Golo Kanté", "posicao": "Volante"},
                    {"nome": "Danny Drinkwater", "posicao": "Volante"}, {"nome": "Riyad Mahrez", "posicao": "Meia Direita"},
                    {"nome": "Marc Albrighton", "posicao": "Meia Esquerda"}, {"nome": "Shinji Okazaki", "posicao": "Segundo Atacante"},
                    {"nome": "Jamie Vardy", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Athletico Paranaense 2001 (Campeão Brasileiro)",
                "jogadores": [
                    {"nome": "Flávio", "posicao": "Goleiro"}, {"nome": "Alessandro", "posicao": "Lateral Direito"},
                    {"nome": "Gustavo", "posicao": "Zagueiro"}, {"nome": "Nem", "posicao": "Zagueiro"},
                    {"nome": "Fabiano", "posicao": "Lateral Esquerdo"}, {"nome": "Cocito", "posicao": "Volante"},
                    {"nome": "Kléberson", "posicao": "Volante"}, {"nome": "Adriano Gabiru", "posicao": "Meia"},
                    {"nome": "Kelly", "posicao": "Meia-Atacante"}, {"nome": "Kléber Pereira", "posicao": "Atacante"},
                    {"nome": "Alex Mineiro", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Bayer Leverkusen 2023/24 (Os Invencíveis)",
                "jogadores": [
                    {"nome": "Hradecky", "posicao": "Goleiro"}, {"nome": "Frimpong", "posicao": "Ala Direito"},
                    {"nome": "Tah", "posicao": "Zagueiro"}, {"nome": "Tapsoba", "posicao": "Zagueiro"},
                    {"nome": "Kossounou", "posicao": "Zagueiro"}, {"nome": "Grimaldo", "posicao": "Ala Esquerdo"},
                    {"nome": "Xhaka", "posicao": "Volante"}, {"nome": "Palacios", "posicao": "Volante"},
                    {"nome": "Hofmann", "posicao": "Meia-Atacante"}, {"nome": "Florian Wirtz", "posicao": "Meia-Atacante"},
                    {"nome": "Boniface", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Ajax 2018/19 (A Surpresa da Champions)",
                "jogadores": [
                    {"nome": "André Onana", "posicao": "Goleiro"}, {"nome": "Mazraoui", "posicao": "Lateral Direito"},
                    {"nome": "De Ligt", "posicao": "Zagueiro"}, {"nome": "Daley Blind", "posicao": "Zagueiro"},
                    {"nome": "Tagliafico", "posicao": "Lateral Esquerdo"}, {"nome": "Lasse Schöne", "posicao": "Volante"},
                    {"nome": "Frenkie de Jong", "posicao": "Meia Central"}, {"nome": "Van de Beek", "posicao": "Meia-Atacante"},
                    {"nome": "Hakim Ziyech", "posicao": "Ponta Direita"}, {"nome": "David Neres", "posicao": "Ponta Esquerda"},
                    {"nome": "Dusan Tadic", "posicao": "Falso 9"}
                ]
            }
        ]

        # ==========================================
        # TODAS AS TRAJETÓRIAS (LOTES 1 ao 6)
        # ==========================================
        trajetorias = [
            # --- LOTE 1 ---
            {
                "titulo": "Gênio Indomável",
                "resposta_oculta": "romario",
                "clubes": ["Vasco", "PSV", "Barcelona", "Flamengo", "Valencia", "Fluminense", "Al-Sadd", "Miami FC", "América-RJ"]
            },
            {
                "titulo": "O Canhão Imparável",
                "resposta_oculta": "roberto carlos",
                "clubes": ["União São João", "Palmeiras", "Inter de Milão", "Real Madrid", "Fenerbahçe", "Corinthians", "Anzhi", "Delhi Dynamos"]
            },
            {
                "titulo": "Maestro de Istambul",
                "resposta_oculta": "alex",
                "clubes": ["Coritiba", "Palmeiras", "Flamengo", "Cruzeiro", "Parma", "Fenerbahçe"]
            },
            {
                "titulo": "Pequeno Mágico",
                "resposta_oculta": "philippe coutinho",
                "clubes": ["Vasco", "Inter de Milão", "Espanyol", "Liverpool", "Barcelona", "Bayern de Munique", "Aston Villa", "Al-Duhail"]
            },
            
            # --- LOTE 2 ---
            {
                "titulo": "O Maior Peregrino",
                "resposta_oculta": "loco abreu",
                "clubes": ["Defensor Sporting", "San Lorenzo", "Deportivo La Coruña", "Nacional", "Cruz Azul", "Monterrey", "Botafogo", "Rosario Central", "Bangu"]
            },
            {
                "titulo": "Cachorro Louco Romeno",
                "resposta_oculta": "edgar davids",
                "clubes": ["Ajax", "Milan", "Juventus", "Barcelona", "Inter de Milão", "Tottenham", "Crystal Palace"]
            },
            {
                "titulo": "Artilheiro da Copa de 2010",
                "resposta_oculta": "diego forlan",
                "clubes": ["Independiente", "Manchester United", "Villarreal", "Atlético de Madrid", "Inter de Milão", "Internacional", "Cerezo Osaka", "Peñarol"]
            },

            # --- LOTE 3 ---
            {
                "titulo": "Rei da Trivela",
                "resposta_oculta": "quaresma",
                "clubes": ["Sporting", "Barcelona", "Porto", "Inter de Milão", "Chelsea", "Besiktas", "Al Ahli", "Kasımpaşa", "Vitória de Guimarães"]
            },
            {
                "titulo": "Artilheiro Alemão-Brasileiro",
                "resposta_oculta": "grafite",
                "clubes": ["Ferroviária", "Santa Cruz", "Grêmio", "Goiás", "São Paulo", "Le Mans", "Wolfsburg", "Al Ahli", "Athletico Paranaense"]
            },
            {
                "titulo": "O Príncipe de Roma",
                "resposta_oculta": "totti",
                "clubes": ["Roma"]
            },

            # --- LOTE 4 ---
            {
                "titulo": "O Maestro Holandês",
                "resposta_oculta": "seedorf",
                "clubes": ["Ajax", "Sampdoria", "Real Madrid", "Inter de Milão", "Milan", "Botafogo"]
            },
            {
                "titulo": "O Imperador",
                "resposta_oculta": "adriano",
                "clubes": ["Flamengo", "Inter de Milão", "Fiorentina", "Parma", "Inter de Milão", "São Paulo", "Flamengo", "Roma", "Corinthians", "Athletico Paranaense", "Miami United"]
            },
            {
                "titulo": "Deus Zlatan",
                "resposta_oculta": "ibrahimovic",
                "clubes": ["Malmö", "Ajax", "Juventus", "Inter de Milão", "Barcelona", "Milan", "PSG", "Manchester United", "LA Galaxy", "Milan"]
            },

            # --- LOTE 5 ---
            {
                "titulo": "O Galinho de Quintino",
                "resposta_oculta": "zico",
                "clubes": ["Flamengo", "Udinese", "Flamengo", "Kashima Antlers"]
            },
            {
                "titulo": "Batigol",
                "resposta_oculta": "batistuta",
                "clubes": ["Newell's Old Boys", "River Plate", "Boca Juniors", "Fiorentina", "Roma", "Inter de Milão", "Al-Arabi"]
            },
            {
                "titulo": "O Chefinho",
                "resposta_oculta": "mascherano",
                "clubes": ["River Plate", "Corinthians", "West Ham", "Liverpool", "Barcelona", "Hebei China Fortune", "Estudiantes"]
            },
            {
                "titulo": "El Mago",
                "resposta_oculta": "valdivia",
                "clubes": ["Colo-Colo", "Rayo Vallecano", "Servette", "Colo-Colo", "Palmeiras", "Al Ain", "Al Wahda", "Monarcas Morelia", "Mazatlán", "Necaxa"]
            },
            {
                "titulo": "O Menino de Ouro",
                "resposta_oculta": "kaka",
                "clubes": ["São Paulo", "Milan", "Real Madrid", "Milan", "São Paulo", "Orlando City"]
            },

            # --- LOTE 6 ---
            {
                "titulo": "O Super Mario",
                "resposta_oculta": "balotelli",
                "clubes": ["Lumezzane", "Inter de Milão", "Manchester City", "Milan", "Liverpool", "Nice", "Marseille", "Brescia", "Monza", "Adana Demirspor", "Sion"]
            },
            {
                "titulo": "O Rei Arturo",
                "resposta_oculta": "vidal",
                "clubes": ["Colo-Colo", "Bayer Leverkusen", "Juventus", "Bayern de Munique", "Barcelona", "Inter de Milão", "Flamengo", "Athletico Paranaense"]
            },
            {
                "titulo": "O Príncipe Ganês",
                "resposta_oculta": "kevin-prince boateng",
                "clubes": ["Hertha Berlin", "Tottenham", "Borussia Dortmund", "Portsmouth", "Genoa", "Milan", "Schalke 04", "Las Palmas", "Eintracht Frankfurt", "Sassuolo", "Barcelona", "Fiorentina", "Besiktas"]
            },
            {
                "titulo": "O Incrível",
                "resposta_oculta": "hulk",
                "clubes": ["Vitória", "Kawasaki Frontale", "Consadole Sapporo", "Tokyo Verdy", "Porto", "Zenit", "Shanghai SIPG", "Atlético Mineiro"]
            },
            {
                "titulo": "Gringo Mais Amado",
                "resposta_oculta": "petkovic",
                "clubes": ["Radnicki Nis", "Estrela Vermelha", "Real Madrid", "Sevilla", "Racing", "Vitória", "Flamengo", "Vasco", "Fluminense", "Goiás", "Santos", "Atlético Mineiro"]
            },
            {
                "titulo": "Canhota Mágica do Penta",
                "resposta_oculta": "rivaldo",
                "clubes": ["Santa Cruz", "Mogi Mirim", "Corinthians", "Palmeiras", "Deportivo La Coruña", "Barcelona", "Milan", "Cruzeiro", "Olympiacos", "AEK", "Bunyodkor", "São Paulo", "Kabuscorp"]
            },
            {
                "titulo": "Xerife do Penta",
                "resposta_oculta": "lucio",
                "clubes": ["Internacional", "Bayer Leverkusen", "Bayern de Munique", "Inter de Milão", "Juventus", "São Paulo", "Palmeiras", "Gama", "Brasiliense"]
            },
            {
                "titulo": "O Fideo",
                "resposta_oculta": "di maria",
                "clubes": ["Rosario Central", "Benfica", "Real Madrid", "Manchester United", "PSG", "Juventus", "Benfica"]
            }
        ]

        self.stdout.write(self.style.WARNING("========================================"))
        self.stdout.write(self.style.WARNING(" INICIANDO POVOAMENTO DO MEGA LOTE"))
        self.stdout.write(self.style.WARNING("========================================\n"))

        # 1. PROCESSAR ELENCOS E ALIMENTAR BANCO DE JOGADORES
        self.stdout.write(self.style.MIGRATE_HEADING("Adicionando Elencos Clássicos..."))
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            
            for j in dados["jogadores"]:
                # Cria o jogador no Banco Centralizado se não existir
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                # Associa ao desafio
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    jogador_vinculado=jogador_obj,
                    posicao_tatica=j["posicao"],
                    ordem=0
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Elenco "{categoria.titulo}" e jogadores registados!'))

        self.stdout.write("\n")

        # 2. PROCESSAR TRAJETÓRIAS E ALIMENTAR BANCO DE CLUBES
        self.stdout.write(self.style.MIGRATE_HEADING("Adicionando Trajetórias Misteriosas..."))
        for dados in trajetorias:
            categoria, _ = CategoriaDesafio.objects.get_or_create(
                titulo=dados["titulo"], 
                tipo='trajetoria', 
                resposta_oculta=dados["resposta_oculta"]
            )
            
            for indice, nome_clube in enumerate(dados["clubes"]):
                # Cria o clube no Banco Centralizado se não existir
                clube_obj, _ = Clube.objects.get_or_create(nome=nome_clube)
                
                # Associa ao desafio
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    clube_vinculado=clube_obj,
                    ordem=indice + 1
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{categoria.titulo}" e clubes registados!'))

        self.stdout.write(self.style.WARNING("\n========================================"))
        self.stdout.write(self.style.SUCCESS(" MEGA LOTE CARREGADO COM SUCESSO!"))
        self.stdout.write(self.style.WARNING("========================================"))