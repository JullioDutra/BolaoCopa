import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from minijogo.models import EstatisticaJogador

class Command(BaseCommand):
    help = 'Baixa fotos da Wikipedia para jogadores que estão sem imagem.'

    def handle(self, *args, **kwargs):
        # Seleciona apenas os jogadores que não têm foto
        jogadores = EstatisticaJogador.objects.filter(foto__isnull=True) | EstatisticaJogador.objects.filter(foto__exact='')
        
        if not jogadores.exists():
            self.stdout.write(self.style.WARNING('Todos os jogadores do banco já possuem foto!'))
            return

        # A API da Wikipedia está na whitelist do PythonAnywhere gratuito
        url_api = "https://pt.wikipedia.org/w/api.php"

        for jogador in jogadores:
            self.stdout.write(f"Pesquisando foto para: {jogador.nome}...")
            
            # Passo 1: Consultar a API para pegar a miniatura (thumbnail) da página
            params = {
                "action": "query",
                "format": "json",
                "prop": "pageimages",
                "titles": jogador.nome,
                "pithumbsize": 400  # Tamanho ideal para um card
            }
            
            try:
                response = requests.get(url_api, params=params, timeout=10)
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                
                foto_url = None
                # Navega pelo dicionário retornado para achar a URL da imagem
                for page_id, page_info in pages.items():
                    if "thumbnail" in page_info:
                        foto_url = page_info["thumbnail"]["source"]
                        break
                
                if foto_url:
                    # Passo 2: Fazer o download da imagem da URL encontrada
                    img_response = requests.get(foto_url, timeout=10)
                    
                    if img_response.status_code == 200:
                        # Passo 3: Salvar a imagem no campo do Django
                        nome_arquivo = f"{jogador.nome.replace(' ', '_').lower()}.jpg"
                        jogador.foto.save(nome_arquivo, ContentFile(img_response.content), save=True)
                        self.stdout.write(self.style.SUCCESS(f"✅ Foto baixada e salva: {jogador.nome}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ Erro ao fazer download do arquivo para {jogador.nome}"))
                else:
                    self.stdout.write(self.style.WARNING(f"❌ Nenhuma foto encontrada na Wikipedia para {jogador.nome}"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"🚨 Erro de conexão ao processar {jogador.nome}: {e}"))

        self.stdout.write(self.style.SUCCESS('Processo de busca de fotos finalizado!'))
