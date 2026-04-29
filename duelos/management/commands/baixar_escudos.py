import requests
import unicodedata
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from duelos.models import Clube

class Command(BaseCommand):
    help = 'Baixa os escudos de TODOS os clubes do sistema automaticamente'

    def normalizar_nome(self, nome):
        """Remove acentos, espaços e deixa tudo em minúsculas para a URL do site."""
        nome_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', nome) if unicodedata.category(c) != 'Mn')
        return nome_sem_acentos.lower().replace(' ', '-')

    def handle(self, *args, **kwargs):
        # Dicionário de resgate: Links diretos para os clubes que o logodetimes não tem
        urls_internacionais = {
            # GIGANTES EUROPEUS
            "Real Madrid": "https://upload.wikimedia.org/wikipedia/pt/9/98/Real_Madrid.png",
            "Barcelona": "https://upload.wikimedia.org/wikipedia/pt/4/43/FCBarcelona.svg",
            "Milan": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
            "Inter de Milão": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
            "Juventus": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Juventus_FC_2017_icon_%28black%29.svg",
            "Chelsea": "https://upload.wikimedia.org/wikipedia/pt/c/cc/Chelsea_FC.svg",
            "Manchester United": "https://upload.wikimedia.org/wikipedia/pt/4/43/Manchester_United_FC.svg",
            "Bayern de Munique": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg",
            "PSG": "https://upload.wikimedia.org/wikipedia/pt/a/a2/Paris_Saint-Germain_Football_Club.svg",
            "Arsenal": "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
            "Liverpool": "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
            "Manchester City": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
            "Tottenham": "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
            "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
            "Bayer Leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
            "Atlético de Madrid": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
            "Roma": "https://upload.wikimedia.org/wikipedia/en/f/f7/AS_Roma_logo_%282017%29.svg",
            "Napoli": "https://upload.wikimedia.org/wikipedia/commons/2/28/S.S.C._Napoli_logo.svg",
            "Lazio": "https://upload.wikimedia.org/wikipedia/en/e/e4/SS_Lazio.svg",
            "Fiorentina": "https://upload.wikimedia.org/wikipedia/en/b/ba/ACF_Fiorentina_2.svg",
            "Ajax": "https://upload.wikimedia.org/wikipedia/en/7/79/Ajax_Amsterdam.svg",
            "PSV": "https://upload.wikimedia.org/wikipedia/en/0/05/PSV_Eindhoven.svg",
            "Porto": "https://upload.wikimedia.org/wikipedia/pt/f/f1/FC_Porto.svg",
            "Benfica": "https://upload.wikimedia.org/wikipedia/en/a/a2/SL_Benfica_logo.svg",
            "Sporting": "https://upload.wikimedia.org/wikipedia/en/e/e2/Sporting_CP_logo.svg",

            # GIGANTES SUL-AMERICANOS E OUTROS
            "Boca Juniors": "https://upload.wikimedia.org/wikipedia/commons/8/83/Escudo_de_Boca_Juniors.svg",
            "River Plate": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Logo_River_Plate_2022.svg",
            "San Lorenzo": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Escudo_del_Club_Atl%C3%A9tico_San_Lorenzo_de_Almagro.svg",
            "Racing": "https://upload.wikimedia.org/wikipedia/commons/c/cc/Escudo_de_Racing_Club_%282014%29.svg",
            "Estudiantes": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Escudo_de_Estudiantes_de_La_Plata.svg",
            "Nacional": "https://upload.wikimedia.org/wikipedia/commons/0/07/Club_Nacional_de_Football_-_Uruguay.svg",
            "Colo-Colo": "https://upload.wikimedia.org/wikipedia/en/1/11/Colo-Colo_logo.svg",
            "LDU": "https://upload.wikimedia.org/wikipedia/commons/3/30/LDU_logo.svg",
            
            # EQUIPAS RARAS DA TRAJETÓRIA (Para não dar erro)
            "Galatasaray": "https://upload.wikimedia.org/wikipedia/commons/f/f6/Galatasaray_Sports_Club_Logo.png",
            "Fenerbahçe": "https://upload.wikimedia.org/wikipedia/en/3/39/Fenerbah%C3%A7e.svg",
            "Besiktas": "https://upload.wikimedia.org/wikipedia/commons/a/ae/Be%C5%9Fikta%C5%9F_logo.svg",
            "Zenit": "https://upload.wikimedia.org/wikipedia/en/0/00/FC_Zenit_1_star_2015_logo.png",
            "LA Galaxy": "https://upload.wikimedia.org/wikipedia/en/6/62/LA_Galaxy_logo_%282024%29.svg",
            "Orlando City": "https://upload.wikimedia.org/wikipedia/en/2/23/Orlando_City_SC_%282014%29.svg",
            "Kashima Antlers": "https://upload.wikimedia.org/wikipedia/en/c/cb/Kashima_Antlers_logo.svg"
        }

        clubes = Clube.objects.all()
        total_clubes = clubes.count()
        
        self.stdout.write(self.style.WARNING(f"\nIniciando a verificação e download para TODOS os {total_clubes} clubes cadastrados..."))
        
        sucessos = 0
        falhas = 0

        for clube in clubes:
            # 1. Ignora se o clube já tiver um escudo carregado
            if clube.escudo:
                continue

            url = None
            origem = "Logodetimes"

            # 2. Verifica primeiro se está no nosso dicionário de resgate (Europeus/Raros)
            if clube.nome in urls_internacionais:
                url = urls_internacionais[clube.nome]
                origem = "Wikipedia"
            else:
                # 3. Se não estiver, assume que é Brasileiro e tenta o gerador automático
                slug = self.normalizar_nome(clube.nome)
                url = f"https://logodetimes.com/times/{slug}/logo-{slug}-256.png"

            # 4. Faz o download
            try:
                # Finge ser um navegador para a Wikipedia não bloquear o download
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                resposta = requests.get(url, stream=True, headers=headers)
                
                if resposta.status_code == 200:
                    extensao = 'svg' if '.svg' in url else 'png'
                    nome_arquivo = f"{self.normalizar_nome(clube.nome)}.{extensao}"
                    
                    clube.escudo.save(nome_arquivo, ContentFile(resposta.content), save=True)
                    self.stdout.write(self.style.SUCCESS(f'[+] {clube.nome} baixado com sucesso! ({origem})'))
                    sucessos += 1
                else:
                    self.stdout.write(self.style.ERROR(f'[X] Falha no {clube.nome}: Escudo não encontrado online.'))
                    falhas += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'[X] Erro de rede ao baixar {clube.nome}'))
                falhas += 1

        self.stdout.write(self.style.WARNING(f"\nResumo: {sucessos} adicionados com sucesso | {falhas} falharam ou não foram encontrados."))
        self.stdout.write("Os que falharam (clubes muito desconhecidos) podem ser adicionados manualmente no /admin.")