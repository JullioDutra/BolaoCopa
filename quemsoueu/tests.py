import datetime
import json
from unittest import mock

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from accounts import coins

from . import engine, servico
from .craques import CRAQUES, POR_CHAVE
from .models import PartidaQSE


class EngineTests(SimpleTestCase):
    def test_fichas_completas_e_unicas(self):
        self.assertGreaterEqual(len(CRAQUES), 40)
        self.assertEqual(len(POR_CHAVE), len(CRAQUES))
        for c in CRAQUES:
            self.assertTrue(c['clubes'] and len(c['curiosidades']) >= 3 and c['apelidos'], c['chave'])
            for rid, _, regra in engine.RAPIDAS:
                regra(c)                      # nenhuma pergunta rápida quebra com alguma ficha

    def test_craque_do_dia_fixo_e_sem_repetir_no_ciclo(self):
        inicio = datetime.date(2026, 1, 1)
        dias = [inicio + datetime.timedelta(days=i) for i in range(len(CRAQUES))]
        self.assertEqual(engine.craque_do_dia(dias[3]), engine.craque_do_dia(dias[3]))
        ciclo = {engine.craque_do_dia(d)['chave'] for d in dias if d.toordinal() // len(CRAQUES) == dias[0].toordinal() // len(CRAQUES)}
        self.assertEqual(len(ciclo), len([d for d in dias if d.toordinal() // len(CRAQUES) == dias[0].toordinal() // len(CRAQUES)]))

    def test_palpite_tolerante(self):
        messi, r9 = POR_CHAVE['messi'], POR_CHAVE['ronaldo']
        for p in ('Lionel Messi', 'messi', 'LEO MESSI', 'la pulga'):
            self.assertTrue(engine.acertou(messi, p), p)
        self.assertTrue(engine.acertou(r9, 'Fenômeno'))
        self.assertFalse(engine.acertou(r9, 'Cristiano Ronaldo'))
        self.assertFalse(engine.acertou(messi, 'me'))

    def test_comentario_nunca_revela_nome(self):
        messi = POR_CHAVE['messi']
        self.assertEqual(engine.comentario_seguro(messi, 'Isso mesmo, o Messi jogou lá!'), '')
        self.assertEqual(engine.comentario_seguro(messi, 'Na mosca, e foi bem jovem!'), 'Na mosca, e foi bem jovem!')

    def test_pontos(self):
        self.assertEqual(engine.pontuar(0, 0, 0), 100)
        self.assertEqual(engine.pontuar(5, 1, 1), 100 - 20 - 10 - 8)
        self.assertEqual(engine.pontuar(20, 2, 5), engine.PONTOS_MINIMOS)


class FluxoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('detetive', password='x', first_name='Sherlock')
        self.client.force_login(self.user)

    def _post(self, nome, pk, corpo):
        return self.client.post(reverse(f'quemsoueu:{nome}', args=[pk]), json.dumps(corpo), content_type='application/json')

    def test_telas(self):
        self.assertEqual(self.client.get(reverse('quemsoueu:hub')).status_code, 200)
        resp = self.client.get(reverse('quemsoueu:desafio'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.client.get(resp['Location']).status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(reverse('quemsoueu:hub')).status_code, 302)

    def test_desafio_unico_por_dia_e_acerto_premiado(self):
        p = servico.desafio_do_dia(self.user)
        self.assertEqual(servico.desafio_do_dia(self.user).pk, p.pk)
        estado = self._post('api_rapida', p.pk, {'id': 'brasileiro'}).json()
        self.assertEqual(len(estado['perguntas']), 1)
        self.assertNotIn('revelado', estado)                       # nada vaza antes do fim
        self.assertEqual(self._post('api_rapida', p.pk, {'id': 'brasileiro'}).status_code, 400)   # repetida
        self._post('api_dica', p.pk, {})
        saldo = coins.saldo(self.user)
        fim = self._post('api_palpite', p.pk, {'palpite': POR_CHAVE[p.craque]['nome']}).json()
        self.assertEqual(fim['status'], 'acertou')
        self.assertEqual(fim['revelado']['pontos'], 100 - 4 - 8)
        self.assertGreater(coins.saldo(self.user), saldo)
        self.assertEqual(self._post('api_palpite', p.pk, {'palpite': 'x'}).status_code, 400)

    def test_tres_palpites_errados_encerram(self):
        p = servico.desafio_do_dia(self.user)
        errados = [c['nome'] for c in CRAQUES if c['chave'] != p.craque][:3]
        for nome in errados:
            estado = self._post('api_palpite', p.pk, {'palpite': nome}).json()
        self.assertEqual(estado['status'], 'errou')
        self.assertEqual(PartidaQSE.objects.get(pk=p.pk).premio, 0)

    @override_settings(ANTHROPIC_API_KEY=None)
    def test_pergunta_livre_sem_ia_avisa(self):
        p = servico.desafio_do_dia(self.user)
        r = self._post('api_perguntar', p.pk, {'texto': 'Jogou na Itália?'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(PartidaQSE.objects.get(pk=p.pk).perguntas, [])

    @override_settings(ANTHROPIC_API_KEY='teste')
    def test_pergunta_livre_com_ia(self):
        p = servico.desafio_do_dia(self.user)
        nome = POR_CHAVE[p.craque]['nome'].split()[-1]
        with mock.patch('ia.cliente.gerar_json', return_value={'resposta': 'sim', 'comentario': f'Claro, {nome} jogou!'}) as g:
            estado = self._post('api_perguntar', p.pk, {'texto': 'Jogou na Itália?'}).json()
        self.assertIn('<pergunta>Jogou na Itália?</pergunta>', g.call_args.args[2])
        self.assertEqual(estado['perguntas'][0]['resposta'], 'sim')
        self.assertEqual(estado['perguntas'][0]['comentario'], '')     # comentário com o nome é descartado
        with mock.patch('ia.cliente.gerar_json', return_value={'resposta': 'invalida', 'comentario': ''}):
            estado = self._post('api_perguntar', p.pk, {'texto': 'Qual o seu nome?'}).json()
        self.assertEqual(len(estado['perguntas']), 1)                   # pergunta inválida não conta
        self.assertTrue(estado['aviso'])

    def test_treino_nao_entrega_o_desafio_do_dia_e_nao_paga(self):
        do_dia = servico.desafio_do_dia(self.user)
        t = servico.novo_treino(self.user)
        self.assertNotEqual(t.craque, do_dia.craque)
        self.assertEqual(t.modo, 'treino')
        fim = self._post('api_palpite', t.pk, {'palpite': POR_CHAVE[t.craque]['nome']}).json()
        self.assertEqual((fim['status'], fim['revelado']['premio']), ('acertou', 0))

    def test_outro_usuario_nao_acessa(self):
        p = servico.desafio_do_dia(self.user)
        self.client.force_login(User.objects.create_user('intruso', password='x'))
        self.assertEqual(self.client.get(reverse('quemsoueu:api_estado', args=[p.pk])).status_code, 404)
        self.assertEqual(self._post('api_palpite', p.pk, {'palpite': 'x'}).status_code, 404)
