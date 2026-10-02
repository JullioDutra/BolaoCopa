from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts import coins
from accounts.models import PerfilUsuario
from bolao.models import Participacao
from palpites.models import Clube, Jogo

from . import noticias

RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<item><title>Flamengo vence e assume a ponta - ge</title><link>https://ge.globo.com/futebol/noticia-1</link>
<pubDate>Tue, 01 Oct 2026 12:00:00 GMT</pubDate><source url="https://ge.globo.com">ge</source></item>
<item><title>Link perigoso</title><link>javascript:alert(1)</link></item>
<item><title>Sem fonte</title><link>https://exemplo.com/a</link></item>
</channel></rss>"""


class NoticiasTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_interpreta_rss_e_descarta_links_perigosos(self):
        itens = noticias.interpretar_rss(RSS)
        self.assertEqual([i['titulo'] for i in itens], ['Flamengo vence e assume a ponta', 'Sem fonte'])
        self.assertEqual(itens[0]['fonte'], 'ge')
        self.assertIn('2026-10-01', itens[0]['publicado_em'])

    def test_falha_de_rede_devolve_lista_vazia_e_nao_levanta(self):
        with mock.patch.object(noticias, '_baixar', side_effect=OSError('sem rede')):
            self.assertEqual(noticias.buscar_noticias('Flamengo'), [])

    def test_usa_cache_na_segunda_chamada(self):
        with mock.patch.object(noticias, '_baixar', return_value=RSS) as baixar:
            noticias.buscar_noticias('Flamengo')
            noticias.buscar_noticias('Flamengo')
        self.assertEqual(baixar.call_count, 1)

    def test_cai_para_cache_antigo_quando_a_fonte_falha(self):
        with mock.patch.object(noticias, '_baixar', return_value=RSS):
            noticias.buscar_noticias('Flamengo')
        cache.delete('noticias:flamengo')  # expirou o cache fresco, mas a cópia antiga continua
        with mock.patch.object(noticias, '_baixar', side_effect=OSError):
            self.assertEqual(len(noticias.buscar_noticias('Flamengo')), 2)


class DashboardTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user('craque', password='x', first_name='Craque')
        Participacao.objects.create(usuario=self.user, tipo='resenha')
        self.client.force_login(self.user)
        self.fla = Clube.objects.create(nome='Flamengo', cor_hexadecimal='#C8102E')

    def test_sem_time_mostra_convite_e_tema_padrao(self):
        r = self.client.get(reverse('dashboard'))
        self.assertContains(r, 'Qual é o seu time?')
        self.assertNotContains(r, 'id="tema-time"')

    def test_primeiro_acesso_do_dia_paga_bonus_so_uma_vez(self):
        self.client.get(reverse('dashboard'))
        self.client.get(reverse('dashboard'))
        self.assertEqual(coins.saldo(self.user), 1000 + 25)
        self.assertEqual(PerfilUsuario.objects.get(usuario=self.user).streak_dias, 1)

    def test_escolher_time_da_bonus_unico_e_aplica_tema(self):
        r = self.client.post(reverse('conta:escolher_time'), {'clube': self.fla.id, 'usar_tema_do_time': 'on'})
        self.assertEqual(r.status_code, 302)
        # +100 do bônus e +25 da conquista "Torcedor de Carteirinha"
        self.assertEqual(coins.saldo(self.user), 1000 + 100 + 25)
        self.client.post(reverse('conta:escolher_time'), {'clube': self.fla.id, 'usar_tema_do_time': 'on'})
        self.assertEqual(coins.saldo(self.user), 1125)  # bônus só na primeira escolha

        r = self.client.get(reverse('dashboard'))
        self.assertContains(r, 'Nação Rubro-Negra')
        self.assertContains(r, 'id="tema-time"')
        self.assertContains(r, '--verde-campo: #b3001b;')

    def test_desligar_tema_volta_ao_padrao(self):
        self.client.post(reverse('conta:escolher_time'), {'clube': self.fla.id, 'usar_tema_do_time': 'on'})
        self.client.post(reverse('conta:escolher_time'), {'clube': self.fla.id, 'usar_tema_do_time': 'off'})
        r = self.client.get(reverse('dashboard'))
        self.assertNotContains(r, 'id="tema-time"')
        self.assertNotContains(r, 'Nação Rubro-Negra')

    def test_feed_noticias_json(self):
        self.client.post(reverse('conta:escolher_time'), {'clube': self.fla.id})
        with mock.patch.object(noticias, '_baixar', return_value=RSS):
            dados = self.client.get(reverse('core:feed_noticias')).json()
        self.assertEqual(dados['time'], 'Flamengo')
        self.assertEqual(len(dados['noticias']), 2)

    def test_feed_noticias_sem_time(self):
        self.assertEqual(self.client.get(reverse('core:feed_noticias')).json(), {'time': None, 'noticias': []})

    @override_settings(FOOTBALL_DATA_TOKEN=None)
    def test_feed_tabela_sem_token_vem_vazio(self):
        self.assertEqual(self.client.get(reverse('core:feed_tabela')).json()['tabela'], [])

    def test_proximo_jogo_do_time_aparece_no_card(self):
        self.client.post(reverse('conta:escolher_time'), {'clube': self.fla.id})
        Jogo.objects.create(time_casa='Flamengo', time_fora='Santos', data_hora=timezone.now() + timedelta(days=1))
        self.assertContains(self.client.get(reverse('dashboard')), 'Flamengo x Santos')

    def test_paginas_de_conta(self):
        for nome in ('conta:escolher_time', 'conta:extrato_coins'):
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200, nome)
