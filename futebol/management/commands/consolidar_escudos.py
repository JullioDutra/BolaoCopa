"""
Junta TODOS os escudos do site (bolão, X1, draft, carreira, jogos) no catálogo global `futebol.Escudo`
e remove arquivos duplicados (mesmo conteúdo) para liberar espaço.

  python manage.py consolidar_escudos            # simulação: só mostra o que faria
  python manage.py consolidar_escudos --aplicar  # grava no catálogo e reaponta os campos para 1 arquivo só
"""
import hashlib
import os

from django.apps import apps
from django.core.management.base import BaseCommand

from futebol import escudos as catalogo
from futebol.models import Escudo, Time

# (app.Modelo, campo com o nome, campo de imagem)
FONTES = [
    ('palpites.Clube', 'nome', 'escudo'),
    ('duelos.Clube', 'nome', 'escudo'),
    ('modocarreira.Clube', 'nome', 'escudo'),
    ('draft.ClubeBrasileiro', 'nome', 'escudo'),
]


def _hash(campo):
    try:
        h = hashlib.md5()
        with campo.open('rb') as f:
            for bloco in iter(lambda: f.read(65536), b''):
                h.update(bloco)
        return h.hexdigest()
    except (OSError, ValueError):
        return None


class Command(BaseCommand):
    help = 'Consolida escudos num catálogo global e elimina duplicados.'

    def add_arguments(self, parser):
        parser.add_argument('--aplicar', action='store_true')

    def handle(self, *args, aplicar=False, **opts):
        novos = reaproveitados = liberados = 0
        vistos = {}  # md5 -> nome do arquivo canônico
        for e in Escudo.objects.exclude(arquivo='').exclude(arquivo__isnull=True):
            h = _hash(e.arquivo)
            if h:
                vistos.setdefault(h, e.arquivo.name)

        itens = []
        for rotulo, campo_nome, campo_img in FONTES:
            try:
                modelo = apps.get_model(rotulo)
            except LookupError:
                continue
            for obj in modelo.objects.all():
                itens.append((obj, getattr(obj, campo_nome), campo_img))

        for obj, nome, campo_img in itens:
            arquivo = getattr(obj, campo_img)
            if not arquivo:
                continue
            h = _hash(arquivo)
            if h is None:
                self.stdout.write(self.style.WARNING(f'  arquivo ausente: {nome} ({arquivo.name})'))
                continue
            canonico = vistos.get(h)
            if canonico is None:
                vistos[h] = arquivo.name
                canonico = arquivo.name
                novos += 1
            elif canonico != arquivo.name:
                reaproveitados += 1
                try:
                    liberados += arquivo.size
                except (OSError, ValueError):
                    pass
                self.stdout.write(f'  duplicado: {nome} -> {canonico}')
                if aplicar:
                    antigo = arquivo.path
                    setattr(obj, campo_img, canonico)
                    obj.save(update_fields=[campo_img])
                    if os.path.exists(antigo) and antigo != getattr(obj, campo_img).path:
                        os.remove(antigo)
            if aplicar:
                esc = catalogo.registrar(nome)
                if esc and not esc.arquivo:
                    esc.arquivo.name = canonico
                    esc.save()

        for t in Time.objects.exclude(escudo_url=''):
            if aplicar:
                catalogo.registrar(t.nome, url=t.escudo_url)
                if t.nome_curto:
                    catalogo.registrar(t.nome_curto, url=t.escudo_url)
        from palpites.models import Jogo
        for j in Jogo.objects.all():
            for nome, url in ((j.time_casa, j.escudo_casa_url), (j.time_fora, j.escudo_fora_url)):
                if aplicar and nome and url:
                    catalogo.registrar(nome, url=url)

        modo = 'APLICADO' if aplicar else 'SIMULAÇÃO (use --aplicar)'
        self.stdout.write(self.style.SUCCESS(
            f'{modo}: {novos} arquivos únicos, {reaproveitados} duplicados, '
            f'{liberados / 1024:.0f} KB liberados, catálogo com {Escudo.objects.count()} clubes.'))
