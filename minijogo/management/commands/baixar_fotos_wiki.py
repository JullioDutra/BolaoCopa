import requests
from io import BytesIO
from PIL import Image, ImageDraw
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from minijogo.models import EstatisticaJogador

class Command(BaseCommand):
    help = 'Tenta baixar da Wiki. Se falhar, desenha um card com as iniciais.'

    def gerar_card_padrao(self, jogador):
        """Desenha um card estilizado para quem não tem foto na Wiki."""
        # Fundo escuro
        img = Image.new('RGB', (300, 400), color=(44, 62, 80))
        draw = ImageDraw.Draw(img)

        # Pegar iniciais (Ex: Flávio Caça-Rato -> FC)
        partes_nome = jogador.nome.split()
        iniciais = f"{partes_nome[0][0]}{partes_nome[1][0]}" if len(partes_nome) >= 2 else partes_nome[0][0:2]
        iniciais = iniciais.upper()

        # Desenhar no card
        draw.text((130, 150), iniciais, fill=(241, 196, 15), align="center")
        draw.text((20, 320), f"Nome: {jogador.nome}", fill=(255, 255, 255))
        draw.text((20, 350), f"Posicao: {jogador.get_posicao_display()}", fill=(241, 196, 15))
        draw.text((20, 370), f"Clube: {jogador.clube}", fill=(189, 195, 199))

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        nome_arquivo = f"{jogador.nome.replace(' ', '_').lower()}_card.png"
        jogador.foto.save(nome_arquivo, ContentFile(buffer.getvalue()), save=True)

    def handle(self, *args, **kwargs):
        jogadores = EstatisticaJogador.objects.filter(foto__isnull=True) | EstatisticaJogador.objects.filter(foto__exact='')
        
        if not jogadores.exists():
            self.stdout.write(self.style.WARNING('Todos os jogadores já possuem foto!'))
            return

        url_api = "https://pt.wikipedia.org/w/api.php"
        headers = {'User-Agent': 'MinijogoCartolandiaApp/1.0'}

        for jogador in jogadores:
            nome_busca = jogador.nome.split(' (')[0].strip()
            self.stdout.write(f"Processando: {nome_busca}...")
            
            params = {
                "action": "query",
                "format": "json",
                "prop": "pageimages",
                "titles": nome_busca,
                "pithumbsize": 400,
                "redirects": 1  # Ajuda a corrigir nomes parecidos
            }
            
            foto_baixada = False
            try:
                response = requests.get(url_api, params=params, headers=headers, timeout=5)
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
            except Exception:
                pass # Ignora o erro da net e vai pro desenho do card
            
            # Se a foto não foi baixada por qualquer motivo, cria o card padrão!
            if not foto_baixada:
                self.gerar_card_padrao(jogador)
                self.stdout.write(self.style.WARNING(f"🎨 Card desenhado para: {jogador.nome}"))

        self.stdout.write(self.style.SUCCESS('Processo 100% finalizado. Todos os jogadores agora têm imagem!'))
