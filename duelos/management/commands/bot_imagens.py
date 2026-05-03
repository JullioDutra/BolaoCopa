import requests
import time
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from duelos.models import CartaTrunfo
from duckduckgo_search import DDGS

class Command(BaseCommand):
    help = 'Busca automaticamente imagens PNG transparentes (Renders) para cartas sem foto'

    def handle(self, *args, **kwargs):
        # Pega todas as cartas que estão com o campo de foto vazio
        cartas_sem_foto = CartaTrunfo.objects.filter(foto__isnull=True) | CartaTrunfo.objects.filter(foto__exact='')
        
        if not cartas_sem_foto:
            self.stdout.write(self.style.SUCCESS("O Elenco está completo! Nenhuma carta sem foto."))
            return

        self.stdout.write(f"Iniciando o Olheiro... Procurando fotos para {cartas_sem_foto.count()} cartas.")

        with DDGS() as ddgs:
            for carta in cartas_sem_foto:
                # O segredo tá na busca: "nome do jogador render png" traz imagens com fundo transparente do FIFA
                termo_busca = f"{carta.nome} {carta.clube.nome} fifa render png transparent"
                self.stdout.write(f"\nBuscando: {termo_busca}...")
                
                try:
                    # Busca imagens no DuckDuckGo (pega o 1º resultado)
                    resultados = list(ddgs.images(termo_busca, max_results=1))
                    
                    if resultados:
                        img_url = resultados[0]['image']
                        self.stdout.write(f"  -> Imagem encontrada: {img_url}")
                        
                        # Faz o download fingindo ser um navegador comum
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                        resposta = requests.get(img_url, headers=headers, timeout=10)
                        
                        if resposta.status_code == 200:
                            # Salva a imagem no banco vinculada ao jogador
                            nome_arquivo = f"render_{carta.nome.replace(' ', '_').lower()}.png"
                            carta.foto.save(nome_arquivo, ContentFile(resposta.content), save=True)
                            self.stdout.write(self.style.SUCCESS(f"  -> GOLAÇO! Foto salva para {carta.nome}!"))
                        else:
                            self.stdout.write(self.style.ERROR(f"  -> Trave! Erro ao baixar: HTTP {resposta.status_code}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"  -> Olheiro não achou imagem para {carta.nome}."))
                        
                    # ⚠️ Pausa de 3 segundos para o DuckDuckGo não bloquear o seu servidor
                    time.sleep(3)
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  -> Falha no jogador {carta.nome}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("\nVarredura do Olheiro concluída com sucesso!"))