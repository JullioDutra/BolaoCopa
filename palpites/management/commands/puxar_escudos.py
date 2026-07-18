"""
Busca o escudo de cada clube na Wikipedia e salva no campo `escudo` do model Clube.

Funciona no plano GRATUITO do PythonAnywhere porque *.wikipedia.org e
*.wikimedia.org estão na allowlist deles (https://www.pythonanywhere.com/whitelist/).
As imagens (thumbnails) da Wikipedia são servidas em upload.wikimedia.org,
que também está liberado.

Uso:
    python manage.py puxar_escudos

Roda quantas vezes quiser: só baixa o escudo de quem ainda não tem
(a menos que você use --forcar).
"""
import requests
from urllib.parse import urlparse
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from palpites.models import Clube


# Mapeia o nome salvo no banco -> título exato da página na Wikipedia,
# pra evitar cair em página de desambiguação (ex: "Santos" é cidade também).
PAGINAS_WIKIPEDIA = {
    # Brasileirão — pt.wikipedia.org
    "Atlético-MG": ("pt", "Clube Atlético Mineiro"),
    "Bahia": ("pt", "Esporte Clube Bahia"),
    "Botafogo": ("pt", "Botafogo de Futebol e Regatas"),
    "Bragantino": ("pt", "Red Bull Bragantino"),
    "Corinthians": ("pt", "Sport Club Corinthians Paulista"),
    "Cruzeiro": ("pt", "Cruzeiro Esporte Clube"),
    "Flamengo": ("pt", "Clube de Regatas do Flamengo"),
    "Fluminense": ("pt", "Fluminense Football Club"),
    "Grêmio": ("pt", "Grêmio Foot-Ball Porto Alegrense"),
    "Internacional": ("pt", "Sport Club Internacional"),
    "Mirassol": ("pt", "Mirassol Futebol Clube"),
    "Palmeiras": ("pt", "Sociedade Esportiva Palmeiras"),
    "Santos": ("pt", "Santos Futebol Clube"),
    "São Paulo": ("pt", "São Paulo Futebol Clube"),
    "Vasco": ("pt", "Club de Regatas Vasco da Gama"),
    "Vitória": ("pt", "Esporte Clube Vitória"),
    "Coritiba": ("pt", "Coritiba Foot Ball Club"),
    "Athletico-PR": ("pt", "Club Athletico Paranaense"),
    "Chapecoense": ("pt", "Associação Chapecoense de Futebol"),
    "Remo": ("pt", "Clube do Remo"),

    # Europa — en.wikipedia.org
    "Real Madrid": ("en", "Real Madrid CF"),
    "Barcelona": ("en", "FC Barcelona"),
    "Manchester City": ("en", "Manchester City F.C."),
    "Liverpool": ("en", "Liverpool F.C."),
    "Arsenal": ("en", "Arsenal F.C."),
    "Bayern de Munique": ("en", "FC Bayern Munich"),
    "Paris Saint-Germain": ("en", "Paris Saint-Germain F.C."),
    "Inter de Milão": ("en", "Inter Milan"),
    "Napoli": ("en", "SSC Napoli"),
    "Atlético de Madrid": ("en", "Atlético Madrid"),
    "Borussia Dortmund": ("en", "Borussia Dortmund"),
    "Chelsea": ("en", "Chelsea F.C."),
    "Juventus": ("en", "Juventus FC"),
    "AC Milan": ("en", "AC Milan"),
    "Manchester United": ("en", "Manchester United F.C."),
    "Benfica": ("en", "S.L. Benfica"),
    "Porto": ("en", "FC Porto"),
    "Newcastle United": ("en", "Newcastle United F.C."),
}

# A Wikimedia pede um User-Agent identificável. Troque o e-mail se quiser.
HEADERS = {
    "User-Agent": "CartolandiaBolao/1.0 (contato@cartolandia.exemplo.com)"
}


class Command(BaseCommand):
    help = "Baixa o escudo de cada clube na Wikipedia e salva no campo 'escudo'."

    def add_arguments(self, parser):
        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Baixa de novo mesmo para clubes que já têm escudo salvo.'
        )

    def buscar_url_imagem(self, idioma, titulo_pagina):
        url_api = f"https://{idioma}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": titulo_pagina,
            "prop": "pageimages",
            "piprop": "original",
            "format": "json",
        }
        resposta = requests.get(url_api, params=params, headers=HEADERS, timeout=15)
        resposta.raise_for_status()
        dados = resposta.json()

        paginas = dados.get("query", {}).get("pages", {})
        for pagina in paginas.values():
            original = pagina.get("original")
            if original and original.get("source"):
                return original["source"]
        return None

    def handle(self, *args, **options):
        forcar = options["forcar"]
        sucesso, falha, pulados = 0, 0, 0

        for clube in Clube.objects.all():
            if clube.escudo and not forcar:
                pulados += 1
                continue

            mapeamento = PAGINAS_WIKIPEDIA.get(clube.nome)
            if not mapeamento:
                self.stdout.write(self.style.WARNING(
                    f"⚠️  Sem mapeamento de Wikipedia pra '{clube.nome}', pulando."
                ))
                falha += 1
                continue

            idioma, titulo_pagina = mapeamento
            try:
                url_imagem = self.buscar_url_imagem(idioma, titulo_pagina)
                if not url_imagem:
                    self.stdout.write(self.style.WARNING(
                        f"⚠️  Não achei imagem pra '{clube.nome}' ({titulo_pagina})."
                    ))
                    falha += 1
                    continue

                resposta_imagem = requests.get(url_imagem, headers=HEADERS, timeout=20)
                resposta_imagem.raise_for_status()

                extensao = urlparse(url_imagem).path.split('.')[-1].lower()
                if extensao not in ('png', 'jpg', 'jpeg', 'svg', 'webp'):
                    extensao = 'png'
                nome_arquivo = f"{slugify(clube.nome)}.{extensao}"

                clube.escudo.save(nome_arquivo, ContentFile(resposta_imagem.content), save=True)

                self.stdout.write(self.style.SUCCESS(f"✅ {clube.nome} -> escudo salvo."))
                sucesso += 1

            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"❌ Erro em '{clube.nome}': {e}"))
                falha += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nConcluído: {sucesso} escudos baixados, {falha} falharam, {pulados} já tinham escudo."
        ))
