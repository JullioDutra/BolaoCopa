import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from duelos.models import Clube

class Command(BaseCommand):
    help = 'Robô Scout: Busca, valida e baixa escudos dos clubes automaticamente via Wikipedia'

    def handle(self, *args, **kwargs):
        # Filtra apenas os clubes que ainda estão sem escudo
        clubes_sem_escudo = Clube.objects.filter(escudo='') | Clube.objects.filter(escudo__isnull=True)
        total = clubes_sem_escudo.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("Todos os clubes já possuem escudo! O vestiário tá completo."))
            return

        self.stdout.write(self.style.WARNING(f"Iniciando a caçada por {total} escudos... O Robô Scout entrou em campo!"))

        # ==========================================
        # A GRANDE PESQUISA (Dicionário Mestre)
        # Corrige nomes curtos/ambíguos para o nome exato da Wikipedia
        # ==========================================
        termos_exatos = {
            "Monaco": "AS Monaco FC",
            "Milan": "Associazione Calcio Milan",
            "Roma": "Associazione Sportiva Roma",
            "Lazio": "Società Sportiva Lazio",
            "Everton": "Everton Football Club",
            "Arsenal": "Arsenal Football Club",
            "Chelsea": "Chelsea Football Club",
            "Liverpool": "Liverpool F.C.",
            "Porto": "Futebol Clube do Porto",
            "Benfica": "Sport Lisboa e Benfica",
            "Sporting": "Sporting Clube de Portugal",
            "Vasco": "Club de Regatas Vasco da Gama",
            "Botafogo": "Botafogo de Futebol e Regatas",
            "Cruzeiro": "Cruzeiro Esporte Clube",
            "Grêmio": "Grêmio Foot-Ball Porto Alegrense",
            "Internacional": "Sport Club Internacional",
            "Corinthians": "Sport Club Corinthians Paulista",
            "São Paulo": "São Paulo Futebol Clube",
            "Flamengo": "Clube de Regatas do Flamengo",
            "Fluminense": "Fluminense Football Club",
            "River Plate": "Club Atlético River Plate",
            "Boca Juniors": "Club Atlético Boca Juniors",
            "Independiente": "Club Atlético Independiente",
            "Racing": "Racing Club",
            "San Lorenzo": "Club Atlético San Lorenzo de Almagro",
            "Peñarol": "Club Atlético Peñarol",
            "Nacional": "Club Nacional de Football",
            "Juventus": "Juventus Football Club",
            "Fiorentina": "ACF Fiorentina",
            "Napoli": "Società Sportiva Calcio Napoli",
            "Bayern de Munique": "FC Bayern München",
            "Borussia Dortmund": "Borussia Dortmund",
            "Schalke 04": "FC Schalke 04",
            "Bayer Leverkusen": "Bayer 04 Leverkusen",
            "Ajax": "AFC Ajax",
            "PSV": "PSV Eindhoven",
            "Feyenoord": "Feyenoord Rotterdam",
            "Galatasaray": "Galatasaray SK",
            "Fenerbahçe": "Fenerbahçe SK",
            "Besiktas": "Beşiktaş JK",
            "Kairat": "FC Kairat",
            "Suduva": "FK Sūduva",
            "Neftchi Baku": "Neftçi PFK",
            "Al-Nassr": "Al-Nassr Football Club",
            "Al-Hilal": "Al-Hilal Saudi Football Club",
            "Guadalajara": "Club Deportivo Guadalajara",
            "Como": "Como 1907",
            "Sion": "FC Sion",
            "Brescia": "Brescia Calcio",
            "Venezia": "Venezia FC",
            "QPR": "Queens Park Rangers Football Club",
            "Saint-Étienne": "Association Sportive de Saint-Étienne Loire",
            "PSG": "Paris Saint-Germain Football Club",
            "LA Galaxy": "Los Angeles Galaxy",
            "Los Angeles FC": "Los Angeles Football Club",
            "CSKA Moscou": "PFC CSKA Moscovo"
        }

        # Simula ser um navegador real para não ser bloqueado
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        for clube in clubes_sem_escudo:
            # Se não estiver no dicionário mestre, ele adiciona "futebol" pra ajudar a Wikipedia a entender
            termo_busca = termos_exatos.get(clube.nome, f"{clube.nome} futebol")
            
            self.stdout.write(f"Buscando: {clube.nome}...")
            
            # 1. Pesquisa na API da Wikipedia para achar o link da página do clube
            url_search = f"https://pt.wikipedia.org/w/api.php?action=opensearch&search={termo_busca}&limit=1&format=json"
            
            try:
                res_search = requests.get(url_search, headers=headers).json()
                
                # Se não achou na Wikipedia em Português, tenta na em Inglês
                if len(res_search[3]) == 0:
                    url_search_en = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={termo_busca}&limit=1&format=json"
                    res_search = requests.get(url_search_en, headers=headers).json()

                if len(res_search[3]) > 0:
                    page_url = res_search[3][0]
                    
                    # 2. Entra na página do clube e raspa o HTML
                    html = requests.get(page_url, headers=headers).text
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 3. Procura a imagem que fica dentro da ficha técnica (infobox)
                    img_tag = soup.select_one('table.infobox img')
                    
                    if img_tag and img_tag.has_attr('src'):
                        img_url = "https:" + img_tag['src']
                        
                        # 4. VALIDAÇÃO: Testa se a imagem realmente existe no servidor
                        img_response = requests.get(img_url, headers=headers)
                        
                        # Se o código for 200 (OK) e for um arquivo de imagem real
                        if img_response.status_code == 200 and 'image' in img_response.headers.get('Content-Type', ''):
                            # Pega a extensão da imagem (png, svg, jpg)
                            ext = img_url.split('.')[-1].lower()
                            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'svg', 'gif']:
                                ext = 'png'
                                
                            nome_arquivo = f"{clube.nome.replace(' ', '_').lower()}.{ext}"
                            
                            # Salva a imagem física no banco de dados
                            clube.escudo.save(nome_arquivo, ContentFile(img_response.content), save=True)
                            self.stdout.write(self.style.SUCCESS(f"  [+] Golaço! Escudo garantido: {clube.nome}"))
                        else:
                            self.stdout.write(self.style.ERROR(f"  [-] Imagem corrompida ou inacessível para: {clube.nome}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"  [-] Escudo não encontrado na página para: {clube.nome}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  [-] Clube não encontrado na Wikipedia: {clube.nome}"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [!] O VAR marcou falta! Erro ao buscar {clube.nome}: {e}"))

        self.stdout.write(self.style.SUCCESS("\nApita o árbitro! Varredura finalizada. Os escudos estão no vestiário! 🏆"))
