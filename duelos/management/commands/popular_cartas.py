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
                    # LENDAS INTERNACIONAIS
                    {"nome": "Messi", "clube": "Barcelona", "pos": "ATA", "ovr": 98, "rit": 85, "fin": 97, "pas": 98, "dri": 99, "def": 30, "fis": 65, "img_url": ""},
                    {"nome": "Cristiano Ronaldo", "clube": "Real Madrid", "pos": "ATA", "ovr": 98, "rit": 89, "fin": 99, "pas": 82, "dri": 88, "def": 35, "fis": 85, "img_url": ""},
                    {"nome": "Ronaldinho", "clube": "Barcelona", "pos": "MEI", "ovr": 94, "rit": 90, "fin": 88, "pas": 92, "dri": 98, "def": 30, "fis": 70, "img_url": ""},
                    {"nome": "Ronaldo Fenômeno", "clube": "Real Madrid", "pos": "ATA", "ovr": 96, "rit": 94, "fin": 98, "pas": 80, "dri": 95, "def": 30, "fis": 80, "img_url": ""},
                    {"nome": "Kaká", "clube": "Milan", "pos": "MEI", "ovr": 92, "rit": 92, "fin": 86, "pas": 88, "dri": 90, "def": 40, "fis": 75, "img_url": ""},
                    {"nome": "Maldini", "clube": "Milan", "pos": "ZAG", "ovr": 94, "rit": 80, "fin": 40, "pas": 75, "dri": 65, "def": 98, "fis": 85, "img_url": ""},
                    {"nome": "Roberto Carlos", "clube": "Real Madrid", "pos": "LAT", "ovr": 91, "rit": 92, "fin": 85, "pas": 80, "dri": 82, "def": 85, "fis": 90, "img_url": ""},
                    {"nome": "Zidane", "clube": "Real Madrid", "pos": "MEI", "ovr": 96, "rit": 75, "fin": 85, "pas": 98, "dri": 95, "def": 60, "fis": 85, "img_url": ""},
                    
                    # CRAQUES ATUAIS
                    {"nome": "Vini Jr", "clube": "Real Madrid", "pos": "ATA", "ovr": 90, "rit": 95, "fin": 86, "pas": 82, "dri": 94, "def": 35, "fis": 70, "img_url": ""},
                    {"nome": "Mbappé", "clube": "Real Madrid", "pos": "ATA", "ovr": 92, "rit": 97, "fin": 90, "pas": 80, "dri": 93, "def": 38, "fis": 78, "img_url": ""},
                    {"nome": "Haaland", "clube": "Manchester City", "pos": "ATA", "ovr": 91, "rit": 89, "fin": 94, "pas": 65, "dri": 80, "def": 45, "fis": 92, "img_url": ""},
                    {"nome": "De Bruyne", "clube": "Manchester City", "pos": "MEI", "ovr": 91, "rit": 74, "fin": 85, "pas": 95, "dri": 88, "def": 65, "fis": 78, "img_url": ""},
                    {"nome": "Alisson", "clube": "Liverpool", "pos": "GOL", "ovr": 89, "rit": 50, "fin": 20, "pas": 85, "dri": 45, "def": 90, "fis": 80, "img_url": ""},
                    {"nome": "Van Dijk", "clube": "Liverpool", "pos": "ZAG", "ovr": 90, "rit": 78, "fin": 50, "pas": 75, "dri": 70, "def": 92, "fis": 88, "img_url": ""},
                    
                    # BRASILEIRÃO (HISTÓRICO E ATUAL)
                    {"nome": "D'Alessandro", "clube": "Internacional", "pos": "MEI", "ovr": 86, "rit": 70, "fin": 78, "pas": 89, "dri": 85, "def": 45, "fis": 65, "img_url": ""},
                    {"nome": "Renato Gaúcho", "clube": "Grêmio", "pos": "ATA", "ovr": 88, "rit": 85, "fin": 86, "pas": 80, "dri": 90, "def": 30, "fis": 78, "img_url": ""},
                    {"nome": "Cássio", "clube": "Corinthians", "pos": "GOL", "ovr": 84, "rit": 40, "fin": 15, "pas": 55, "dri": 40, "def": 86, "fis": 88, "img_url": ""},
                    {"nome": "Dudu", "clube": "Palmeiras", "pos": "ATA", "ovr": 83, "rit": 86, "fin": 78, "pas": 82, "dri": 88, "def": 40, "fis": 68, "img_url": ""},
                    {"nome": "Hulk", "clube": "Atlético Mineiro", "pos": "ATA", "ovr": 85, "rit": 80, "fin": 88, "pas": 78, "dri": 82, "def": 45, "fis": 95, "img_url": ""},
                    {"nome": "Cano", "clube": "Fluminense", "pos": "ATA", "ovr": 84, "rit": 75, "fin": 90, "pas": 65, "dri": 75, "def": 35, "fis": 75, "img_url": ""},
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