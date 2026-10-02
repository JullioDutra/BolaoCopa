"""
Avisos automáticos (rode de hora em hora, ex.: PythonAnywhere → Tasks):

    python manage.py enviar_lembretes

  * Lembrete: jogos que começam em até 3h (palpites fecham 1h antes) → avisa quem ainda não palpitou.
  * Resultado: jogo finalizado → avisa cada palpiteiro de quantos pontos fez.
  * Rodada: bolão da rodada encerrado → avisa os inscritos.
Cada aviso tem uma chave única, então rodar várias vezes NÃO repete notificação.
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from avisos import servico
from palpites.models import InscricaoRodada, Jogo, Palpite, RodadaBolao


class Command(BaseCommand):
    help = "Envia lembretes de palpite e avisos de resultado (idempotente)."

    def handle(self, *args, **opts):
        agora = timezone.now()
        enviados = {'lembrete': 0, 'resultado': 0, 'rodada': 0}
        ativos = list(User.objects.filter(is_active=True))
        url_jogos = reverse('palpites:listar_jogos')

        for jogo in Jogo.objects.filter(finalizado=False, data_hora__gt=agora, data_hora__lte=agora + timedelta(hours=3)):
            if not jogo.aceita_palpite:
                continue
            com = set(Palpite.objects.filter(jogo=jogo).values_list('usuario_id', flat=True))
            falta = jogo.data_hora - timedelta(hours=1) - agora
            minutos = max(int(falta.total_seconds() // 60), 1)
            for u in ativos:
                if u.id in com:
                    continue
                if servico.notificar(u, f"⏰ Falta palpitar: {jogo.time_casa} x {jogo.time_fora}",
                                     f"Os palpites fecham em ~{minutos} min. Bora cravar!", reverse('palpites:fazer_palpite', args=[jogo.id]),
                                     tipo='lembrete', chave=f'lembrete:{jogo.id}'):
                    enviados['lembrete'] += 1

        for jogo in Jogo.objects.filter(finalizado=True, data_hora__gte=agora - timedelta(days=2)):
            for p in Palpite.objects.filter(jogo=jogo).select_related('usuario'):
                if p.pontuacao_obtida == 15:
                    titulo, texto = "🎯 CRAVOU!", f"{jogo.time_casa} {jogo.gols_casa_real} x {jogo.gols_fora_real} {jogo.time_fora}: placar exato, +15 pts e 🪙 50!"
                elif p.pontuacao_obtida:
                    titulo, texto = "✅ Acertou o vencedor", f"{jogo.time_casa} {jogo.gols_casa_real} x {jogo.gols_fora_real} {jogo.time_fora}: +{p.pontuacao_obtida} pts."
                else:
                    titulo, texto = "😬 Dessa vez não deu", f"{jogo.time_casa} {jogo.gols_casa_real} x {jogo.gols_fora_real} {jogo.time_fora}. Bora pro próximo!"
                if servico.notificar(p.usuario, titulo, texto, url_jogos, tipo='resultado', chave=f'resultado:{jogo.id}'):
                    enviados['resultado'] += 1

        for rodada in RodadaBolao.objects.filter(premio_distribuido=True, jogos__data_hora__gte=agora - timedelta(days=3)).distinct():
            for insc in InscricaoRodada.objects.filter(rodada=rodada).select_related('usuario'):
                if servico.notificar(insc.usuario, f"🏁 {rodada.nome} encerrado", "Veja a classificação final e quem levou o pote.",
                                     reverse('palpites:ranking_rodada', args=[rodada.id]), tipo='rodada', chave=f'rodada:{rodada.id}'):
                    enviados['rodada'] += 1

        self.stdout.write(self.style.SUCCESS(f"Avisos enviados: {enviados}"))
