from django.urls import path
from . import views

app_name = 'modocarreira' # O NOME CORRETO!

urlpatterns = [
    # Peneira e Criação
    path('peneira/', views.tela_peneira, name='tela_peneira'),
    path('api/assinar/', views.api_assinar_contrato, name='api_assinar_contrato'),
    
    # Dashboard e Treinos
    path('dashboard/', views.dashboard_carreira, name='dashboard'),
    path('api/treinar/', views.api_treinar, name='api_treinar'),
    path('api/dilema/', views.api_resolver_dilema, name='api_resolver_dilema'),
    
    # Vestiário e Jogo Ao Vivo
    path('vestiario/', views.tela_vestiario, name='tela_vestiario'),
    path('partida/<int:partida_id>/', views.tela_match_day, name='tela_match_day'),
    path('api/partida/<int:partida_id>/sync/', views.api_sync_partida, name='api_sync_partida'),
    path('api/partida/<int:partida_id>/acao/', views.api_acao_lance, name='api_acao_lance'),
    path('partida/<int:partida_id>/resumo/', views.tela_resumo_partida, name='tela_resumo_partida'),
    
    # Mercado e Vida Social
    path('mercado/', views.tela_mercado, name='tela_mercado'),
    path('api/proposta/<int:proposta_id>/responder/', views.api_responder_proposta, name='api_responder_proposta'),
    path('social/', views.tela_social, name='tela_social'),
    path('api/pazes/<int:conflito_id>/', views.api_fazer_pazes, name='api_fazer_pazes'),
    path('museu/', views.tela_museu, name='tela_museu'),
    path('classificacao/', views.tela_classificacao, name='tela_classificacao'),
    path('elencos/', views.tela_elencos, name='tela_elencos'),
    
    # Cronjob (O Motor do Jogo)
    path('api/engine/cron/<str:token>/', views.api_cron_engine, name='api_cron_engine'),
]
