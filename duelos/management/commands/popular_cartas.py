import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from duelos.models import ClubeFutebol, CartaTrunfo

class Command(BaseCommand):
    help = 'Cria cartas do Super Trunfo em lote. Baixa imagens automaticamente se a URL for fornecida.'

    def handle(self, *args, **kwargs):
        # 📋 LISTA DE CRAQUES
        # Para adicionar mais, basta copiar uma linha e mudar os dados.
        # Se não tiver uma boa imagem PNG em link agora, deixe "img_url": ""
        
        jogadores = [
            # FLAMENGO
            {"nome": "Zico", "clube": "Flamengo", "pos": "MEI", "ovr": 96, "rit": 82, "fin": 94, "pas": 96, "dri": 93, "def": 45, "fis": 75, "img_url": ""},
            {"nome": "Gabigol", "clube": "Flamengo", "pos": "ATA", "ovr": 85, "rit": 84, "fin": 88, "pas": 75, "dri": 80, "def": 35, "fis": 82, "img_url": ""},
            
            # SANTOS
            {"nome": "Pelé", "clube": "Santos", "pos": "ATA", "ovr": 99, "rit": 95, "fin": 98, "pas": 93, "dri": 96, "def": 50, "fis": 85, "img_url": ""},
            {"nome": "Neymar", "clube": "Santos", "pos": "ATA", "ovr": 92, "rit": 94, "fin": 87, "pas": 88, "dri": 96, "def": 30, "fis": 65, "img_url": ""},
            
            # SÃO PAULO
            {"nome": "Rogério Ceni", "clube": "São Paulo", "pos": "GOL", "ovr": 89, "rit": 40, "fin": 85, "pas": 90, "dri": 50, "def": 92, "fis": 80, "img_url": ""},
            
            # PALMEIRAS
            {"nome": "Marcos", "clube": "Palmeiras", "pos": "GOL", "ovr": 88, "rit": 45, "fin": 20, "pas": 60, "dri": 40, "def": 90, "fis": 85, "img_url": ""},
            
            # CORINTHIANS
            {"nome": "Sócrates", "clube": "Corinthians", "pos": "MEI", "ovr": 91, "rit": 75, "fin": 85, "pas": 94, "dri": 88, "def": 60, "fis": 80, "img_url": ""},
            
            # VASCO
            {"nome": "Romário", "clube": "Vasco da Gama", "pos": "ATA", "ovr": 94, "rit": 88, "fin": 98, "pas": 78, "dri": 92, "def": 25, "fis": 70, "img_url": ""},
        ]

        cartas_criadas = 0

        for j in jogadores:
            # 1. Garante que o clube existe no banco
            clube, _ = ClubeFutebol.objects.get_or_create(nome=j['clube'])

            # 2. Cria a carta (se não existir para não duplicar)
            carta, created = CartaTrunfo.objects.get_or_create(
                nome=j['nome'],
                clube=clube,
                defaults={
                    'posicao': j['pos'],
                    'overall': j['ovr'],
                    'ritmo': j['rit'],
                    'finalizacao': j['fin'],
                    'passe': j['pas'],
                    'drible': j['dri'],
                    'defesa': j['def'],
                    'fisico': j['fis']
                }
            )

            if created:
                cartas_criadas += 1
                self.stdout.write(self.style.SUCCESS(f"[CRIADO] Carta: {carta.nome} ({carta.overall})"))

                # 3. Baixa a imagem se a URL foi fornecida
                if j.get('img_url'):
                    try:
                        self.stdout.write(f"Baixando imagem para {carta.nome}...")
                        resposta = requests.get(j['img_url'], timeout=10)
                        if resposta.status_code == 200:
                            # Monta o nome do arquivo (ex: pele.png)
                            nome_arquivo = f"{carta.nome.replace(' ', '_').lower()}.png"
                            carta.foto.save(nome_arquivo, ContentFile(resposta.content), save=True)
                            self.stdout.write(self.style.SUCCESS(f"  -> Imagem de {carta.nome} salva!"))
                        else:
                            self.stdout.write(self.style.ERROR(f"  -> Erro ao baixar imagem de {carta.nome}: Status {resposta.status_code}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  -> Falha na imagem de {carta.nome}: {str(e)}"))
            else:
                self.stdout.write(self.style.WARNING(f"[EXISTE] {carta.nome} já está no banco."))

        self.stdout.write(self.style.SUCCESS(f"\nOperação concluída! {cartas_criadas} novas cartas adicionadas."))