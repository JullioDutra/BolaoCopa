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
                    # DEUSES DO FUTEBOL (OVR 95+)
                    # ==========================================
                    {"nome": "Pelé", "clube": "Santos", "pos": "ATA", "ovr": 99, "rit": 95, "fin": 98, "pas": 93, "dri": 96, "def": 50, "fis": 85, "img_url": ""},
                    {"nome": "Maradona", "clube": "Napoli", "pos": "MEI", "ovr": 97, "rit": 88, "fin": 91, "pas": 95, "dri": 98, "def": 40, "fis": 75, "img_url": ""},
                    {"nome": "Messi", "clube": "Barcelona", "pos": "ATA", "ovr": 98, "rit": 85, "fin": 97, "pas": 98, "dri": 99, "def": 30, "fis": 65, "img_url": ""},
                    {"nome": "Cristiano Ronaldo", "clube": "Real Madrid", "pos": "ATA", "ovr": 98, "rit": 89, "fin": 99, "pas": 82, "dri": 88, "def": 35, "fis": 85, "img_url": ""},
                    {"nome": "Ronaldo Fenômeno", "clube": "Real Madrid", "pos": "ATA", "ovr": 96, "rit": 94, "fin": 98, "pas": 80, "dri": 95, "def": 30, "fis": 80, "img_url": ""},
                    {"nome": "Zico", "clube": "Flamengo", "pos": "MEI", "ovr": 96, "rit": 82, "fin": 94, "pas": 96, "dri": 93, "def": 45, "fis": 75, "img_url": ""},
                    {"nome": "Beckenbauer", "clube": "Bayern de Munique", "pos": "ZAG", "ovr": 95, "rit": 78, "fin": 75, "pas": 88, "dri": 82, "def": 96, "fis": 85, "img_url": ""},
        
                    # ==========================================
                    # LENDAS INTERNACIONAIS & BRASILEIRAS (OVR 88-94)
                    # ==========================================
                    {"nome": "Ronaldinho", "clube": "Barcelona", "pos": "MEI", "ovr": 94, "rit": 90, "fin": 88, "pas": 92, "dri": 98, "def": 30, "fis": 70, "img_url": ""},
                    {"nome": "Romário", "clube": "Vasco da Gama", "pos": "ATA", "ovr": 94, "rit": 88, "fin": 98, "pas": 78, "dri": 92, "def": 25, "fis": 70, "img_url": ""},
                    {"nome": "Zidane", "clube": "Real Madrid", "pos": "MEI", "ovr": 96, "rit": 75, "fin": 85, "pas": 98, "dri": 95, "def": 60, "fis": 85, "img_url": ""},
                    {"nome": "Maldini", "clube": "Milan", "pos": "ZAG", "ovr": 94, "rit": 80, "fin": 40, "pas": 75, "dri": 65, "def": 98, "fis": 85, "img_url": ""},
                    {"nome": "Roberto Carlos", "clube": "Real Madrid", "pos": "LAT", "ovr": 91, "rit": 92, "fin": 85, "pas": 80, "dri": 82, "def": 85, "fis": 90, "img_url": ""},
                    {"nome": "Kaká", "clube": "Milan", "pos": "MEI", "ovr": 92, "rit": 92, "fin": 86, "pas": 88, "dri": 90, "def": 40, "fis": 75, "img_url": ""},
                    {"nome": "Sócrates", "clube": "Corinthians", "pos": "MEI", "ovr": 91, "rit": 75, "fin": 85, "pas": 94, "dri": 88, "def": 60, "fis": 80, "img_url": ""},
                    {"nome": "Reinaldo", "clube": "Atlético Mineiro", "pos": "ATA", "ovr": 90, "rit": 86, "fin": 95, "pas": 82, "dri": 92, "def": 30, "fis": 72, "img_url": ""},
                    {"nome": "Rogério Ceni", "clube": "São Paulo", "pos": "GOL", "ovr": 89, "rit": 40, "fin": 85, "pas": 90, "dri": 50, "def": 92, "fis": 80, "img_url": ""},
                    {"nome": "Marcos", "clube": "Palmeiras", "pos": "GOL", "ovr": 88, "rit": 45, "fin": 20, "pas": 60, "dri": 40, "def": 90, "fis": 85, "img_url": ""},
                    {"nome": "Victor", "clube": "Atlético Mineiro", "pos": "GOL", "ovr": 86, "rit": 40, "fin": 15, "pas": 55, "dri": 45, "def": 91, "fis": 82, "img_url": ""},
        
                    # ==========================================
                    # ESTRELAS ATUAIS (OVR 86-92)
                    # ==========================================
                    {"nome": "Vini Jr", "clube": "Real Madrid", "pos": "ATA", "ovr": 90, "rit": 95, "fin": 86, "pas": 82, "dri": 94, "def": 35, "fis": 70, "img_url": ""},
                    {"nome": "Mbappé", "clube": "Real Madrid", "pos": "ATA", "ovr": 92, "rit": 97, "fin": 90, "pas": 80, "dri": 93, "def": 38, "fis": 78, "img_url": ""},
                    {"nome": "Haaland", "clube": "Manchester City", "pos": "ATA", "ovr": 91, "rit": 89, "fin": 94, "pas": 65, "dri": 80, "def": 45, "fis": 92, "img_url": ""},
                    {"nome": "De Bruyne", "clube": "Manchester City", "pos": "MEI", "ovr": 91, "rit": 74, "fin": 85, "pas": 95, "dri": 88, "def": 65, "fis": 78, "img_url": ""},
                    {"nome": "Bellingham", "clube": "Real Madrid", "pos": "MEI", "ovr": 88, "rit": 82, "fin": 85, "pas": 86, "dri": 88, "def": 78, "fis": 85, "img_url": ""},
                    {"nome": "Van Dijk", "clube": "Liverpool", "pos": "ZAG", "ovr": 90, "rit": 78, "fin": 50, "pas": 75, "dri": 70, "def": 92, "fis": 88, "img_url": ""},
                    {"nome": "Alisson", "clube": "Liverpool", "pos": "GOL", "ovr": 89, "rit": 50, "fin": 20, "pas": 85, "dri": 45, "def": 90, "fis": 80, "img_url": ""},
        
                    # ==========================================
                    # CRAQUES DO BRASILEIRÃO (OVR 80-86)
                    # ==========================================
                    {"nome": "Hulk", "clube": "Atlético Mineiro", "pos": "ATA", "ovr": 86, "rit": 80, "fin": 88, "pas": 78, "dri": 82, "def": 45, "fis": 95, "img_url": ""},
                    {"nome": "Arrascaeta", "clube": "Flamengo", "pos": "MEI", "ovr": 84, "rit": 72, "fin": 78, "pas": 88, "dri": 85, "def": 40, "fis": 65, "img_url": ""},
                    {"nome": "Gabigol", "clube": "Flamengo", "pos": "ATA", "ovr": 84, "rit": 82, "fin": 88, "pas": 75, "dri": 80, "def": 35, "fis": 82, "img_url": ""},
                    {"nome": "Dudu", "clube": "Palmeiras", "pos": "ATA", "ovr": 83, "rit": 86, "fin": 78, "pas": 82, "dri": 88, "def": 40, "fis": 68, "img_url": ""},
                    {"nome": "Raphael Veiga", "clube": "Palmeiras", "pos": "MEI", "ovr": 83, "rit": 76, "fin": 84, "pas": 85, "dri": 82, "def": 55, "fis": 72, "img_url": ""},
                    {"nome": "Paulinho", "clube": "Atlético Mineiro", "pos": "ATA", "ovr": 82, "rit": 88, "fin": 82, "pas": 75, "dri": 84, "def": 40, "fis": 70, "img_url": ""},
                    {"nome": "Guilherme Arana", "clube": "Atlético Mineiro", "pos": "LAT", "ovr": 82, "rit": 85, "fin": 70, "pas": 80, "dri": 82, "def": 78, "fis": 75, "img_url": ""},
                    {"nome": "Calleri", "clube": "São Paulo", "pos": "ATA", "ovr": 82, "rit": 75, "fin": 84, "pas": 65, "dri": 76, "def": 40, "fis": 85, "img_url": ""},
                    {"nome": "Cano", "clube": "Fluminense", "pos": "ATA", "ovr": 84, "rit": 75, "fin": 90, "pas": 65, "dri": 75, "def": 35, "fis": 75, "img_url": ""},
                    {"nome": "Ganso", "clube": "Fluminense", "pos": "MEI", "ovr": 80, "rit": 40, "fin": 72, "pas": 92, "dri": 82, "def": 35, "fis": 60, "img_url": ""},
                    {"nome": "Cássio", "clube": "Corinthians", "pos": "GOL", "ovr": 83, "rit": 40, "fin": 15, "pas": 55, "dri": 40, "def": 86, "fis": 88, "img_url": ""},
                    {"nome": "Tadeu", "clube": "Goiás", "pos": "GOL", "ovr": 81, "rit": 45, "fin": 20, "pas": 60, "dri": 50, "def": 85, "fis": 75, "img_url": ""},
                    {"nome": "Diego Tardelli", "clube": "Atlético Mineiro", "pos": "ATA", "ovr": 83, "rit": 82, "fin": 86, "pas": 78, "dri": 84, "def": 35, "fis": 70, "img_url": ""},
        
                    # ==========================================
                    # HERÓIS, RAÇUDOS E FOLCLÓRICOS (OVR 68-79)
                    # (A Mágica do jogo: Cartas fracas com um status apelão!)
                    # ==========================================
                    {"nome": "Felipe Melo", "clube": "Fluminense", "pos": "ZAG", "ovr": 75, "rit": 40, "fin": 55, "pas": 75, "dri": 65, "def": 78, "fis": 94, "img_url": ""},
                    {"nome": "Apodi", "clube": "Goiás", "pos": "LAT", "ovr": 73, "rit": 96, "fin": 65, "pas": 60, "dri": 72, "def": 65, "fis": 75, "img_url": ""},
                    {"nome": "Deyverson", "clube": "Atlético Mineiro", "pos": "ATA", "ovr": 76, "rit": 70, "fin": 78, "pas": 65, "dri": 72, "def": 45, "fis": 85, "img_url": ""},
                    {"nome": "Harlei", "clube": "Goiás", "pos": "GOL", "ovr": 79, "rit": 40, "fin": 15, "pas": 50, "dri": 45, "def": 84, "fis": 75, "img_url": ""},
                    {"nome": "Paulo Baier", "clube": "Goiás", "pos": "MEI", "ovr": 79, "rit": 50, "fin": 82, "pas": 88, "dri": 75, "def": 45, "fis": 70, "img_url": ""},
                    {"nome": "Fernandão", "clube": "Goiás", "pos": "ATA", "ovr": 80, "rit": 65, "fin": 84, "pas": 75, "dri": 72, "def": 50, "fis": 88, "img_url": ""},
                    {"nome": "Ribamar", "clube": "Vasco da Gama", "pos": "ATA", "ovr": 68, "rit": 78, "fin": 60, "pas": 55, "dri": 62, "def": 30, "fis": 88, "img_url": ""},
                    {"nome": "Amaral", "clube": "Palmeiras", "pos": "VOL", "ovr": 74, "rit": 72, "fin": 40, "pas": 65, "dri": 60, "def": 82, "fis": 90, "img_url": ""},
                    {"nome": "Obina", "clube": "Flamengo", "pos": "ATA", "ovr": 75, "rit": 68, "fin": 80, "pas": 60, "dri": 72, "def": 35, "fis": 86, "img_url": ""},
                    {"nome": "Harry Maguire", "clube": "Manchester United", "pos": "ZAG", "ovr": 78, "rit": 48, "fin": 50, "pas": 65, "dri": 55, "def": 80, "fis": 88, "img_url": ""},
                    {"nome": "Luan", "clube": "Grêmio", "pos": "MEI", "ovr": 72, "rit": 65, "fin": 68, "pas": 72, "dri": 74, "def": 35, "fis": 55, "img_url": ""},
                    {"nome": "Michael", "clube": "Goiás", "pos": "ATA", "ovr": 78, "rit": 92, "fin": 75, "pas": 70, "dri": 88, "def": 35, "fis": 60, "img_url": ""},
                    {"nome": "Yuri Alberto", "clube": "Corinthians", "pos": "ATA", "ovr": 76, "rit": 84, "fin": 72, "pas": 65, "dri": 75, "def": 35, "fis": 78, "img_url": ""},
                    {"nome": "Romero", "clube": "Corinthians", "pos": "ATA", "ovr": 76, "rit": 78, "fin": 72, "pas": 68, "dri": 76, "def": 60, "fis": 75, "img_url": ""},
                    {"nome": "Marinho", "clube": "Fortaleza", "pos": "ATA", "ovr": 78, "rit": 86, "fin": 82, "pas": 72, "dri": 80, "def": 40, "fis": 75, "img_url": ""},
                    {"nome": "Alecsandro", "clube": "Vasco da Gama", "pos": "ATA", "ovr": 75, "rit": 60, "fin": 82, "pas": 65, "dri": 68, "def": 35, "fis": 84, "img_url": ""},
                    {"nome": "Rony", "clube": "Palmeiras", "pos": "ATA", "ovr": 80, "rit": 92, "fin": 75, "pas": 70, "dri": 78, "def": 45, "fis": 80, "img_url": ""},
                    {"nome": "Perdigão", "clube": "Internacional", "pos": "VOL", "ovr": 70, "rit": 55, "fin": 45, "pas": 75, "dri": 65, "def": 70, "fis": 72, "img_url": ""},
                    {"nome": "Fagner", "clube": "Corinthians", "pos": "LAT", "ovr": 79, "rit": 76, "fin": 55, "pas": 78, "dri": 75, "def": 78, "fis": 82, "img_url": ""},
                    {"nome": "Léo Silva", "clube": "Atlético Mineiro", "pos": "ZAG", "ovr": 80, "rit": 55, "fin": 65, "pas": 60, "dri": 50, "def": 84, "fis": 88, "img_url": ""},
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
