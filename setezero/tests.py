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
        self.assertGreaterEqual(len(dados.TIMES), 36)
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
        self.assertLess(melhor_fregues, pior_historico)


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


def _draftar_sozinho(draft):
    """ Bot: escolhe sempre o melhor jogador que cabe numa vaga (usa o banco por último). """
    from . import copa
    while not copa.completo(draft):
        chave = copa.sortear(draft)
        time = dados.obter(chave)
        vagas = copa.vagas(draft)
        pos = copa.posicoes_slots(draft)
        melhor = None
        for j in sorted(time['elenco'], key=lambda x: -x['nota']):
            for i in vagas['slots']:
                if dados.custo_posicao(j['pos'], pos[i]) <= copa.CUSTO_MAXIMO_ADAPTACAO:
                    melhor = (j, i)
                    break
            if melhor:
                break
        if melhor:
            copa.escolher(draft, melhor[0]['nome'], melhor[1])
        elif vagas['banco']:
            copa.escolher(draft, time['elenco'][0]['nome'], 'banco')
        else:
            copa.pular(draft) if draft.estado['skips'] > 0 else copa.escolher(draft, time['elenco'][0]['nome'], 'banco')


class PenaltisTests(SimpleTestCase):
    def test_empate_no_mata_mata_vai_para_penaltis_e_tem_vencedor(self):
        achou = 0
        for seed in range(40):
            e = engine.novo_estado({'time': 'fla-2019'}, {'time': 'pal-2021'}, seed, usuario_lado='casa', mata_mata=True)
            engine.simular_completo(e)
            if e['placar']['casa'] == e['placar']['fora']:
                achou += 1
                self.assertIn(e['penaltis']['vencedor'], ('casa', 'fora'))
                self.assertNotEqual(e['penaltis']['casa'], e['penaltis']['fora'])
                self.assertIn('pen_gol', {x['tipo'] for x in e['eventos']} | {'pen_gol'})
            self.assertIn(engine.vencedor(e), ('casa', 'fora'))
        self.assertGreater(achou, 0)

    def test_sem_mata_mata_nao_ha_penaltis(self):
        for seed in range(30):
            e = engine.novo_estado({'time': 'fla-2019'}, {'time': 'pal-2021'}, seed)
            engine.simular_completo(e)
            self.assertNotIn('penaltis', e)


class DraftCopaTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('tec', password='x', first_name='Tec')
        self.client.force_login(self.u)

    def test_regras_do_draft(self):
        from . import copa
        d = copa.criar_draft(self.u)
        with self.assertRaises(copa.ErroDraft):
            copa.escolher(d, 'Zico', 5)             # sem dado rolado
        chave = copa.sortear(d)
        self.assertEqual(copa.sortear(d), chave)    # mesmo dado até escolher
        time = dados.obter(chave)
        goleiro = next(j for j in time['elenco'] if j['pos'] == 'GOL')
        atacante = next(j for j in time['elenco'] if j['pos'] == 'ATA')
        with self.assertRaises(copa.ErroDraft):
            copa.escolher(d, atacante['nome'], 0)   # atacante no gol
        copa.escolher(d, goleiro['nome'], 0)
        self.assertEqual(d.estado['slots'][0]['pos'], 'GOL')
        self.assertIsNone(d.estado['pendente'])
        copa.sortear(d)
        copa.pular(d)
        self.assertEqual(d.estado['skips'], copa.SKIPS - 1)
        with self.assertRaises(copa.ErroDraft):
            copa.escolher(d, 'Fulano Inexistente', 'banco')

    def test_jogador_adaptado_perde_nota_e_nome_repetido_fica_unico(self):
        from . import copa
        d = copa.criar_draft(self.u, formacao='4-4-2')
        d.estado['pendente'] = 'spa-2006'          # Júnior (LAT) existe aqui e no Flamengo 1981
        copa.escolher(d, 'Júnior', 1)
        d.estado['pendente'] = 'fla-1981'
        copa.escolher(d, 'Júnior', 4)
        nomes = [j['nome'] for j in d.estado['slots'] if j]
        self.assertEqual(len(set(nomes)), 2)
        d.estado['pendente'] = 'fla-1981'
        mei = next(j for j in dados.obter('fla-1981')['elenco'] if j['pos'] == 'MEI' and j['nome'] == 'Adílio')
        copa.escolher(d, 'Adílio', 5)              # MEI na vaga de VOL: adaptado
        j = d.estado['slots'][5]
        self.assertTrue(j['adaptado'])
        self.assertLess(j['nota'], mei['nota'])
        self.assertEqual(j['pos'], 'VOL')

    def test_copa_completa_ate_o_fim(self):
        from . import copa
        d = copa.criar_draft(self.u)
        _draftar_sozinho(d)
        d.refresh_from_db()
        self.assertEqual(sum(1 for j in d.estado['slots'] if j), 11)
        self.assertEqual(sum(1 for j in d.estado['banco'] if j), 5)
        copa.iniciar_copa(d)
        d.refresh_from_db()
        self.assertEqual(len(d.estado['rivais']), 7)
        self.assertEqual(len(set(d.estado['rivais'])), 7)
        self.assertTrue(all(r in dados.TIMES for r in d.estado['rivais']))  # só times históricos reais
        for fase in range(7):
            d.refresh_from_db()
            if d.status != 'copa':
                break
            p = copa.partida_da_fase(d)
            self.assertEqual(p.fase, fase)
            self.assertTrue(p.estado['mata_mata'])
            while p.status != 'fim':
                servico.avancar(p, 'fim')
                p.refresh_from_db()
            self.assertIn(p.resultado, 'VD')
        d.refresh_from_db()
        self.assertIn(d.status, ('campeao', 'eliminado'))
        if d.status == 'eliminado':
            self.assertEqual(d.campanha[-1]['resultado'], 'D')
            self.assertEqual([c['resultado'] for c in d.campanha[:-1]], ['V'] * (len(d.campanha) - 1))
            self.assertIsNone(copa.partida_da_fase(d))   # não joga mais nenhuma fase
        r = self.client.get(reverse('setezero:retrospecto', args=[d.codigo]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'wa.me')

    def test_mata_mata_elimina_na_primeira_derrota(self):
        from . import copa
        d = copa.criar_draft(self.u)
        _draftar_sozinho(d)
        d.refresh_from_db()
        copa.iniciar_copa(d)
        d.refresh_from_db()
        for _ in range(7):
            d.refresh_from_db()
            if d.status != 'copa':
                break
            p = copa.partida_da_fase(d)
            while p.status != 'fim':
                servico.avancar(p, 'fim')
                p.refresh_from_db()
        d.refresh_from_db()
        derrotas = [c for c in d.campanha if c['resultado'] == 'D']
        if d.status == 'eliminado':
            self.assertEqual(len(derrotas), 1)
            self.assertEqual(d.campanha[-1]['resultado'], 'D')
        else:
            self.assertEqual(d.status, 'campeao')
            self.assertEqual(len(d.campanha), 7)

    def test_titulos_e_premio(self):
        from . import copa
        d = copa.criar_draft(self.u)
        d.status = 'campeao'
        d.campanha = [{'fase': i, 'nome_fase': copa.FASES[i], 'rival': 'varzea-fc', 'rival_nome': 'Várzea', 'gols_pro': 2, 'gols_contra': 0,
                       'penaltis': '', 'resultado': 'V', 'partida': 0} for i in range(7)]
        saldo = coins.saldo(self.u)
        copa._fechar(d)
        d.save()
        self.assertTrue(d.invicto)
        self.assertEqual(copa.titulo(d)['manchete'], '7 A 0! CAMPEÃO INVICTO')
        self.assertGreaterEqual(coins.saldo(self.u), saldo + copa.PREMIO_CAMPEAO + copa.PREMIO_INVICTO)
        d.campanha[3]['penaltis'] = '4-3'
        d.invicto = False
        self.assertEqual(copa.titulo(d)['curto'], 'Campeão sem perder')
        d.campanha[2]['resultado'] = 'D'
        self.assertEqual(copa.titulo(d)['curto'], 'Campeão')

    def test_paginas_e_api(self):
        from . import copa
        self.assertEqual(self.client.get(reverse('setezero:draft_novo')).status_code, 200)
        r = self.client.post(reverse('setezero:draft_novo'), {'formacao': '4-4-2', 'mentalidade': 'ofensivo', 'modo': 'campanha'})
        d = copa.DraftCopa7a0.objects.get()
        self.assertTrue(d.eliminatorio)   # sempre mata-mata, mesmo se mandarem outro modo
        self.assertEqual(self.client.get(reverse('setezero:draft', args=[d.pk])).status_code, 200)
        j = self.client.post(reverse('setezero:api_draft', args=[d.pk, 'sortear'])).json()
        self.assertTrue(j['visao']['pendente']['elenco'])
        ruim = self.client.post(reverse('setezero:api_draft', args=[d.pk, 'iniciar']), content_type='application/json')
        self.assertEqual(ruim.status_code, 400)
        self.assertEqual(self.client.get(reverse('setezero:hub')).status_code, 200)
        # retrospecto de draft em andamento só para o dono
        self.client.logout()
        self.assertEqual(self.client.get(reverse('setezero:retrospecto', args=[d.codigo])).status_code, 404)
        outro = User.objects.create_user('outro', password='x')
        self.client.force_login(outro)
        self.assertEqual(self.client.get(reverse('setezero:draft', args=[d.pk])).status_code, 404)


class CalibragemCopaTests(TestCase):
    def test_bot_tem_chance_razoavel_mas_nao_garantida(self):
        from . import copa
        u = User.objects.create_user('bot', password='x')
        titulos = 0
        N = 6
        for _ in range(N):
            d = copa.criar_draft(u)
            _draftar_sozinho(d)
            d.refresh_from_db()
            copa.iniciar_copa(d)
            for _ in range(7):
                d.refresh_from_db()
                if d.status != 'copa':
                    break
                p = copa.partida_da_fase(d)
                while p.status != 'fim':
                    servico.avancar(p, 'fim')
                    p.refresh_from_db()
            d.refresh_from_db()
            titulos += d.status == 'campeao'
        self.assertLess(titulos, N)   # não pode ser passeio
