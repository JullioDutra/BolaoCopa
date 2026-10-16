from types import SimpleNamespace
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from . import cliente
from .models import UsoIA

SCHEMA = cliente.schema({'resposta': cliente.enum('sim', 'nao')})


def _resposta(texto, stop='end_turn'):
    return SimpleNamespace(stop_reason=stop, content=[SimpleNamespace(type='thinking', thinking=''),
                                                      SimpleNamespace(type='text', text=texto)],
                           usage=SimpleNamespace(input_tokens=120, output_tokens=30))


class ClienteIATests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('u', password='x')

    @override_settings(ANTHROPIC_API_KEY=None)
    def test_sem_chave_devolve_none_sem_gastar_cota(self):
        self.assertIsNone(cliente.gerar_json(self.user, 's', 'm', SCHEMA))
        self.assertFalse(UsoIA.objects.exists())

    @override_settings(ANTHROPIC_API_KEY='teste', IA_LIMITE_DIARIO=2, IA_MODELO='claude-haiku-5-5')
    def test_json_estruturado_cota_e_tokens(self):
        falso = mock.Mock()
        falso.messages.create.return_value = _resposta('{"resposta": "sim"}')
        with mock.patch.object(cliente, '_client', return_value=falso):
            self.assertEqual(cliente.gerar_json(self.user, 's', 'm', SCHEMA), {'resposta': 'sim'})
            self.assertEqual(cliente.gerar_json(self.user, 's', 'm', SCHEMA), {'resposta': 'sim'})
            self.assertIsNone(cliente.gerar_json(self.user, 's', 'm', SCHEMA))      # cota do dia acabou
        args = falso.messages.create.call_args.kwargs
        self.assertEqual(args['model'], 'claude-haiku-5-5')
        self.assertEqual(args['output_config']['format']['type'], 'json_schema')
        self.assertEqual(falso.messages.create.call_count, 2)
        uso = UsoIA.objects.get(usuario=self.user)
        self.assertEqual((uso.chamadas, uso.tokens_entrada, uso.tokens_saida), (2, 240, 60))
        self.assertEqual(cliente.restantes(self.user), 0)

    @override_settings(ANTHROPIC_API_KEY='teste')
    def test_erros_recusa_e_json_quebrado_viram_none(self):
        import anthropic
        falso = mock.Mock()
        with mock.patch.object(cliente, '_client', return_value=falso):
            falso.messages.create.return_value = _resposta('', stop='refusal')
            self.assertIsNone(cliente.gerar_json(self.user, 's', 'm', SCHEMA))
            falso.messages.create.return_value = _resposta('não é json')
            self.assertIsNone(cliente.gerar_json(self.user, 's', 'm', SCHEMA))
            falso.messages.create.side_effect = anthropic.APIConnectionError(request=mock.Mock())
            self.assertIsNone(cliente.gerar_json(self.user, 's', 'm', SCHEMA))

    def test_limitar_e_cortar(self):
        self.assertEqual(cliente.limitar('99', 0, 10), 10)
        self.assertEqual(cliente.limitar(None, 0, 10, 5), 5)
        self.assertEqual(cliente.cortar('abcdefghij', 5), 'abcd…')
