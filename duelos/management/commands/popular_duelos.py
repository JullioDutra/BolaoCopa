from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Adiciona o Lote 10: Era de Prata e os Imigrantes da Bola (Inéditos)'

    def handle(self, *args, **kwargs):
        # ==========================================
        # ELENCOS - LOTE 10 (ORDEM 4-3-3 EXATA PARA O FRONTEND)
        # 1 Goleiro | 4 Defesa | 3 Meio | 3 Ataque
        # ==========================================
        elencos = [
            {
                "titulo": "Vasco 2000 (O Expresso da Virada)",
                "jogadores": [
                    {"nome": "Helton", "posicao": "Goleiro"}, 
                    {"nome": "Clebson", "posicao": "Lateral Direito"},
                    {"nome": "Odvan", "posicao": "Zagueiro"}, 
                    {"nome": "Mauro Galvão", "posicao": "Zagueiro"},
                    {"nome": "Jorginho Paulista", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Jorginho", "posicao": "Volante"},
                    {"nome": "Juninho Paulista", "posicao": "Meia Central"}, 
                    {"nome": "Juninho Pernambucano", "posicao": "Meia-Atacante"},
                    {"nome": "Euller", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Pedrinho", "posicao": "Ponta Direita"},
                    {"nome": "Romário", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Chelsea 2004/05 (A Muralha de Mourinho)",
                "jogadores": [
                    {"nome": "Petr Cech", "posicao": "Goleiro"}, 
                    {"nome": "Paulo Ferreira", "posicao": "Lateral Direito"},
                    {"nome": "Ricardo Carvalho", "posicao": "Zagueiro"}, 
                    {"nome": "John Terry", "posicao": "Zagueiro"},
                    {"nome": "William Gallas", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Makelele", "posicao": "Volante"},
                    {"nome": "Tiago", "posicao": "Meia Central"}, 
                    {"nome": "Frank Lampard", "posicao": "Meia-Atacante"},
                    {"nome": "Damien Duff", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Arjen Robben", "posicao": "Ponta Direita"},
                    {"nome": "Drogba", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Liverpool 2004/05 (Milagre de Istambul)",
                "jogadores": [
                    {"nome": "Jerzy Dudek", "posicao": "Goleiro"}, 
                    {"nome": "Steve Finnan", "posicao": "Lateral Direito"},
                    {"nome": "Jamie Carragher", "posicao": "Zagueiro"}, 
                    {"nome": "Sami Hyypiä", "posicao": "Zagueiro"},
                    {"nome": "Djimi Traoré", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Xabi Alonso", "posicao": "Volante"},
                    {"nome": "Luis Garcia", "posicao": "Meia Central"}, 
                    {"nome": "Steven Gerrard", "posicao": "Meia-Atacante"},
                    {"nome": "John Arne Riise", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Harry Kewell", "posicao": "Ponta Direita"},
                    {"nome": "Milan Baros", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Cruzeiro 2013 (A Raposa Campeã)",
                "jogadores": [
                    {"nome": "Fábio", "posicao": "Goleiro"}, 
                    {"nome": "Ceará", "posicao": "Lateral Direito"},
                    {"nome": "Dedé", "posicao": "Zagueiro"}, 
                    {"nome": "Bruno Rodrigo", "posicao": "Zagueiro"},
                    {"nome": "Egídio", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Nilton", "posicao": "Volante"},
                    {"nome": "Lucas Silva", "posicao": "Meia Central"}, 
                    {"nome": "Everton Ribeiro", "posicao": "Meia Direita"},
                    {"nome": "Ricardo Goulart", "posicao": "Meia-Atacante"}, 
                    {"nome": "Willian Bigode", "posicao": "Segundo Atacante"},
                    {"nome": "Borges", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "França 1998 (Donos da Casa)",
                "jogadores": [
                    {"nome": "Fabien Barthez", "posicao": "Goleiro"}, 
                    {"nome": "Lilian Thuram", "posicao": "Lateral Direito"},
                    {"nome": "Laurent Blanc", "posicao": "Zagueiro"}, 
                    {"nome": "Marcel Desailly", "posicao": "Zagueiro"},
                    {"nome": "Bixente Lizarazu", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Didier Deschamps", "posicao": "Volante"},
                    {"nome": "Emmanuel Petit", "posicao": "Volante"}, 
                    {"nome": "Christian Karembeu", "posicao": "Meia Direita"},
                    {"nome": "Zinedine Zidane", "posicao": "Meia-Atacante"}, 
                    {"nome": "Youri Djorkaeff", "posicao": "Segundo Atacante"},
                    {"nome": "Stéphane Guivarc'h", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Athletico Paranaense 2001 (O Furacão)",
                "jogadores": [
                    {"nome": "Flávio", "posicao": "Goleiro"}, 
                    {"nome": "Alessandro", "posicao": "Lateral Direito"},
                    {"nome": "Nem", "posicao": "Zagueiro"}, 
                    {"nome": "Gustavo", "posicao": "Zagueiro"},
                    {"nome": "Fabiano", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Cocito", "posicao": "Volante"},
                    {"nome": "Kléberson", "posicao": "Volante"}, 
                    {"nome": "Adriano Gabiru", "posicao": "Meia Central"},
                    {"nome": "Kelly", "posicao": "Meia-Atacante"}, 
                    {"nome": "Kléber Pereira", "posicao": "Segundo Atacante"},
                    {"nome": "Alex Mineiro", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Boca Juniors 2003 (Reis do Japão)",
                "jogadores": [
                    {"nome": "Abbondanzieri", "posicao": "Goleiro"}, 
                    {"nome": "Luis Perea", "posicao": "Lateral Direito"},
                    {"nome": "Rolando Schiavi", "posicao": "Zagueiro"}, 
                    {"nome": "Nicolás Burdisso", "posicao": "Zagueiro"},
                    {"nome": "Clemente Rodríguez", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Raúl Cascini", "posicao": "Volante"},
                    {"nome": "Sebastián Battaglia", "posicao": "Volante"}, 
                    {"nome": "Diego Cagna", "posicao": "Meia Central"},
                    {"nome": "Matías Donnet", "posicao": "Meia-Atacante"}, 
                    {"nome": "Pedro Iarley", "posicao": "Segundo Atacante"},
                    {"nome": "Carlos Tevez", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Portugal 2016 (A Conquista da Europa)",
                "jogadores": [
                    {"nome": "Rui Patrício", "posicao": "Goleiro"}, 
                    {"nome": "Cédric Soares", "posicao": "Lateral Direito"},
                    {"nome": "Pepe", "posicao": "Zagueiro"}, 
                    {"nome": "José Fonte", "posicao": "Zagueiro"},
                    {"nome": "Raphael Guerreiro", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "William Carvalho", "posicao": "Volante"},
                    {"nome": "Adrien Silva", "posicao": "Meia Central"}, 
                    {"nome": "Renato Sanches", "posicao": "Meia Direita"},
                    {"nome": "João Mário", "posicao": "Meia Esquerda"}, 
                    {"nome": "Nani", "posicao": "Segundo Atacante"},
                    {"nome": "Cristiano Ronaldo", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Juventus 1995/96 (A Velha Senhora)",
                "jogadores": [
                    {"nome": "Angelo Peruzzi", "posicao": "Goleiro"}, 
                    {"nome": "Moreno Torricelli", "posicao": "Lateral Direito"},
                    {"nome": "Pietro Vierchowod", "posicao": "Zagueiro"}, 
                    {"nome": "Ciro Ferrara", "posicao": "Zagueiro"},
                    {"nome": "Gianluca Pessotto", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Paulo Sousa", "posicao": "Volante"},
                    {"nome": "Didier Deschamps", "posicao": "Volante"}, 
                    {"nome": "Antonio Conte", "posicao": "Meia Central"},
                    {"nome": "Alessandro Del Piero", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Fabrizio Ravanelli", "posicao": "Ponta Direita"},
                    {"nome": "Gianluca Vialli", "posicao": "Centroavante"}
                ]
            }
        ]

        # ==========================================
        # TRAJETÓRIAS - LOTE 10 (OS IMIGRANTES DA BOLA)
        # ==========================================
        trajetorias = [
            {
                "titulo": "O Rei das Cavadinhas",
                "resposta_oculta": "loco abreu",
                "clubes": ["San Lorenzo", "Deportivo La Coruña", "Grêmio", "Cruz Azul", "Monterrey", "River Plate", "Botafogo", "Figueirense", "Rosario Central", "Bangu"]
            },
            {
                "titulo": "As Pedaladas Santistas",
                "resposta_oculta": "robinho",
                "clubes": ["Santos", "Real Madrid", "Manchester City", "Milan", "Guangzhou Evergrande", "Atlético Mineiro", "Sivasspor", "Istanbul Basaksehir"]
            },
            {
                "titulo": "O Mago Romeno",
                "resposta_oculta": "hagi",
                "clubes": ["Steaua Bucuresti", "Real Madrid", "Brescia", "Barcelona", "Galatasaray"]
            },
            {
                "titulo": "O Tigre Colombiano",
                "resposta_oculta": "falcao garcia",
                "clubes": ["River Plate", "Porto", "Atlético de Madrid", "Monaco", "Manchester United", "Chelsea", "Galatasaray", "Rayo Vallecano"]
            },
            {
                "titulo": "Valdanito",
                "resposta_oculta": "hernan crespo",
                "clubes": ["River Plate", "Parma", "Lazio", "Inter de Milão", "Chelsea", "Milan", "Genoa"]
            },
            {
                "titulo": "O Animal",
                "resposta_oculta": "edmundo",
                "clubes": ["Vasco", "Palmeiras", "Flamengo", "Corinthians", "Fiorentina", "Napoli", "Cruzeiro", "Tokyo Verdy", "Fluminense", "Figueirense"]
            },
            {
                "titulo": "O Gringo Mais Carioca do Brasil",
                "resposta_oculta": "petkovic",
                "clubes": ["Estrela Vermelha", "Real Madrid", "Sevilla", "Vitória", "Flamengo", "Vasco", "Fluminense", "Goiás", "Santos", "Atlético Mineiro"]
            },
            {
                "titulo": "O Mágico Luso-Brasileiro",
                "resposta_oculta": "deco",
                "clubes": ["Corinthians", "Alverca", "Salgueiros", "Porto", "Barcelona", "Chelsea", "Fluminense"]
            },
            {
                "titulo": "Paredão de Gelo",
                "resposta_oculta": "dida",
                "clubes": ["Vitória", "Cruzeiro", "Lugano", "Corinthians", "Milan", "Portuguesa", "Grêmio", "Internacional"]
            },
            {
                "titulo": "Lenda do Arsenal",
                "resposta_oculta": "thierry henry",
                "clubes": ["Monaco", "Juventus", "Arsenal", "Barcelona", "New York Red Bulls"]
            }
        ]

        self.stdout.write("Iniciando Povoamento do Lote 10...")

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
            self.stdout.write(self.style.SUCCESS(f'[+] Elenco "{dados["titulo"]}" processado.'))

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

        self.stdout.write(self.style.WARNING("\nLote 10 Finalizado! A Prancheta agora tem 100% de times inéditos e o campinho tá pronto pro show!"))
