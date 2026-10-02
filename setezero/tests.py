import json
import statistics

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from accounts import coins

from . import dados, engine, servico
from .models import Partida7a0, Temporada7a0


class DadosTests(SimpleTestCase):
    def test_times_historicos_completos(self):
        self.assertGreaterEqual(len(dados.TIMES), 16)
        for t in list(dados.TIMES.values()) + dados.fregueses():
            self.assertGreaterEqual(len(t['elenco']), 14, t['nome'])
            for formacao in dados.FORMACOES:
                xi = dados.escalar(t, formacao)
                self.assertEqual(len({j['nome'] for j in xi}), 11)
                self.assertEqual(xi[0]['pos'], 'GOL')

    def test_escalacao_manual_valida_e_invalida(self):
        t = dados.obter('fla-2019')
        base = dados.titulares_padrao(t, '4-3-3')
        trocado = base[:10] + ['Thuler']
        self.assertEqual([j['nome'] for j in dados.escalar(t, '4-3-3', trocado)][-1], 'Thuler')
        self.assertEqual([j['nome'] for j in dados.escalar(t, '4-3-3', ['Fulano'] * 11)], base)

    def test_fregueses_sao_mais_fracos(self):
        melhor_fregues = max(f['overall'] for f in dados.fregueses())
        pior_historico = min(t['overall'] for t in dados.TIMES.values())
        self.assertLess(melhor_fregues + 5, pior_historico)


class MotorTests(SimpleTestCase):
    def jogo(self, a, b, seed, **kw):
        e = engine.novo_estado({'time': a, **kw.get('casa', {})}, {'time': b, **kw.get('fora', {})}, seed)
        return engine.simular_completo(e)

    def test_deterministico_e_termina(self):
        a = self.jogo('fla-2019', 'pal-2021', 7)
        b = self.jogo('fla-2019', 'pal-2021', 7)
        self.assertEqual(a['placar'], b['placar'])
        self.assertEqual(a['eventos'], b['eventos'])
        self.assertEqual(a['status'], 'fim')
        self.assertEqual(a['eventos'][-1]['tipo'], 'fim')
        self.assertIn('intervalo', {e['tipo'] for e in a['eventos']})

    def test_media_de_gols_realista(self):
        gols = []
        keys = list(dados.TIMES)
        for i in range(120):
            e = self.jogo(keys[i % 16], keys[(i * 5 + 3) % 16] if keys[(i * 5 + 3) % 16] != keys[i % 16] else keys[(i + 1) % 16], i)
            gols += [e['placar']['casa'], e['placar']['fora']]
        self.assertTrue(0.9 < statistics.mean(gols) < 1.8, statistics.mean(gols))

    def test_gols_batem_com_eventos_e_estatisticas(self):
        e = self.jogo('cru-2003', 'varzea-fc', 3)
        self.assertEqual(sum(1 for x in e['eventos'] if x['tipo'] == 'gol' and x['lado'] == 'casa'), e['placar']['casa'])
        r = engine.resumo(e)
        self.assertAlmostEqual(r['stats']['casa']['posse'] + r['stats']['fora']['posse'], 100, delta=1)
        self.assertGreaterEqual(e['stats']['casa']['chutes'], e['stats']['casa']['no_alvo'])

    def test_time_forte_vence_freguês_quase_sempre(self):
        vitorias = sum(1 for i in range(60) if (lambda e: e['placar']['casa'] > e['placar']['fora'])(self.jogo('fla-2019', 'varzea-fc', i)))
        self.assertGreater(vitorias, 45)

    def test_substituicao_e_limite(self):
        e = engine.novo_estado({'time': 'fla-2019'}, {'time': 'pal-2021'}, 1, usuario_lado='casa')
        engine.avancar(e, 30)
        titular = e['lados']['casa']['titulares'][5]
        ok, _ = engine.aplicar_ajuste(e, 'casa', {'sai': titular, 'entra': e['lados']['casa']['banco'][0]})
        self.assertTrue(ok)
        self.assertNotIn(titular, e['lados']['casa']['titulares'])
        self.assertEqual(e['lados']['casa']['subs'], 1)
        ok, msg = engine.aplicar_ajuste(e, 'casa', {'sai': 'Ninguém', 'entra': 'x'})
        self.assertFalse(ok)

    def test_mentalidade_muda_o_jogo(self):
        def media(m):
            gols = 0
            for i in range(80):
                e = engine.novo_estado({'time': 'fla-2019', 'mentalidade': m}, {'time': 'varzea-fc', 'mentalidade': 'equilibrado'}, i)
                engine.simular_completo(e)
                gols += e['placar']['casa']
            return gols / 80
        self.assertGreater(media('tudo'), media('retranca'))

    def test_avancar_pausa_no_intervalo_e_retoma(self):
        e = engine.novo_estado({'time': 'fla-2019'}, {'time': 'pal-2021'}, 5)
        engine.avancar(e, 'fim')
        self.assertEqual(e['status'], 'intervalo')
        engine.avancar(e, 'fim')
        self.assertEqual(e['status'], 'fim')
        self.assertEqual(engine.avancar(e, 'fim'), [])


class FluxoTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('tec', password='x', first_name='Tec')
        self.client.force_login(self.u)

    def test_paginas_abrem(self):
        for nome, args in (('hub', []), ('ranking', []), ('novo', ['amistoso']), ('novo', ['desafio']), ('novo', ['temporada'])):
            self.assertEqual(self.client.get(reverse(f'setezero:{nome}', args=args)).status_code, 200, nome)

    def test_criar_e_jogar_pela_api(self):
        r = self.client.post(reverse('setezero:novo', args=['amistoso']), {'time': 'fla-2019', 'rival': 'pal-2021', 'formacao': '4-4-2', 'mentalidade': 'ofensivo', 'estilo': 'pressao'})
        p = Partida7a0.objects.get()
        self.assertRedirects(r, reverse('setezero:partida', args=[p.pk]))
        self.assertEqual(self.client.get(reverse('setezero:partida', args=[p.pk])).status_code, 200)
        url = reverse('setezero:api_avancar', args=[p.pk])
        j = self.client.post(url, json.dumps({'ate': 'intervalo', 'desde': 0}), content_type='application/json').json()
        self.assertEqual(j['visao']['status'], 'intervalo')
        self.assertTrue(j['eventos'])
        j = self.client.post(url, json.dumps({'ajuste': {'mentalidade': 'retranca'}, 'desde': len(j['eventos'])}), content_type='application/json').json()
        self.assertEqual(j['visao']['lados']['casa']['mentalidade'], 'retranca')
        j = self.client.post(url, json.dumps({'ate': 'fim', 'desde': 0}), content_type='application/json').json()
        self.assertEqual(j['visao']['status'], 'fim')
        p.refresh_from_db()
        self.assertIn(p.resultado, 'VED')
        self.assertIsNotNone(p.finalizado_em)

    def test_premio_e_idempotencia(self):
        p = servico.criar_partida(self.u, 'desafio', 'fla-2019', 'varzea-fc', mentalidade='tudo')
        for _ in range(3):
            servico.avancar(p, 'fim')
            p.refresh_from_db()
        antes = coins.saldo(self.u)
        servico.finalizar(p)
        self.assertEqual(coins.saldo(self.u), antes)  # já premiado uma vez
        self.assertEqual(p.status, 'fim')

    def test_prêmio_de_sete_a_zero(self):
        p = servico.criar_partida(self.u, 'amistoso', 'fla-2019', 'pal-2021')
        p.estado['placar'] = {'casa': 7, 'fora': 0}
        p.estado['status'] = 'fim'
        servico._sync(p)
        p.save()
        saldo = coins.saldo(self.u)
        servico.finalizar(p)
        self.assertEqual(coins.saldo(self.u), saldo + servico.PREMIO_VITORIA + servico.PREMIO_GOLEADA + servico.PREMIO_SETE_A_ZERO + 3 * 25)  # + 3 conquistas
        from avisos.models import Conquista
        self.assertTrue(Conquista.objects.filter(usuario=self.u, slug='sete_a_zero').exists())

    def test_nao_acessa_partida_de_outro(self):
        outro = User.objects.create_user('outro', password='x')
        p = servico.criar_partida(outro, 'amistoso', 'fla-2019')
        self.assertEqual(self.client.get(reverse('setezero:partida', args=[p.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('setezero:api_avancar', args=[p.pk])).status_code, 404)

    def test_time_invalido_e_mesmo_time(self):
        with self.assertRaises(servico.ErroJogo):
            servico.criar_partida(self.u, 'amistoso', 'inexistente')
        with self.assertRaises(servico.ErroJogo):
            servico.criar_partida(self.u, 'amistoso', 'fla-2019', 'fla-2019')
        with self.assertRaises(servico.ErroJogo):
            servico.criar_partida(self.u, 'amistoso', 'varzea-fc')

    def test_temporada_completa(self):
        t = servico.criar_temporada(self.u, 'fla-2019')
        self.assertEqual(len(t.estado['calendario']), 14)
        # todos jogam contra todos, ida e volta
        pares = {tuple(sorted(j)) for r in t.estado['calendario'] for j in r}
        self.assertEqual(len(pares), 28)
        for _ in range(14):
            t.refresh_from_db()
            p = servico.partida_da_rodada(t)
            self.assertIsNotNone(p)
            while p.status != 'fim':
                servico.avancar(p, 'fim')
                p.refresh_from_db()
        t.refresh_from_db()
        self.assertEqual(t.status, 'finalizada')
        self.assertIn(t.posicao_final, range(1, 9))
        tabela = servico.tabela_ordenada(t)
        self.assertTrue(all(l['pj'] == 14 for l in tabela))
        self.assertEqual(sum(l['gp'] for l in tabela), sum(l['gc'] for l in tabela))
        self.assertIsNone(servico.partida_da_rodada(t))
        self.assertEqual(self.client.get(reverse('setezero:temporada', args=[t.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('setezero:ranking')).status_code, 200)
