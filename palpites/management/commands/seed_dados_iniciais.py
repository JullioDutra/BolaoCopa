"""
Comando para popular os dados iniciais do modo Campeão/G4/Z4/Europa/CDB.

Uso:
    python manage.py seed_dados_iniciais

Pode rodar quantas vezes quiser: usa get_or_create, então não duplica nem
sobrescreve escudos que você já tiver subido manualmente pelo Admin.
"""
from django.core.management.base import BaseCommand
from palpites.models import Clube, Temporada


# 20 clubes confirmados no Brasileirão Série A 2026
# (16 que permaneceram da Série A 2025 + 4 que subiram da Série B 2025:
#  Coritiba, Athletico-PR, Chapecoense e Remo)
CLUBES_BRASILEIRAO = [
    ("Atlético-MG", "#000000"),
    ("Bahia", "#1560BD"),
    ("Botafogo", "#000000"),
    ("Bragantino", "#E4002B"),
    ("Corinthians", "#000000"),
    ("Cruzeiro", "#003DA5"),
    ("Flamengo", "#C8102E"),
    ("Fluminense", "#9A1030"),
    ("Grêmio", "#0D80C4"),
    ("Internacional", "#E2231A"),
    ("Mirassol", "#FFD400"),
    ("Palmeiras", "#006437"),
    ("Santos", "#000000"),
    ("São Paulo", "#E4002B"),
    ("Vasco", "#1B1B1B"),
    ("Vitória", "#B22222"),
    ("Coritiba", "#00612B"),
    ("Athletico-PR", "#B01F24"),
    ("Chapecoense", "#00A651"),
    ("Remo", "#002B7F"),
]

# Principais candidatos ao título europeu (Champions League) — usado só
# como pool de opções pro campo "Campeão Europeu". Ajuste à vontade no Admin.
CLUBES_EUROPA = [
    ("Real Madrid", "#1B398E"),
    ("Barcelona", "#A50044"),
    ("Manchester City", "#6CABDD"),
    ("Liverpool", "#C8102E"),
    ("Arsenal", "#EF0107"),
    ("Bayern de Munique", "#DC052D"),
    ("Paris Saint-Germain", "#004170"),
    ("Inter de Milão", "#0F3B82"),
    ("Napoli", "#12A0D7"),
    ("Atlético de Madrid", "#CB3524"),
    ("Borussia Dortmund", "#FDE100"),
    ("Chelsea", "#034694"),
    ("Juventus", "#000000"),
    ("AC Milan", "#FB090B"),
    ("Manchester United", "#DA291C"),
    ("Benfica", "#E30613"),
    ("Porto", "#003399"),
    ("Newcastle United", "#241F20"),
]

# Temporada ativa que será criada/ativada
ANO_TEMPORADA_ATIVA = 2026


class Command(BaseCommand):
    help = "Popula os clubes do Brasileirão 2026 + candidatos europeus e cria a temporada ativa."

    def handle(self, *args, **options):
        criados_br = 0
        for nome, cor in CLUBES_BRASILEIRAO:
            obj, created = Clube.objects.get_or_create(
                nome=nome,
                defaults={'cor_hexadecimal': cor, 'competicao': 'BRASILEIRAO'}
            )
            if created:
                criados_br += 1
            elif obj.competicao != 'BRASILEIRAO':
                # Corrige a competição caso o clube já existisse sem essa marcação
                obj.competicao = 'BRASILEIRAO'
                obj.save(update_fields=['competicao'])

        criados_eu = 0
        for nome, cor in CLUBES_EUROPA:
            obj, created = Clube.objects.get_or_create(
                nome=nome,
                defaults={'cor_hexadecimal': cor, 'competicao': 'EUROPA'}
            )
            if created:
                criados_eu += 1
            elif obj.competicao != 'EUROPA':
                obj.competicao = 'EUROPA'
                obj.save(update_fields=['competicao'])

        temporada, temporada_criada = Temporada.objects.get_or_create(
            ano=ANO_TEMPORADA_ATIVA,
            defaults={'ativa': True}
        )
        if not temporada_criada and not temporada.ativa:
            temporada.ativa = True
            temporada.save(update_fields=['ativa'])

        self.stdout.write(self.style.SUCCESS(
            f"✅ {criados_br} clubes do Brasileirão criados (de {len(CLUBES_BRASILEIRAO)} no total)."
        ))
        self.stdout.write(self.style.SUCCESS(
            f"✅ {criados_eu} clubes da Europa criados (de {len(CLUBES_EUROPA)} no total)."
        ))
        self.stdout.write(self.style.SUCCESS(
            f"✅ Temporada {temporada.ano} está ativa."
        ))
        self.stdout.write(self.style.WARNING(
            "⚠️  Os escudos (campo 'escudo') não foram preenchidos — suba as imagens pelo Admin em Clubes."
        ))
