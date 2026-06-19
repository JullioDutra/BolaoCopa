from django.urls import path
from . import views

app_name = 'carreira'

urlpatterns = [
    path('peneira/', views.tela_peneira, name='tela_peneira'),
    path('api/assinar/', views.api_assinar_contrato, name='api_assinar_contrato'),

    path('dashboard/', views.dashboard_carreira, name='dashboard'),
    path('api/treinar/', views.api_treinar, name='api_treinar'),
    path('vestiario/', views.tela_vestiario, name='tela_vestiario'),

    path('match/<int:partida_id>/', views.tela_match_day, name='tela_match_day'),
    path('api/match/<int:partida_id>/sync/', views.api_sync_partida, name='api_sync_partida'),
    path('api/match/<int:partida_id>/acao/', views.api_acao_lance, name='api_acao_lance'),


]