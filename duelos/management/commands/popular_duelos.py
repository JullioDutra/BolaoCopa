from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Adiciona o Lote 12: Os Imortais e os Reis do Passaporte'

    def handle(self, *args, **kwargs):
        # ==========================================
        # ELENCOS - LOTE 12 (ORDEM 4-3-3 EXATA PARA O FRONTEND)
        # 1 Goleiro | 4 Defesa | 3 Meio | 3 Ataque
        # ==========================================
        elencos = [
            {
                "titulo": "Brasil 1970 (O Tri no México)",
                "jogadores": [
                    {"nome": "Félix", "posicao": "Goleiro"}, 
                    {"nome": "Carlos Alberto Torres", "posicao": "Lateral Direito"},
                    {"nome": "Brito", "posicao": "Zagueiro"}, 
                    {"nome": "Piazza", "posicao": "Zagueiro"},
                    {"nome": "Everaldo", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Clodoaldo", "posicao": "Volante"},
                    {"nome": "Gérson", "posicao": "Meia Central"}, 
                    {"nome": "Rivellino", "posicao": "Meia Esquerda"},
                    {"nome": "Jairzinho", "posicao": "Ponta Direita"}, 
                    {"nome": "Tostão", "posicao": "Segundo Atacante"},
                    {"nome": "Pelé", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Porto 2003/04 (A Máquina de Mourinho)",
                "jogadores": [
                    {"nome": "Vítor Baía", "posicao": "Goleiro"}, 
                    {"nome": "Paulo Ferreira", "posicao": "Lateral Direito"},
                    {"nome": "Jorge Costa", "posicao": "Zagueiro"}, 
                    {"nome": "Ricardo Carvalho", "posicao": "Zagueiro"},
                    {"nome": "Nuno Valente", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Costinha", "posicao": "Volante"},
                    {"nome": "Maniche", "posicao": "Volante"}, 
                    {"nome": "Pedro Mendes", "posicao": "Meia Central"},
                    {"nome": "Deco", "posicao": "Meia-Atacante"}, 
                    {"nome": "Carlos Alberto", "posicao": "Segundo Atacante"},
                    {"nome": "Derlei", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Botafogo 1995 (Túlio Maravilha)",
                "jogadores": [
                    {"nome": "Wagner", "posicao": "Goleiro"}, 
                    {"nome": "Wilson Goiano", "posicao": "Lateral Direito"},
                    {"nome": "Gottardo", "posicao": "Zagueiro"}, 
                    {"nome": "Gonçalves", "posicao": "Zagueiro"},
                    {"nome": "André Silva", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Jamir", "posicao": "Volante"},
                    {"nome": "Leandro Ávila", "posicao": "Volante"}, 
                    {"nome": "Sérgio Manoel", "posicao": "Meia Esquerda"},
                    {"nome": "Beto", "posicao": "Meia-Atacante"}, 
                    {"nome": "Donizete Pantera", "posicao": "Segundo Atacante"},
                    {"nome": "Túlio Maravilha", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Internacional 2010 (Bicampeão da América)",
                "jogadores": [
                    {"nome": "Renan", "posicao": "Goleiro"}, 
                    {"nome": "Nei", "posicao": "Lateral Direito"},
                    {"nome": "Bolívar", "posicao": "Zagueiro"}, 
                    {"nome": "Índio", "posicao": "Zagueiro"},
                    {"nome": "Kleber", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Sandro", "posicao": "Volante"},
                    {"nome": "Guiñazú", "posicao": "Volante"}, 
                    {"nome": "Tinga", "posicao": "Meia Central"},
                    {"nome": "D'Alessandro", "posicao": "Meia-Atacante"}, 
                    {"nome": "Taison", "posicao": "Ponta Esquerda"},
                    {"nome": "Rafael Sóbis", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Boca Juniors 2007 (O Show de Riquelme)",
                "jogadores": [
                    {"nome": "Mauricio Caranta", "posicao": "Goleiro"}, 
                    {"nome": "Hugo Ibarra", "posicao": "Lateral Direito"},
                    {"nome": "Cata Díaz", "posicao": "Zagueiro"}, 
                    {"nome": "Morel Rodríguez", "posicao": "Zagueiro"},
                    {"nome": "Clemente Rodríguez", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Pablo Ledesma", "posicao": "Volante"},
                    {"nome": "Éver Banega", "posicao": "Meia Central"}, 
                    {"nome": "Neri Cardozo", "posicao": "Meia Esquerda"},
                    {"nome": "Riquelme", "posicao": "Meia-Atacante"}, 
                    {"nome": "Rodrigo Palacio", "posicao": "Segundo Atacante"},
                    {"nome": "Martín Palermo", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Ajax 2018/19 (A Sensação da Europa)",
                "jogadores": [
                    {"nome": "Onana", "posicao": "Goleiro"}, 
                    {"nome": "Mazraoui", "posicao": "Lateral Direito"},
                    {"nome": "De Ligt", "posicao": "Zagueiro"}, 
                    {"nome": "Blind", "posicao": "Zagueiro"},
                    {"nome": "Tagliafico", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Lasse Schöne", "posicao": "Volante"},
                    {"nome": "Frenkie de Jong", "posicao": "Volante"}, 
                    {"nome": "Van de Beek", "posicao": "Meia-Atacante"},
                    {"nome": "Ziyech", "posicao": "Ponta Direita"}, 
                    {"nome": "David Neres", "posicao": "Ponta Esquerda"},
                    {"nome": "Dusan Tadic", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Argentina 1986 (O Auge de D10S)",
                "jogadores": [
                    {"nome": "Pumpido", "posicao": "Goleiro"}, 
                    {"nome": "Cuciuffo", "posicao": "Lateral Direito"},
                    {"nome": "Tata Brown", "posicao": "Zagueiro"}, 
                    {"nome": "Oscar Ruggeri", "posicao": "Zagueiro"},
                    {"nome": "Olarticoechea", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Checho Batista", "posicao": "Volante"},
                    {"nome": "Ricardo Giusti", "posicao": "Meia Direita"}, 
                    {"nome": "Enrique", "posicao": "Meia Central"},
                    {"nome": "Burruchaga", "posicao": "Meia-Atacante"}, 
                    {"nome": "Maradona", "posicao": "Segundo Atacante"},
                    {"nome": "Jorge Valdano", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Vasco 2011 (Trem Bala da Colina)",
                "jogadores": [
                    {"nome": "Fernando Prass", "posicao": "Goleiro"}, 
                    {"nome": "Fagner", "posicao": "Lateral Direito"},
                    {"nome": "Dedé", "posicao": "Zagueiro"}, 
                    {"nome": "Anderson Martins", "posicao": "Zagueiro"},
                    {"nome": "Ramon", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Rômulo", "posicao": "Volante"},
                    {"nome": "Eduardo Costa", "posicao": "Volante"}, 
                    {"nome": "Juninho Pernambucano", "posicao": "Meia Central"},
                    {"nome": "Diego Souza", "posicao": "Meia-Atacante"}, 
                    {"nome": "Eder Luis", "posicao": "Ponta Direita"},
                    {"nome": "Alecsandro", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Galatasaray 1999/00 (Reis de Istambul)",
                "jogadores": [
                    {"nome": "Taffarel", "posicao": "Goleiro"}, 
                    {"nome": "Capone", "posicao": "Lateral Direito"},
                    {"nome": "Popescu", "posicao": "Zagueiro"}, 
                    {"nome": "Bülent Korkmaz", "posicao": "Zagueiro"},
                    {"nome": "Ergün Penbe", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Suat Kaya", "posicao": "Volante"},
                    {"nome": "Okan Buruk", "posicao": "Meia Central"}, 
                    {"nome": "Gheorghe Hagi", "posicao": "Meia-Atacante"},
                    {"nome": "Arif Erdem", "posicao": "Ponta Direita"}, 
                    {"nome": "Hasan Sas", "posicao": "Ponta Esquerda"},
                    {"nome": "Hakan Sükür", "posicao": "Centroavante"}
                ]
            }
        ]

        # ==========================================
        # TRAJETÓRIAS - LOTE 12 (REIS DO PASSAPORTE)
        # ==========================================
        trajetorias = [
            {
                "titulo": "Super Mario",
                "resposta_oculta": "balotelli",
                "clubes": ["Lumezzane", "Inter de Milão", "Manchester City", "Milan", "Liverpool", "Nice", "Marseille", "Brescia", "Monza", "Adana Demirspor", "Sion"]
            },
            {
                "titulo": "O Nômade Ganês",
                "resposta_oculta": "kevin prince boateng",
                "clubes": ["Hertha Berlin", "Tottenham", "Portsmouth", "Milan", "Schalke 04", "Las Palmas", "Eintracht Frankfurt", "Sassuolo", "Barcelona", "Fiorentina", "Besiktas", "Monza"]
            },
            {
                "titulo": "O Garoto de Ouro",
                "resposta_oculta": "alexandre pato",
                "clubes": ["Internacional", "Milan", "Corinthians", "São Paulo", "Chelsea", "Villarreal", "São Paulo", "Orlando City"]
            },
            {
                "titulo": "O Incrível",
                "resposta_oculta": "hulk",
                "clubes": ["Vitória", "Kawasaki Frontale", "Consadole Sapporo", "Tokyo Verdy", "Porto", "Zenit", "Shanghai SIPG", "Atlético Mineiro"]
            },
            {
                "titulo": "Cachavacha",
                "resposta_oculta": "diego forlan",
                "clubes": ["Independiente", "Manchester United", "Villarreal", "Atlético de Madrid", "Inter de Milão", "Internacional", "Cerezo Osaka", "Peñarol"]
            },
            {
                "titulo": "El Depredador",
                "resposta_oculta": "paolo guerrero",
                "clubes": ["Bayern de Munique", "Hamburgo", "Corinthians", "Flamengo", "Internacional", "Avaí", "Racing", "LDU"]
            },
            {
                "titulo": "O Maestro Holandês",
                "resposta_oculta": "wesley sneijder",
                "clubes": ["Ajax", "Real Madrid", "Inter de Milão", "Galatasaray", "Nice"]
            },
            {
                "titulo": "A Lenda da Baviera",
                "resposta_oculta": "bastian schweinsteiger",
                "clubes": ["Bayern de Munique", "Manchester United", "Chicago Fire"]
            },
            {
                "titulo": "O Xerife Luso-Brasileiro",
                "resposta_oculta": "pepe",
                "clubes": ["Marítimo", "Porto", "Real Madrid", "Besiktas", "Porto"]
            },
            {
                "titulo": "Rei da Trivela",
                "resposta_oculta": "ricardo quaresma",
                "clubes": ["Sporting", "Barcelona", "Porto", "Inter de Milão", "Chelsea", "Besiktas", "Al Ahli", "Kasımpaşa", "Vitória de Guimarães"]
            }
        ]

        self.stdout.write("Iniciando Povoamento do Lote 12...")

        # 1. PROCESSAR ELENCOS E POPULAR BANCO DE JOGADORES
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            for indice, j in enumerate(dados["jogadores"]):
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                # Respeitando a ordem do array (0=Goleiro, 1..4=Defesa, 5..7=Meio, 8..10=Ataque)
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    jogador_vinculado=jogador_obj,
                    posicao_tatica=j["posicao"],
                    ordem=indice
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Elenco "{dados["titulo"]}" processado com Tática 4-3-3.'))

        # 2. PROCESSAR TRAJETÓRIAS E POPULAR CLUBES
        for dados in trajetorias:
            categoria, _ = CategoriaDesafio.objects.get_or_create(
                titulo=dados["titulo"], 
                tipo='trajetoria', 
                resposta_oculta=dados["resposta_oculta"]
            )
            for indice, nome_clube in enumerate(dados["clubes"]):
                clube_obj, _ = Clube.objects.get_or_create(nome=nome_clube)
                
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    clube_vinculado=clube_obj,
                    ordem=indice + 1
                )
            
            nome_jogador = dados["resposta_oculta"].title()
            JogadorBanco.objects.get_or_create(nome=nome_jogador)
            
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{dados["titulo"]}" processada.'))

        self.stdout.write(self.style.WARNING("\nLote 12 Finalizado! O X1 agora tem times de todas as eras!"))
