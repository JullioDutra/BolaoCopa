import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from minijogo.models import EstatisticaJogador

class Command(BaseCommand):
    help = 'Baixa fotos da Wikipedia para jogadores que estão sem imagem.'

    def handle(self, *args, **kwargs):
        jogadores = EstatisticaJogador.objects.filter(foto__isnull=True) | EstatisticaJogador.objects.filter(foto__exact='')
        
        if not jogadores.exists():
            self.stdout.write(self.style.WARNING('Todos os jogadores do banco já possuem foto!'))
            return

        url_api = "https://pt.wikipedia.org/w/api.php"
        
        # A WIKIPEDIA EXIGE ISSO: Um User-Agent customizado para não ser bloqueado
        headers = {
            'User-Agent': 'MinijogoCartolandiaApp/1.0 (https://seusite.pythonanywhere.com; contato@seusite.com)'
        }

        for jogador in jogadores:
            # Limpa o nome para a busca (Ex: "Felipe (Mão de Alface)" vira só "Felipe")
            nome_busca = jogador.nome.split(' (')[0].strip()
            
            self.stdout.write(f"Pesquisando foto para: {nome_busca}...")
            
            params = {
                "action": "query",
                "format": "json",
                "prop": "pageimages",
                "titles": nome_busca,
                "pithumbsize": 400
            }
            
            try:
                # Enviando o cabeçalho de identificação (headers)
                response = requests.get(url_api, params=params, headers=headers, timeout=10)
                
                # Se a Wikipedia der algum erro diferente de 200 (OK), ele pula o jogador
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"Erro {response.status_code} da Wikipedia."))
                    continue

                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                
                foto_url = None
                for page_id, page_info in pages.items():
                    if "thumbnail" in page_info:
                        foto_url = page_info["thumbnail"]["source"]
                        break
                
                if foto_url:
                    # Faz o download da imagem (também mandando o User-Agent)
                    img_response = requests.get(foto_url, headers=headers, timeout=10)
                    
                    if img_response.status_code == 200:
                        nome_arquivo = f"{jogador.nome.replace(' ', '_').lower()}.jpg"
                        jogador.foto.save(nome_arquivo, ContentFile(img_response.content), save=True)
                        self.stdout.write(self.style.SUCCESS(f"✅ Foto baixada e salva: {jogador.nome}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ Erro ao fazer download do arquivo para {jogador.nome}"))
                else:
                    self.stdout.write(self.style.WARNING(f"❌ Nenhuma foto encontrada na Wikipedia para {nome_busca}"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"🚨 Erro ao processar {jogador.nome}: {e}"))

        self.stdout.write(self.style.SUCCESS('Processo de busca de fotos finalizado!'))
