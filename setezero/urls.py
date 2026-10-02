from django.urls import path

from . import views

app_name = 'setezero'

urlpatterns = [
    path('', views.hub, name='hub'),
    path('novo/<str:modo>/', views.novo, name='novo'),
    path('partida/<int:pk>/', views.partida, name='partida'),
    path('api/partida/<int:pk>/estado/', views.api_estado, name='api_estado'),
    path('api/partida/<int:pk>/avancar/', views.api_avancar, name='api_avancar'),
    path('api/partida/<int:pk>/simular/', views.api_simular, name='api_simular'),
    path('temporada/<int:pk>/', views.temporada, name='temporada'),
    path('temporada/<int:pk>/jogar/', views.temporada_jogar, name='temporada_jogar'),
    path('ranking/', views.ranking, name='ranking'),
    path('copa/novo/', views.draft_novo, name='draft_novo'),
    path('mundial/novo/', views.draft_novo, {'torneio': 'mundial'}, name='mundial_novo'),
    path('copa/<int:pk>/', views.draft, name='draft'),
    path('copa/<int:pk>/api/<str:acao>/', views.api_draft, name='api_draft'),
    path('copa/<int:pk>/jogar/', views.draft_jogar, name='draft_jogar'),
    path('r/<uuid:codigo>/', views.retrospecto, name='retrospecto'),
]
