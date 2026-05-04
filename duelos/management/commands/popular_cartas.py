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
            # ==========================================
            # HERÓIS FOLCLÓRICOS E "BAGRES" (OVR 65-78)
            # ==========================================
            
            # Os Tanques (Físico Apelão)
            {"nome": "Walter", "clube": "Goiás", "pos": "ATA", "ovr": 76, "rit": 45, "fin": 82, "pas": 70, "dri": 75, "def": 30, "fis": 96, "img_url": ""},
            {"nome": "Souza Caveirão", "clube": "Flamengo", "pos": "ATA", "ovr": 74, "rit": 55, "fin": 78, "pas": 50, "dri": 60, "def": 35, "fis": 92, "img_url": ""},
            {"nome": "Sassá", "clube": "Cruzeiro", "pos": "ATA", "ovr": 73, "rit": 75, "fin": 74, "pas": 55, "dri": 65, "def": 40, "fis": 88, "img_url": ""},
            
            # Os Ligeirinhos (Ritmo Alto, Resto Baixo)
            {"nome": "Neto Berola", "clube": "Atlético Mineiro", "pos": "ATA", "ovr": 73, "rit": 94, "fin": 65, "pas": 55, "dri": 78, "def": 25, "fis": 40, "img_url": ""},
            {"nome": "Breno Lopes", "clube": "Palmeiras", "pos": "ATA", "ovr": 75, "rit": 86, "fin": 72, "pas": 65, "dri": 74, "def": 40, "fis": 70, "img_url": ""},
            {"nome": "Alef Manga", "clube": "Coritiba", "pos": "ATA", "ovr": 75, "rit": 85, "fin": 76, "pas": 60, "dri": 75, "def": 35, "fis": 78, "img_url": ""},

            # Os Volantes e Laterais "Raiz" (A base da porradaria)
            {"nome": "Márcio Araújo", "clube": "Flamengo", "pos": "VOL", "ovr": 71, "rit": 68, "fin": 30, "pas": 65, "dri": 55, "def": 78, "fis": 75, "img_url": ""},
            {"nome": "Pará", "clube": "Santos", "pos": "LAT", "ovr": 70, "rit": 72, "fin": 40, "pas": 62, "dri": 60, "def": 72, "fis": 70, "img_url": ""},
            {"nome": "Patric", "clube": "Atlético Mineiro", "pos": "LAT", "ovr": 73, "rit": 76, "fin": 55, "pas": 65, "dri": 68, "def": 70, "fis": 75, "img_url": ""},
            {"nome": "Rodinei", "clube": "Flamengo", "pos": "LAT", "ovr": 78, "rit": 88, "fin": 60, "pas": 75, "dri": 80, "def": 72, "fis": 84, "img_url": ""},
            
            # Ídolos Alternativos (Média Geral)
            {"nome": "Wellington Paulista", "clube": "Fortaleza", "pos": "ATA", "ovr": 76, "rit": 65, "fin": 82, "pas": 60, "dri": 65, "def": 40, "fis": 80, "img_url": ""},
            {"nome": "Magno Alves", "clube": "Ceará", "pos": "ATA", "ovr": 77, "rit": 60, "fin": 85, "pas": 70, "dri": 75, "def": 30, "fis": 65, "img_url": ""},
            {"nome": "Zé Love", "clube": "Santos", "pos": "ATA", "ovr": 72, "rit": 70, "fin": 75, "pas": 55, "dri": 65, "def": 35, "fis": 72, "img_url": ""},
            {"nome": "Tuta", "clube": "Fluminense", "pos": "ATA", "ovr": 74, "rit": 55, "fin": 78, "pas": 60, "dri": 62, "def": 40, "fis": 85, "img_url": ""},
            {"nome": "Kieza", "clube": "Bahia", "pos": "ATA", "ovr": 73, "rit": 78, "fin": 74, "pas": 60, "dri": 70, "def": 35, "fis": 72, "img_url": ""},
            {"nome": "Danilinho", "clube": "Atlético Mineiro", "pos": "MEI", "ovr": 75, "rit": 88, "fin": 65, "pas": 72, "dri": 82, "def": 40, "fis": 50, "img_url": ""},
            {"nome": "Carlos", "clube": "Atlético Mineiro", "pos": "ATA", "ovr": 68, "rit": 75, "fin": 66, "pas": 55, "dri": 68, "def": 30, "fis": 60, "img_url": ""},
            {"nome": "Erik", "clube": "Goiás", "pos": "ATA", "ovr": 74, "rit": 88, "fin": 72, "pas": 62, "dri": 75, "def": 35, "fis": 65, "img_url": ""},
            {"nome": "Rafael Moura", "clube": "Goiás", "pos": "ATA", "ovr": 75, "rit": 50, "fin": 78, "pas": 65, "dri": 65, "def": 45, "fis": 88, "img_url": ""},
            {"nome": "Iarley", "clube": "Goiás", "pos": "MEI", "ovr": 77, "rit": 65, "fin": 75, "pas": 80, "dri": 78, "def": 40, "fis": 70, "img_url": ""},
            
            # O Goleiro que sempre toma frango (Stats de defesa e reflexo baixos)
            {"nome": "Alex Muralha", "clube": "Flamengo", "pos": "GOL", "ovr": 70, "rit": 35, "fin": 10, "pas": 50, "dri": 30, "def": 72, "fis": 75, "img_url": ""},
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
