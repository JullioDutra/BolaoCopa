from django.urls import path

from . import views

app_name = 'craque'

urlpatterns = [
    # --- Telas ---
    path('', views.hub, name='hub'),
    path('nova/', views.nova, name='nova'),
    path('carreira/<int:pk>/', views.carreira, name='carreira'),

    # --- APIs (JSON) ---
    path('api/carreira/<int:pk>/', views.api_estado, name='api_estado'),
    path('api/carreira/<int:pk>/decidir/', views.api_decidir, name='api_decidir'),
    path('api/carreira/<int:pk>/coletiva/', views.api_coletiva, name='api_coletiva'),
    path('api/carreira/<int:pk>/seguir/', views.api_seguir, name='api_seguir'),
]
