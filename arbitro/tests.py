import json
import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts import coins

from . import engine, historicos, servico
from .base import AREA_X, LIMITE_LINHA_CM
from .models import PartidaArbitro


def _resposta_certa(lance):
    return dict(lance['correta'])


def _resposta_errada(lance):
    resp = {}
    for g in lance['grupos']:
        resp[g['id']] = next(o[0] for o in g['opcoes'] if o[0] != lance['correta'][g['id']])
    return resp


class HistoricosTests(SimpleTestCase):
    def test_lances_reais_completos_e_coerentes(self):
        lances = historicos.todos()
        self.assertGreaterEqual(len(lances), 15)
        self.assertEqual(len({l['chave'] for l in lances}), len(lances))
        for l in lances:
            self.assertIn(l['categoria'], engine.CATEGORIAS)
            self.assertTrue(l['explicacao'] and l['contexto'] and l['titulo'])
            for g in l['grupos']:
                self.assertIn(l['correta'][g['id']], [o[0] for o in g['opcoes']], l['chave'])

    def test_linha_dos_historicos_bate_com_a_regra(self):
        por_chave = {l['chave']: l for l in historicos.todos()}
        self.assertGreater(por_chave['lampard-2010']['cena']['c'], LIMITE_LINHA_CM)
        self.assertLess(por_chave['hurst-1966']['cena']['c'], LIMITE_LINHA_CM)
        self.assertLess(por_chave['mitoma-2022']['cena']['c'], LIMITE_LINHA_CM)
        self.assertGreater(por_chave['benzema-2014']['cena']['c'], LIMITE_LINHA_CM)
        linhas = por_chave['lautaro-2022']['var']['linhas']
        self.assertGreater(linhas[1]['x'], linhas[0]['x'])     # Lautaro à frente do penúltimo defensor


class GeradoresTests(SimpleTestCase):
    def test_impedimento_segue_a_geometria(self):
        for semente in range(300):
            lance = engine.gerar_impedimento(random.Random(semente), semente % 10 / 9)
            x_def, x_atk = (l['x'] for l in lance['var']['linhas'])
            variante = lance['chave'].split(':')[1]
            esperado = 'impedido' if variante == 'passe' and x_atk > x_def else 'legal'
            self.assertEqual(lance['correta']['decisao'], esperado, semente)
            foco = next(j for j in lance['cena']['jogadores'] if j.get('foco'))
            self.assertAlmostEqual(foco['p'][0], x_atk, places=1)

    def test_linha_do_gol_exige_a_bola_inteira(self):
        for semente in range(200):
            lance = engine.gerar_linha(random.Random(semente), 0.5)
            passou = lance['cena']['c'] > LIMITE_LINHA_CM
            self.assertEqual(lance['correta']['decisao'] in ('gol', 'saiu'), passou, semente)

    def test_area_vale_o_lugar_do_contato_e_a_linha_e_da_area(self):
        for semente in range(200):
            lance = engine.gerar_area(random.Random(semente), 0.7)
            cx, cy = lance['cena']['contato']
            dentro = cx > AREA_X and 13.84 < cy < 54.16
            self.assertEqual(lance['correta']['marcacao'], 'penalti' if dentro else 'falta', semente)

    def test_regra_12_cartoes(self):
        self.assertEqual(engine.decidir_cartao('violenta', 'comum', False)[0], 'vermelho')
        self.assertEqual(engine.decidir_cartao('disputa', 'clara', False)[0], 'vermelho')
        self.assertEqual(engine.decidir_cartao('disputa', 'clara', True)[0], 'amarelo')
        self.assertEqual(engine.decidir_cartao('puxao', 'clara', True)[0], 'vermelho')
        self.assertEqual(engine.decidir_cartao('disputa', 'promissora', False)[0], 'amarelo')
        self.assertEqual(engine.decidir_cartao('disputa', 'promissora', True)[0], 'nenhum')
        self.assertEqual(engine.decidir_cartao('puxao', 'promissora', True)[0], 'amarelo')
        self.assertEqual(engine.decidir_cartao('disputa', 'comum', False)[0], 'nenhum')

    def test_partida_deterministica_com_historicos_e_gerados(self):
        a, b = engine.gerar_partida(42), engine.gerar_partida(42)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertEqual(len(a), engine.LANCES_POR_PARTIDA)
        self.assertEqual(sum(1 for l in a if l['historico']), engine.HISTORICOS_POR_PARTIDA)
        evitar = [l['chave'] for l in a if l['historico']]
        c = engine.gerar_partida(43, evitar=evitar)
        self.assertFalse({l['chave'] for l in c if l['historico']} & set(evitar))
        for semente in range(40):          # todos os geradores rodam sem erro e são serializáveis
            json.dumps(engine.gerar_partida(semente))

    def test_publico_nao_vaza_gabarito(self):
        lance = engine.gerar_partida(7)[0]
        pub = engine.publico(lance, 0, 10)
        for chave in ('correta', 'explicacao', 'var'):
            self.assertNotIn(chave, pub)


class PontuacaoTests(SimpleTestCase):
    def setUp(self):
        self.lance = next(l for l in historicos.todos() if l['chave'] == 'suarez-2010')

    def test_acerto_rapido_com_sequencia(self):
        n = engine.avaliar(self.lance, _resposta_certa(self.lance), 0, False, 3)
        self.assertTrue(n['acertou'])
        self.assertEqual(n['pontos'], 100 + 50 + 30)

    def test_var_reduz_e_parcial_vale_menos(self):
        n = engine.avaliar(self.lance, _resposta_certa(self.lance), 30000, True, 0)
        self.assertEqual(n['pontos'], 60)
        parcial = engine.avaliar(self.lance, {'marcacao': 'penalti', 'cartao': 'amarelo'}, 0, False, 5)
        self.assertTrue(parcial['parcial'])
        self.assertEqual(parcial['pontos'], engine.PONTOS_PARCIAL)

    def test_resposta_invalida(self):
        with self.assertRaises(engine.RespostaInvalida):
            engine.avaliar(self.lance, {'marcacao': 'penalti'}, 0, False, 0)
        with self.assertRaises(engine.RespostaInvalida):
            engine.avaliar(self.lance, {'marcacao': 'xx', 'cartao': 'amarelo'}, 0, False, 0)


class FluxoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('juiz', password='x', first_name='Juiz')
        self.outro = User.objects.create_user('intruso', password='x')
        self.client.force_login(self.user)

    def _nova(self):
        self.client.post(reverse('arbitro:nova'))
        return PartidaArbitro.objects.get(usuario=self.user, status='andamento')

    def _responder(self, partida, resposta, indice=None):
        return self.client.post(reverse('arbitro:api_responder', args=[partida.pk]),
                                json.dumps({'indice': partida.indice if indice is None else indice, 'resposta': resposta}),
                                content_type='application/json')

    def test_telas(self):
        self.assertEqual(self.client.get(reverse('arbitro:hub')).status_code, 200)
        self.assertEqual(self.client.get(reverse('arbitro:ranking')).status_code, 200)
        partida = self._nova()
        resp = self.client.get(reverse('arbitro:partida', args=[partida.pk]))
        self.assertContains(resp, 'id="cena-arbitro"')
        self.assertContains(resp, 'window.CenaArbitro')
        self.client.logout()
        self.assertEqual(self.client.get(reverse('arbitro:hub')).status_code, 302)

    def test_nova_reaproveita_partida_aberta(self):
        p1 = self._nova()
        self.client.post(reverse('arbitro:nova'))
        self.assertEqual(PartidaArbitro.objects.filter(usuario=self.user).count(), 1)
        self.assertEqual(p1.total, engine.LANCES_POR_PARTIDA)

    def test_lance_publico_e_var(self):
        partida = self._nova()
        dados = self.client.get(reverse('arbitro:api_lance', args=[partida.pk])).json()
        self.assertFalse(dados['fim'])
        self.assertNotIn('correta', dados['lance'])
        var = self.client.post(reverse('arbitro:api_var', args=[partida.pk])).json()
        self.assertTrue(var['ok'])
        partida.refresh_from_db()
        self.assertTrue(partida.var_usado)
        self.assertEqual(partida.vars_chamados, 1)

    def test_partida_completa_premia_uma_vez_e_desbloqueia_conquista(self):
        partida = self._nova()
        saldo_antes = coins.saldo(self.user)
        for i in range(partida.total):
            partida.refresh_from_db()
            self.client.get(reverse('arbitro:api_lance', args=[partida.pk]))
            PartidaArbitro.objects.filter(pk=partida.pk).update(inicio_lance=timezone.now() - timedelta(seconds=60))
            lance = partida.lances[partida.indice]
            r = self._responder(partida, _resposta_certa(lance)).json()
            self.assertTrue(r['ok'] and r['acertou'], r)
        self.assertTrue(r['fim'])
        partida.refresh_from_db()
        self.assertEqual((partida.status, partida.acertos, partida.melhor_sequencia), ('fim', 10, 10))
        self.assertEqual(partida.premio, engine.premio(10))
        self.assertEqual(coins.saldo(self.user) - saldo_antes, engine.premio(10) + _recompensas_conquistas(self.user))
        # repetir a última resposta não paga de novo
        self.assertEqual(self._responder(partida, {}, indice=9).status_code, 400)
        self.assertEqual(self.client.get(reverse('arbitro:resultado', args=[partida.pk])).status_code, 200)
        from avisos.models import Conquista
        self.assertTrue(Conquista.objects.filter(usuario=self.user, slug='apito_de_ouro').exists())
        self.assertContains(self.client.get(reverse('arbitro:ranking')), 'Juiz')

    def test_erro_zera_sequencia_e_indice_antigo_e_recusado(self):
        partida = self._nova()
        self._responder(partida, _resposta_certa(partida.lances[0]))
        partida.refresh_from_db()
        self.assertEqual(self._responder(partida, _resposta_certa(partida.lances[0]), indice=0).status_code, 400)
        self._responder(partida, _resposta_errada(partida.lances[1]))
        partida.refresh_from_db()
        self.assertEqual((partida.indice, partida.sequencia, partida.acertos), (2, 0, 1))

    def test_outro_usuario_nao_mexe_na_partida(self):
        partida = self._nova()
        self.client.force_login(self.outro)
        self.assertEqual(self.client.get(reverse('arbitro:api_lance', args=[partida.pk])).status_code, 404)
        self.assertEqual(self._responder(partida, _resposta_certa(partida.lances[0])).status_code, 404)
        self.assertEqual(self.client.post(reverse('arbitro:api_var', args=[partida.pk])).status_code, 404)

    def test_limite_diario_de_premios(self):
        for _ in range(servico.LIMITE_PREMIADAS_POR_DIA):
            PartidaArbitro.objects.create(usuario=self.user, semente=1, lances=[], status='fim', premio=10,
                                          finalizado_em=timezone.now())
        partida = self._nova()
        for i in range(partida.total):
            partida.refresh_from_db()
            self._responder(partida, _resposta_certa(partida.lances[partida.indice]))
        partida.refresh_from_db()
        self.assertEqual((partida.status, partida.premio), ('fim', 0))


def _recompensas_conquistas(usuario):
    from avisos.conquistas import RECOMPENSA
    from avisos.models import Conquista
    return RECOMPENSA * Conquista.objects.filter(usuario=usuario).count()


class ResenhaTests(TestCase):
    def test_resenha_do_comentarista(self):
        from unittest import mock
        from django.test import override_settings
        user = User.objects.create_user('juiz2', password='x')
        self.client.force_login(user)
        self.client.post(reverse('arbitro:nova'))
        partida = PartidaArbitro.objects.get(usuario=user)
        url = reverse('arbitro:api_resenha', args=[partida.pk])
        self.assertEqual(self.client.post(url).status_code, 400)          # só no fim
        for _ in range(partida.total):
            partida.refresh_from_db()
            self.client.post(reverse('arbitro:api_responder', args=[partida.pk]),
                             json.dumps({'indice': partida.indice, 'resposta': _resposta_certa(partida.lances[partida.indice])}),
                             content_type='application/json')
        with override_settings(ANTHROPIC_API_KEY=None):
            r = self.client.post(url).json()
        self.assertEqual((r['ok'], r['fonte']), (True, 'pronta'))
        with override_settings(ANTHROPIC_API_KEY='teste'), \
                mock.patch('ia.cliente.gerar_json', return_value={'titulo': 'Apito de ouro!', 'texto': 'Que atuação.'}):
            r = self.client.post(url).json()
        self.assertEqual(r['titulo'], 'Apito de ouro!')
        partida.refresh_from_db()
        self.assertEqual(partida.resenha['fonte'], 'ia')
