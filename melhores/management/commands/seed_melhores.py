"""
Cria (ou atualiza) a edição dos Melhores do Ano com as categorias e candidatos
baseados no histórico de 2025 e 2021.

Uso:
    python manage.py seed_melhores              # edição do ano atual
    python manage.py seed_melhores --ano 2026
    python manage.py seed_melhores --incluir-2021   # inclui também quem só participou de 2021

Pode rodar várias vezes: atualiza categorias/votos, mas NUNCA mexe nas apostas.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from melhores.dados_historicos import CATEGORIAS, PARTICIPANTES_2025, PARTICIPANTES_SO_2021
from melhores.models import Candidato, Categoria, Edicao


class Command(BaseCommand):
    help = "Popula a edição dos Melhores do Ano com as odds baseadas no histórico."

    def add_arguments(self, parser):
        parser.add_argument('--ano', type=int, default=timezone.localdate().year)
        parser.add_argument('--incluir-2021', action='store_true',
                            help="Inclui como candidatos quem só participou do Troféu 2021.")

    def handle(self, *args, **opts):
        edicao, criada = Edicao.objects.get_or_create(
            ano=opts['ano'], defaults={'titulo': 'Melhores do Ano'},
        )
        self.stdout.write(f"{'Criada' if criada else 'Atualizando'} a edição {edicao.ano}")

        participantes = list(PARTICIPANTES_2025)
        if opts['incluir_2021']:
            participantes += PARTICIPANTES_SO_2021

        total_candidatos = 0
        for ordem, (slug, nome, emoji, tipo, descricao, candidatos) in enumerate(CATEGORIAS, start=1):
            categoria, _ = Categoria.objects.update_or_create(
                edicao=edicao, slug=slug,
                defaults={'nome': nome, 'emoji': emoji, 'tipo': tipo, 'descricao': descricao, 'ordem': ordem},
            )
            for nome_candidato, (votos_25, votos_21) in candidatos.items():
                Candidato.objects.update_or_create(
                    categoria=categoria, nome=nome_candidato, texto='',
                    defaults={'votos_ano_anterior': votos_25, 'votos_anos_anteriores': votos_21},
                )
                total_candidatos += 1

            # Todos os participantes entram (sem votos = azarão); não sobrescreve quem já tem histórico
            if tipo in ('pessoa', 'autor'):
                for nome_participante in participantes:
                    _, criado = Candidato.objects.get_or_create(
                        categoria=categoria, nome=nome_participante, texto='',
                    )
                    total_candidatos += criado

        self.stdout.write(self.style.SUCCESS(
            f"{len(CATEGORIAS)} categorias e {total_candidatos} candidatos prontos."
        ))
