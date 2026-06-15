from django.urls import path
from . import views

app_name = 'minijogo'

urlpatterns = [
    # --- Telas Visuais ---
    path('draft/', views.tela_draft, name='tela_draft'),
    path('lobby/', views.lobby_batalha, name='lobby'),
    path('partida/<int:partida_id>/', views.tela_jogo, name='tela_jogo'),
    path('convite/<int:partida_id>/', views.aceitar_convite, name='aceitar_convite'),
    path('api/partida/desistir/', views.api_desistir, name='api_desistir'),
    path('ranking/', views.ranking_x1, name='ranking_x1'),
    path('partida/<int:partida_id>/cancelar/', views.cancelar_lobby, name='cancelar_lobby'),
    path('api/enviar-emote/', views.api_enviar_emote, name='api_enviar_emote'),

    
    # --- APIs (Chamadas AJAX em segundo plano) ---
    path('api/draft/escolher/', views.api_escolher_carta, name='api_escolher_carta'),
    path('api/partida/acao/', views.api_enviar_acao, name='api_enviar_acao'),
    path('api/partida/<int:partida_id>/status/', views.api_status_partida, name='api_status_partida'),
]
