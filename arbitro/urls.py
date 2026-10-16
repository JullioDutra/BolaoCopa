from django.urls import path

from . import views

app_name = 'arbitro'

urlpatterns = [
    # --- Telas ---
    path('', views.hub, name='hub'),
    path('nova/', views.nova, name='nova'),
    path('partida/<int:pk>/', views.partida, name='partida'),
    path('partida/<int:pk>/sumula/', views.resultado, name='resultado'),
    path('ranking/', views.ranking, name='ranking'),

    # --- APIs (JSON) ---
    path('api/partida/<int:pk>/lance/', views.api_lance, name='api_lance'),
    path('api/partida/<int:pk>/var/', views.api_var, name='api_var'),
    path('api/partida/<int:pk>/responder/', views.api_responder, name='api_responder'),
]
