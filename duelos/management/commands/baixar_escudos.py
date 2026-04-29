import requests
import time
import urllib.parse
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from duelos.models import Clube

class Command(BaseCommand):
    help = 'Robô Scout v2: Busca, valida e baixa escudos dos clubes sem cair no bloqueio da Wikipedia'

    def handle(self, *args, **kwargs):
        clubes_sem_escudo = Clube.objects.filter(escudo='') | Clube.objects.filter(escudo__isnull=True)
        total = clubes_sem_escudo.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("Todos os clubes já possuem escudo! O vestiário tá completo."))
            return

        self.stdout.write(self.style.WARNING(f"Iniciando a caçada por {total} escudos... O Robô Scout v2 entrou em campo!"))

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

        # Crachá oficial pro robô não ser barrado na porta do estádio (Wikipedia)
        headers = {
            'User-Agent': 'CartolandiaScoutBot/2.0 (admin@cartolandia.local) Python-Requests'
        }

        for clube in clubes_sem_escudo:
            termo_busca = termos_exatos.get(clube.nome, f"{clube.nome} futebol")
            
            # Codifica a URL (troca os espaços por %20 e ajusta acentos)
            termo_encoded = urllib.parse.quote(termo_busca)
            
            self.stdout.write(f"Buscando: {clube.nome}...")
            
            url_search = f"https://pt.wikipedia.org/w/api.php?action=opensearch&search={termo_encoded}&limit=1&format=json"
            
            try:
                res = requests.get(url_search, headers=headers)
                
                # Se não retornar 200 OK, a gente pula pra evitar quebrar o JSON
                if res.status_code != 200:
                    self.stdout.write(self.style.WARNING(f"  [!] Bloqueio detectado ao buscar {clube.nome}. Status {res.status_code}"))
                    time.sleep(1)
                    continue
                    
                res_search = res.json()
                
                # Se não achou na Wikipedia PT, tenta na EN
                if len(res_search) < 4 or len(res_search[3]) == 0:
                    url_search_en = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={termo_encoded}&limit=1&format=json"
                    res_en = requests.get(url_search_en, headers=headers)
                    if res_en.status_code == 200:
                        res_search = res_en.json()

                if len(res_search) >= 4 and len(res_search[3]) > 0:
                    page_url = res_search[3][0]
                    
                    # 2. Entra na página do clube
                    html = requests.get(page_url, headers=headers).text
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 3. Procura a imagem dentro da ficha técnica (infobox)
                    img_tag = soup.select_one('table.infobox img')
                    
                    if img_tag and img_tag.has_attr('src'):
                        img_url = "https:" + img_tag['src']
                        
                        img_response = requests.get(img_url, headers=headers)
                        
                        if img_response.status_code == 200 and 'image' in img_response.headers.get('Content-Type', ''):
                            ext = img_url.split('.')[-1].lower()
                            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'svg', 'gif']:
                                ext = 'png'
                                
                            nome_arquivo = f"{clube.nome.replace(' ', '_').lower()}.{ext}"
                            
                            clube.escudo.save(nome_arquivo, ContentFile(img_response.content), save=True)
                            self.stdout.write(self.style.SUCCESS(f"  [+] Golaço! Escudo garantido: {clube.nome}"))
                        else:
                            self.stdout.write(self.style.ERROR(f"  [-] Imagem corrompida para: {clube.nome}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"  [-] Escudo não encontrado na ficha técnica: {clube.nome}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  [-] Clube não encontrado na Wikipedia: {clube.nome}"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [!] Erro na jogada ao buscar {clube.nome}: {e}"))
            
            # Cera estratégica (meio segundo) pra não levar cartão vermelho da Wikipedia
            time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS("\nApita o árbitro! O Robô v2 finalizou o trabalho! 🏆"))
