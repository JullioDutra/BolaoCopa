from django.urls import path
from . import views

app_name = 'duelos'

urlpatterns = [
    # Rotas de Navegação e Criação
    path('', views.listar_desafios, name='listar_desafios'),
    path('criar/<str:tipo_jogo>/', views.criar_duelo, name='criar_duelo'),
    path('lobby/<int:partida_id>/', views.lobby_espera, name='lobby_espera'),
    path('entrar/<int:partida_id>/', views.entrar_duelo_link, name='entrar_duelo_link'),
    
    # Rotas de API (AJAX Invisível)
    path('api/lobby/<int:partida_id>/', views.checar_oponente_api, name='checar_oponente_api'),

    path('jogo/<int:partida_id>/', views.tela_jogo, name='tela_jogo'),
    path('api/status/<int:partida_id>/', views.status_partida_api, name='status_partida_api'),
    path('api/chutar/<int:partida_id>/', views.enviar_palpite_api, name='enviar_palpite_api'),
    path('api/desistir/<int:partida_id>/', views.desistir_partida_api, name='desistir_partida_api'),
    path('historico/', views.historico_duelos, name='historico_duelos'),
    path('campeonatos/criar/', views.criar_campeonato, name='criar_campeonato'),
    path('campeonatos/<int:campeonato_id>/', views.painel_campeonato, name='painel_campeonato'),
    path('campeonatos/entrar/<uuid:codigo_convite>/', views.entrar_campeonato, name='entrar_campeonato'),
    path('campeonatos/<int:campeonato_id>/gerar-chaves/', views.gerar_chaveamento, name='gerar_chaveamento'),
    path('campeonatos/<int:campeonato_id>/chaves/', views.ver_chaveamento, name='ver_chaveamento'),
    path('campeonatos/confronto/<int:confronto_id>/jogar/', views.iniciar_jogo_campeonato, name='iniciar_jogo_campeonato'),
    path('campeonatos/<int:campeonato_id>/', views.painel_campeonato, name='painel_campeonato'),
    path('campeonatos/<int:campeonato_id>/resetar/', views.resetar_campeonato, name='resetar_campeonato'),
    # ==========================================
    # ROTAS DO MINI FANÁTICOS (2v2)
    # ==========================================
    path('mini/criar/', views.criar_mini_fanaticos, name='criar_mini_fanaticos'),
    path('mini/entrar/<int:partida_id>/', views.entrar_mini_fanaticos, name='entrar_mini_fanaticos'),
    path('mini/lobby/<int:partida_id>/', views.lobby_mini, name='lobby_mini'),
    path('api/mini/status/<int:partida_id>/', views.status_lobby_mini_api, name='status_lobby_mini_api'),
    path('mini/jogar/<int:partida_id>/', views.tela_jogo_mini, name='tela_jogo_mini'),
    path('api/mini/submeter/<int:partida_id>/', views.submeter_respostas_mini, name='submeter_respostas_mini'),
    path('mini/resultado/<int:partida_id>/', views.resultado_mini, name='resultado_mini'),
]
