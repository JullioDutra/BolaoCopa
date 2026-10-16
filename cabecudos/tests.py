import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts import coins

from . import servico
from .fases import DURACAO_S, FASES
from .models import PartidaCabecudos


class CabecudosTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('cabecudo', password='x')
        self.client.force_login(self.user)

    def _post(self, nome, corpo):
        return self.client.post(reverse(f'cabecudos:{nome}'), json.dumps(corpo), content_type='application/json')

    def _iniciar(self, fase):
        r = self._post('api_iniciar', {'fase': fase})
        return r, r.json()

    def _envelhecer(self, token, segundos=DURACAO_S + 5):
        PartidaCabecudos.objects.filter(token=token).update(iniciada_em=timezone.now() - timedelta(seconds=segundos))

    def test_telas(self):
        self.assertEqual(self.client.get(reverse('cabecudos:hub')).status_code, 200)
        resp = self.client.get(reverse('cabecudos:jogar', args=[1]))
        self.assertContains(resp, 'id="cabecudos"')
        self.assertContains(resp, 'window.Cabecudos')
        self.assertEqual(self.client.get(reverse('cabecudos:jogar', args=[2])).status_code, 302)   # bloqueada

    def test_fase_bloqueada_nao_inicia(self):
        r, d = self._iniciar(2)
        self.assertEqual(r.status_code, 400)
        r, d = self._iniciar(1)
        self.assertTrue(d['ok'])
        self.assertEqual((d['nome'], d['duracao']), (FASES[0]['nome'], DURACAO_S))

    def test_resultado_rapido_demais_e_invalido(self):
        _, d = self._iniciar(1)
        r = self._post('api_finalizar', {'token': d['token'], 'gols_pro': 9, 'gols_contra': 0})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(PartidaCabecudos.objects.get(token=d['token']).status, 'invalida')
        self.assertEqual(servico.fase_liberada(self.user), 1)

    def test_vitoria_libera_fase_e_paga_uma_vez(self):
        _, d = self._iniciar(1)
        self._envelhecer(d['token'])
        saldo = coins.saldo(self.user)
        r = self._post('api_finalizar', {'token': d['token'], 'gols_pro': 3, 'gols_contra': 1}).json()
        self.assertEqual((r['status'], r['liberada']), ('vitoria', 2))
        self.assertGreater(coins.saldo(self.user), saldo)
        self.assertEqual(self._post('api_finalizar', {'token': d['token'], 'gols_pro': 3, 'gols_contra': 1}).status_code, 400)
        self.assertEqual(self.client.get(reverse('cabecudos:jogar', args=[2])).status_code, 200)

    def test_placar_absurdo_e_token_alheio(self):
        _, d = self._iniciar(1)
        self._envelhecer(d['token'])
        self.assertEqual(self._post('api_finalizar', {'token': d['token'], 'gols_pro': 99, 'gols_contra': 0}).status_code, 400)
        _, d2 = self._iniciar(1)
        self.client.force_login(User.objects.create_user('outro', password='x'))
        self.assertEqual(self._post('api_finalizar', {'token': d2['token'], 'gols_pro': 1, 'gols_contra': 0}).status_code, 400)
        self.assertEqual(self._post('api_finalizar', {'token': 'nao-e-uuid', 'gols_pro': 1, 'gols_contra': 0}).status_code, 400)

    def test_abandonar_conta_como_derrota(self):
        _, d = self._iniciar(1)
        self._iniciar(1)
        self.assertEqual(PartidaCabecudos.objects.get(token=d['token']).status, 'derrota')

    def test_campeao_desbloqueia_conquista(self):
        for fase in range(1, len(FASES) + 1):
            _, d = self._iniciar(fase)
            self._envelhecer(d['token'])
            r = self._post('api_finalizar', {'token': d['token'], 'gols_pro': 2, 'gols_contra': 0}).json()
            self.assertEqual(r['status'], 'vitoria')
        from avisos.models import Conquista
        self.assertTrue(Conquista.objects.filter(usuario=self.user, slug='cabecudo_rei').exists())
        self.assertContains(self.client.get(reverse('cabecudos:hub')), '🏆')
