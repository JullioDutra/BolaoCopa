import requests
from io import BytesIO
from PIL import Image, ImageDraw
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from minijogo.models import EstatisticaJogador

class Command(BaseCommand):
    help = 'Popula a base de jogadores, baixando fotos precisas da Wiki e criando cards fallback.'

    def gerar_card_padrao(self, jogador):
        """Desenha um card estilizado para quem não tem foto na Wiki."""
        img = Image.new('RGB', (300, 400), color=(44, 62, 80))
        draw = ImageDraw.Draw(img)

        partes_nome = jogador.nome.split()
        iniciais = f"{partes_nome[0][0]}{partes_nome[1][0]}" if len(partes_nome) >= 2 else partes_nome[0][0:2]
        iniciais = iniciais.upper()

        draw.text((130, 150), iniciais, fill=(241, 196, 15), align="center")
        draw.text((20, 320), f"Nome: {jogador.nome}", fill=(255, 255, 255))
        draw.text((20, 350), f"Posicao: {jogador.get_posicao_display()}", fill=(241, 196, 15))
        draw.text((20, 370), f"Clube: {jogador.clube}", fill=(189, 195, 199))

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        nome_arquivo = f"{jogador.nome.replace(' ', '_').lower()}_card.png"
        jogador.foto.save(nome_arquivo, ContentFile(buffer.getvalue()), save=True)

    def handle(self, *args, **kwargs):
        # A nova base de dados rica fornecida por você
        JOGADORES = [
            # ---------------- LENDAS ----------------
            {"nome": "Pelé", "clube": "Santos / Seleção Brasileira", "posicao": "ATA", "gols": 767, "assistencias": 200, "cartoes_amarelos": 20, "cartoes_vermelhos": 1, "jogos": 831, "wiki": "Pelé"},
            {"nome": "Diego Maradona", "clube": "Boca Juniors / Napoli / Seleção Argentina", "posicao": "MEI", "gols": 312, "assistencias": 180, "cartoes_amarelos": 45, "cartoes_vermelhos": 3, "jogos": 588, "wiki": "Diego_Maradona"},
            {"nome": "Johan Cruyff", "clube": "Ajax / Barcelona / Seleção Holandesa", "posicao": "ATA", "gols": 396, "assistencias": 150, "cartoes_amarelos": 15, "cartoes_vermelhos": 1, "jogos": 668, "wiki": "Johan_Cruyff"},
            {"nome": "Franz Beckenbauer", "clube": "Bayern de Munique / Seleção Alemã", "posicao": "ZAG", "gols": 105, "assistencias": 90, "cartoes_amarelos": 25, "cartoes_vermelhos": 0, "jogos": 741, "wiki": "Franz_Beckenbauer"},
            {"nome": "Garrincha", "clube": "Botafogo / Seleção Brasileira", "posicao": "ATA", "gols": 249, "assistencias": 130, "cartoes_amarelos": 10, "cartoes_vermelhos": 0, "jogos": 581, "wiki": "Garrincha"},
            {"nome": "Zico", "clube": "Flamengo / Seleção Brasileira", "posicao": "MEI", "gols": 508, "assistencias": 220, "cartoes_amarelos": 30, "cartoes_vermelhos": 1, "jogos": 731, "wiki": "Zico"},
            {"nome": "Michel Platini", "clube": "Juventus / Seleção Francesa", "posicao": "MEI", "gols": 353, "assistencias": 170, "cartoes_amarelos": 20, "cartoes_vermelhos": 0, "jogos": 580, "wiki": "Michel_Platini"},
            {"nome": "Ferenc Puskás", "clube": "Real Madrid / Seleção Húngara", "posicao": "ATA", "gols": 729, "assistencias": 150, "cartoes_amarelos": 10, "cartoes_vermelhos": 0, "jogos": 754, "wiki": "Ferenc_Puskás"},
            {"nome": "Eusébio", "clube": "Benfica / Seleção Portuguesa", "posicao": "ATA", "gols": 733, "assistencias": 140, "cartoes_amarelos": 12, "cartoes_vermelhos": 0, "jogos": 745, "wiki": "Eusébio"},
            {"nome": "Alfredo Di Stéfano", "clube": "Real Madrid / Seleção Espanhola", "posicao": "ATA", "gols": 512, "assistencias": 160, "cartoes_amarelos": 15, "cartoes_vermelhos": 0, "jogos": 700, "wiki": "Alfredo_Di_Stéfano"},
            {"nome": "Gerd Müller", "clube": "Bayern de Munique / Seleção Alemã", "posicao": "ATA", "gols": 634, "assistencias": 90, "cartoes_amarelos": 18, "cartoes_vermelhos": 0, "jogos": 607, "wiki": "Gerd_Müller"},
            {"nome": "George Best", "clube": "Manchester United / Seleção Norte-Irlandesa", "posicao": "ATA", "gols": 205, "assistencias": 120, "cartoes_amarelos": 25, "cartoes_vermelhos": 2, "jogos": 527, "wiki": "George_Best"},
            {"nome": "Romário", "clube": "Vasco / Barcelona / Seleção Brasileira", "posicao": "ATA", "gols": 772, "assistencias": 190, "cartoes_amarelos": 40, "cartoes_vermelhos": 3, "jogos": 994, "wiki": "Romário"},
            {"nome": "Ronaldinho Gaúcho", "clube": "Barcelona / Milan / Seleção Brasileira", "posicao": "MEI", "gols": 353, "assistencias": 270, "cartoes_amarelos": 55, "cartoes_vermelhos": 2, "jogos": 848, "wiki": "Ronaldinho"},
            {"nome": "Rivaldo", "clube": "Barcelona / Seleção Brasileira", "posicao": "MEI", "gols": 350, "assistencias": 180, "cartoes_amarelos": 60, "cartoes_vermelhos": 4, "jogos": 803, "wiki": "Rivaldo"},
            {"nome": "Ronaldo Fenômeno", "clube": "Barcelona / Real Madrid / Seleção Brasileira", "posicao": "ATA", "gols": 414, "assistencias": 130, "cartoes_amarelos": 35, "cartoes_vermelhos": 1, "jogos": 518, "wiki": "Ronaldo_(Brazilian_footballer)"},
            {"nome": "Cafu", "clube": "São Paulo / Milan / Seleção Brasileira", "posicao": "LAT", "gols": 22, "assistencias": 95, "cartoes_amarelos": 90, "cartoes_vermelhos": 2, "jogos": 776, "wiki": "Cafu"},
            {"nome": "Roberto Carlos", "clube": "Real Madrid / Seleção Brasileira", "posicao": "LAT", "gols": 71, "assistencias": 160, "cartoes_amarelos": 100, "cartoes_vermelhos": 3, "jogos": 693, "wiki": "Roberto_Carlos_(footballer)"},
            {"nome": "Kaká", "clube": "Milan / Real Madrid / Seleção Brasileira", "posicao": "MEI", "gols": 226, "assistencias": 150, "cartoes_amarelos": 40, "cartoes_vermelhos": 1, "jogos": 599, "wiki": "Kaká"},
            {"nome": "Zinedine Zidane", "clube": "Juventus / Real Madrid / Seleção Francesa", "posicao": "MEI", "gols": 125, "assistencias": 145, "cartoes_amarelos": 65, "cartoes_vermelhos": 4, "jogos": 690, "wiki": "Zinedine_Zidane"},
            {"nome": "Alessandro Del Piero", "clube": "Juventus / Seleção Italiana", "posicao": "ATA", "gols": 346, "assistencias": 150, "cartoes_amarelos": 60, "cartoes_vermelhos": 1, "jogos": 826, "wiki": "Alessandro_Del_Piero"},
            {"nome": "Francesco Totti", "clube": "Roma / Seleção Italiana", "posicao": "ATA", "gols": 307, "assistencias": 210, "cartoes_amarelos": 90, "cartoes_vermelhos": 5, "jogos": 785, "wiki": "Francesco_Totti"},
            {"nome": "Paolo Maldini", "clube": "Milan / Seleção Italiana", "posicao": "ZAG", "gols": 33, "assistencias": 60, "cartoes_amarelos": 55, "cartoes_vermelhos": 1, "jogos": 902, "wiki": "Paolo_Maldini"},
            {"nome": "Fabio Cannavaro", "clube": "Parma / Real Madrid / Seleção Italiana", "posicao": "ZAG", "gols": 24, "assistencias": 25, "cartoes_amarelos": 80, "cartoes_vermelhos": 3, "jogos": 671, "wiki": "Fabio_Cannavaro"},
            {"nome": "Gianluigi Buffon", "clube": "Parma / Juventus / Seleção Italiana", "posicao": "GOL", "gols": 0, "assistencias": 1, "cartoes_amarelos": 25, "cartoes_vermelhos": 2, "jogos": 1103, "wiki": "Gianluigi_Buffon"},
            {"nome": "Andrés Iniesta", "clube": "Barcelona / Seleção Espanhola", "posicao": "MEI", "gols": 90, "assistencias": 140, "cartoes_amarelos": 70, "cartoes_vermelhos": 1, "jogos": 941, "wiki": "Andrés_Iniesta"},
            {"nome": "Xavi", "clube": "Barcelona / Seleção Espanhola", "posicao": "MEI", "gols": 85, "assistencias": 180, "cartoes_amarelos": 95, "cartoes_vermelhos": 3, "jogos": 1057, "wiki": "Xavi"},
            {"nome": "Carles Puyol", "clube": "Barcelona / Seleção Espanhola", "posicao": "ZAG", "gols": 20, "assistencias": 20, "cartoes_amarelos": 100, "cartoes_vermelhos": 2, "jogos": 593, "wiki": "Carles_Puyol"},
            {"nome": "Iker Casillas", "clube": "Real Madrid / Porto / Seleção Espanhola", "posicao": "GOL", "gols": 0, "assistencias": 0, "cartoes_amarelos": 20, "cartoes_vermelhos": 1, "jogos": 1017, "wiki": "Iker_Casillas"},
            {"nome": "Raúl González", "clube": "Real Madrid / Seleção Espanhola", "posicao": "ATA", "gols": 371, "assistencias": 150, "cartoes_amarelos": 45, "cartoes_vermelhos": 1, "jogos": 887, "wiki": "Raúl_González"},
            {"nome": "Marco van Basten", "clube": "Ajax / Milan / Seleção Holandesa", "posicao": "ATA", "gols": 300, "assistencias": 90, "cartoes_amarelos": 20, "cartoes_vermelhos": 0, "jogos": 437, "wiki": "Marco_van_Basten"},
            {"nome": "David Beckham", "clube": "Manchester United / Real Madrid / Seleção Inglesa", "posicao": "MEI", "gols": 130, "assistencias": 260, "cartoes_amarelos": 70, "cartoes_vermelhos": 3, "jogos": 815, "wiki": "David_Beckham"},
            {"nome": "Ryan Giggs", "clube": "Manchester United / Seleção Galesa", "posicao": "MEI", "gols": 168, "assistencias": 260, "cartoes_amarelos": 40, "cartoes_vermelhos": 0, "jogos": 963, "wiki": "Ryan_Giggs"},
            {"nome": "Thierry Henry", "clube": "Arsenal / Barcelona / Seleção Francesa", "posicao": "ATA", "gols": 411, "assistencias": 230, "cartoes_amarelos": 55, "cartoes_vermelhos": 2, "jogos": 900, "wiki": "Thierry_Henry"},
            {"nome": "Didier Drogba", "clube": "Chelsea / Seleção Marfinense", "posicao": "ATA", "gols": 331, "assistencias": 140, "cartoes_amarelos": 90, "cartoes_vermelhos": 4, "jogos": 723, "wiki": "Didier_Drogba"},
            {"nome": "Samuel Eto'o", "clube": "Barcelona / Inter de Milão / Seleção Camaronesa", "posicao": "ATA", "gols": 380, "assistencias": 110, "cartoes_amarelos": 60, "cartoes_vermelhos": 2, "jogos": 741, "wiki": "Samuel_Eto'o"},

            # ---------------- ATUAIS / RECENTES ----------------
            {"nome": "Cristiano Ronaldo", "clube": "Al-Nassr / Seleção Portuguesa", "posicao": "ATA", "gols": 934, "assistencias": 250, "cartoes_amarelos": 130, "cartoes_vermelhos": 12, "jogos": 1260, "wiki": "Cristiano_Ronaldo"},
            {"nome": "Lionel Messi", "clube": "Inter Miami / Seleção Argentina", "posicao": "ATA", "gols": 870, "assistencias": 380, "cartoes_amarelos": 95, "cartoes_vermelhos": 3, "jogos": 1080, "wiki": "Lionel_Messi"},
            {"nome": "Neymar Jr", "clube": "Santos / Seleção Brasileira", "posicao": "ATA", "gols": 480, "assistencias": 230, "cartoes_amarelos": 120, "cartoes_vermelhos": 5, "jogos": 780, "wiki": "Neymar"},
            {"nome": "Kylian Mbappé", "clube": "Real Madrid / Seleção Francesa", "posicao": "ATA", "gols": 350, "assistencias": 150, "cartoes_amarelos": 45, "cartoes_vermelhos": 1, "jogos": 460, "wiki": "Kylian_Mbappé"},
            {"nome": "Erling Haaland", "clube": "Manchester City / Seleção Norueguesa", "posicao": "ATA", "gols": 290, "assistencias": 55, "cartoes_amarelos": 30, "cartoes_vermelhos": 1, "jogos": 330, "wiki": "Erling_Haaland"},
            {"nome": "Mohamed Salah", "clube": "Liverpool / Seleção Egípcia", "posicao": "ATA", "gols": 280, "assistencias": 140, "cartoes_amarelos": 40, "cartoes_vermelhos": 0, "jogos": 620, "wiki": "Mohamed_Salah"},
            {"nome": "Robert Lewandowski", "clube": "Barcelona / Seleção Polonesa", "posicao": "ATA", "gols": 660, "assistencias": 170, "cartoes_amarelos": 55, "cartoes_vermelhos": 1, "jogos": 830, "wiki": "Robert_Lewandowski"},
            {"nome": "Karim Benzema", "clube": "Al-Ittihad / Seleção Francesa", "posicao": "ATA", "gols": 430, "assistencias": 210, "cartoes_amarelos": 60, "cartoes_vermelhos": 2, "jogos": 820, "wiki": "Karim_Benzema"},
            {"nome": "Luka Modrić", "clube": "Real Madrid / Milan / Seleção Croata", "posicao": "MEI", "gols": 90, "assistencias": 170, "cartoes_amarelos": 90, "cartoes_vermelhos": 2, "jogos": 900, "wiki": "Luka_Modrić"},
            {"nome": "Toni Kroos", "clube": "Real Madrid (aposentado) / Seleção Alemã", "posicao": "MEI", "gols": 65, "assistencias": 200, "cartoes_amarelos": 75, "cartoes_vermelhos": 1, "jogos": 730, "wiki": "Toni_Kroos"},
            {"nome": "Kevin De Bruyne", "clube": "Napoli / Seleção Belga", "posicao": "MEI", "gols": 130, "assistencias": 270, "cartoes_amarelos": 55, "cartoes_vermelhos": 1, "jogos": 620, "wiki": "Kevin_De_Bruyne"},
            {"nome": "Antoine Griezmann", "clube": "Atlético de Madrid / Seleção Francesa", "posicao": "ATA", "gols": 300, "assistencias": 150, "cartoes_amarelos": 70, "cartoes_vermelhos": 2, "jogos": 780, "wiki": "Antoine_Griezmann"},
            {"nome": "Luis Suárez", "clube": "Inter Miami / Seleção Uruguaia", "posicao": "ATA", "gols": 530, "assistencias": 230, "cartoes_amarelos": 100, "cartoes_vermelhos": 8, "jogos": 890, "wiki": "Luis_Suárez"},
            {"nome": "Sergio Agüero", "clube": "Manchester City (aposentado) / Seleção Argentina", "posicao": "ATA", "gols": 430, "assistencias": 140, "cartoes_amarelos": 55, "cartoes_vermelhos": 1, "jogos": 750, "wiki": "Sergio_Agüero"},
            {"nome": "Zlatan Ibrahimović", "clube": "Milan (aposentado) / Seleção Sueca", "posicao": "ATA", "gols": 573, "assistencias": 190, "cartoes_amarelos": 85, "cartoes_vermelhos": 5, "jogos": 895, "wiki": "Zlatan_Ibrahimović"},
            {"nome": "Harry Kane", "clube": "Bayern de Munique / Seleção Inglesa", "posicao": "ATA", "gols": 420, "assistencias": 110, "cartoes_amarelos": 35, "cartoes_vermelhos": 0, "jogos": 650, "wiki": "Harry_Kane"},
            {"nome": "Virgil van Dijk", "clube": "Liverpool / Seleção Holandesa", "posicao": "ZAG", "gols": 45, "assistencias": 30, "cartoes_amarelos": 60, "cartoes_vermelhos": 2, "jogos": 570, "wiki": "Virgil_van_Dijk"},
            {"nome": "Alisson Becker", "clube": "Liverpool / Seleção Brasileira", "posicao": "GOL", "gols": 1, "assistencias": 1, "cartoes_amarelos": 15, "cartoes_vermelhos": 0, "jogos": 470, "wiki": "Alisson_Becker"},
            {"nome": "Ederson", "clube": "Fenerbahçe / Seleção Brasileira", "posicao": "GOL", "gols": 1, "assistencias": 2, "cartoes_amarelos": 20, "cartoes_vermelhos": 1, "jogos": 430, "wiki": "Ederson_(footballer,_born_1993)"},
            {"nome": "Vinícius Júnior", "clube": "Real Madrid / Seleção Brasileira", "posicao": "ATA", "gols": 130, "assistencias": 100, "cartoes_amarelos": 55, "cartoes_vermelhos": 2, "jogos": 380, "wiki": "Vinícius_Júnior"},
            {"nome": "Rodrygo", "clube": "Real Madrid / Seleção Brasileira", "posicao": "ATA", "gols": 80, "assistencias": 70, "cartoes_amarelos": 30, "cartoes_vermelhos": 1, "jogos": 300, "wiki": "Rodrygo_(footballer)"},
            {"nome": "Casemiro", "clube": "Manchester United / Seleção Brasileira", "posicao": "MEI", "gols": 55, "assistencias": 45, "cartoes_amarelos": 130, "cartoes_vermelhos": 6, "jogos": 620, "wiki": "Casemiro"},
            {"nome": "Thiago Silva", "clube": "Fluminense / Seleção Brasileira", "posicao": "ZAG", "gols": 55, "assistencias": 25, "cartoes_amarelos": 100, "cartoes_vermelhos": 5, "jogos": 850, "wiki": "Thiago_Silva"},
            {"nome": "Dani Alves", "clube": "Puebla (aposentado) / Seleção Brasileira", "posicao": "LAT", "gols": 40, "assistencias": 180, "cartoes_amarelos": 150, "cartoes_vermelhos": 6, "jogos": 1000, "wiki": "Dani_Alves"},
            {"nome": "Marcelo", "clube": "Fluminense / Seleção Brasileira", "posicao": "LAT", "gols": 45, "assistencias": 130, "cartoes_amarelos": 110, "cartoes_vermelhos": 4, "jogos": 750, "wiki": "Marcelo_(footballer,_born_1988)"},
            {"nome": "Pepe", "clube": "Porto / Seleção Portuguesa", "posicao": "ZAG", "gols": 40, "assistencias": 15, "cartoes_amarelos": 160, "cartoes_vermelhos": 15, "jogos": 830, "wiki": "Pepe_(footballer,_born_1983)"},
            {"nome": "Sergio Ramos", "clube": "Monterrey / Seleção Espanhola", "posicao": "ZAG", "gols": 130, "assistencias": 45, "cartoes_amarelos": 200, "cartoes_vermelhos": 26, "jogos": 1080, "wiki": "Sergio_Ramos"},

            # ---------------- CAMPEONATO BRASILEIRO ATUAL ----------------
            {"nome": "Gabriel Barbosa (Gabigol)", "clube": "Cruzeiro", "posicao": "ATA", "gols": 220, "assistencias": 60, "cartoes_amarelos": 65, "cartoes_vermelhos": 3, "jogos": 520, "wiki": "Gabriel_Barbosa"},
            {"nome": "Hulk", "clube": "Atlético Mineiro / Seleção Brasileira", "posicao": "ATA", "gols": 340, "assistencias": 120, "cartoes_amarelos": 80, "cartoes_vermelhos": 3, "jogos": 700, "wiki": "Hulk_(footballer)"},
            {"nome": "Everton Ribeiro", "clube": "Flamengo", "posicao": "MEI", "gols": 90, "assistencias": 130, "cartoes_amarelos": 60, "cartoes_vermelhos": 1, "jogos": 620, "wiki": "Everton_Ribeiro"},
            {"nome": "Giorgian De Arrascaeta", "clube": "Flamengo / Seleção Uruguaia", "posicao": "MEI", "gols": 130, "assistencias": 140, "cartoes_amarelos": 45, "cartoes_vermelhos": 1, "jogos": 480, "wiki": "Giorgian_De_Arrascaeta"},
            {"nome": "Raphael Veiga", "clube": "Palmeiras", "posicao": "MEI", "gols": 100, "assistencias": 70, "cartoes_amarelos": 55, "cartoes_vermelhos": 2, "jogos": 420, "wiki": "Raphael_Veiga"},
            {"nome": "Endrick", "clube": "Real Madrid / Seleção Brasileira", "posicao": "ATA", "gols": 45, "assistencias": 15, "cartoes_amarelos": 10, "cartoes_vermelhos": 0, "jogos": 120, "wiki": "Endrick_(footballer)"},
            {"nome": "Estêvão", "clube": "Chelsea / Seleção Brasileira", "posicao": "ATA", "gols": 30, "assistencias": 20, "cartoes_amarelos": 8, "cartoes_vermelhos": 0, "jogos": 100, "wiki": "Estêvão_(footballer)"},
            {"nome": "Pedro", "clube": "Flamengo / Seleção Brasileira", "posicao": "ATA", "gols": 160, "assistencias": 30, "cartoes_amarelos": 35, "cartoes_vermelhos": 1, "jogos": 340, "wiki": "Pedro_(footballer,_born_1997)"},
            {"nome": "Yuri Alberto", "clube": "Corinthians", "posicao": "ATA", "gols": 95, "assistencias": 25, "cartoes_amarelos": 30, "cartoes_vermelhos": 1, "jogos": 260, "wiki": "Yuri_Alberto"},
            {"nome": "Gerson", "clube": "Flamengo / Seleção Brasileira", "posicao": "MEI", "gols": 60, "assistencias": 55, "cartoes_amarelos": 70, "cartoes_vermelhos": 2, "jogos": 460, "wiki": "Gerson_(footballer)"},
            {"nome": "Everton Cebolinha", "clube": "Fenerbahçe / Seleção Brasileira", "posicao": "ATA", "gols": 110, "assistencias": 90, "cartoes_amarelos": 40, "cartoes_vermelhos": 1, "jogos": 450, "wiki": "Everton_(footballer,_born_1996)"},
            {"nome": "Alan Patrick", "clube": "Internacional", "posicao": "MEI", "gols": 100, "assistencias": 95, "cartoes_amarelos": 60, "cartoes_vermelhos": 2, "jogos": 460, "wiki": "Alan_Patrick"},
        ]

        cadastrados = 0
        atualizados = 0

        # Mudamos a URL para a WIKIPEDIA EM INGLÊS, já que os slugs que estamos passando são em inglês
        url_api_en = "https://en.wikipedia.org/w/api.php"
        headers = {'User-Agent': 'MinijogoCartolandiaApp/1.0'}

        for dados in JOGADORES:
            # 1. Salvar as estatísticas do jogador no banco
            jogador, created = EstatisticaJogador.objects.update_or_create(
                nome=dados['nome'],
                defaults={
                    'clube': dados['clube'],
                    'posicao': dados['posicao'],
                    'gols': dados['gols'],
                    'assistencias': dados['assistencias'],
                    'cartoes_amarelos': dados['cartoes_amarelos'],
                    'cartoes_vermelhos': dados['cartoes_vermelhos'],
                    'jogos': dados['jogos'],
                    'ativo': True
                }
            )
            
            if created:
                cadastrados += 1
            else:
                atualizados += 1

            # 2. Tentar baixar a foto usando o slug da Wikipedia que informamos
            if not jogador.foto:
                self.stdout.write(f"Buscando foto para: {jogador.nome} (Wiki: {dados['wiki']})...")
                
                params = {
                    "action": "query",
                    "format": "json",
                    "prop": "pageimages",
                    "titles": dados['wiki'],
                    "pithumbsize": 400,
                    "redirects": 1
                }
                
                foto_baixada = False
                try:
                    response = requests.get(url_api_en, params=params, headers=headers, timeout=5)
                    if response.status_code == 200:
                        pages = response.json().get("query", {}).get("pages", {})
                        foto_url = None
                        
                        for page_id, page_info in pages.items():
                            if "thumbnail" in page_info:
                                foto_url = page_info["thumbnail"]["source"]
                                break
                        
                        if foto_url:
                            img_response = requests.get(foto_url, headers=headers, timeout=5)
                            if img_response.status_code == 200:
                                nome_arquivo = f"{jogador.nome.replace(' ', '_').lower()}.jpg"
                                jogador.foto.save(nome_arquivo, ContentFile(img_response.content), save=True)
                                self.stdout.write(self.style.SUCCESS(f"✅ Wiki foto salva: {jogador.nome}"))
                                foto_baixada = True
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erro na requisição: {e}"))
                
                # Se não conseguiu baixar da Wiki, cria a carta fallback
                if not foto_baixada:
                    self.gerar_card_padrao(jogador)
                    self.stdout.write(self.style.WARNING(f"🎨 Card desenhado para: {jogador.nome}"))

        self.stdout.write(self.style.SUCCESS(f'Processo 100% finalizado! {cadastrados} jogadores criados e {atualizados} atualizados com foto.'))
