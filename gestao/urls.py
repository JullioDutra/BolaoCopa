from django.urls import path

from . import views

app_name = 'gestao'

urlpatterns = [
    path('', views.hub, name='hub'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/<int:pk>/', views.usuario, name='usuario'),
    path('auditoria/', views.auditoria_view, name='auditoria'),
    path('sistema/', views.sistema, name='sistema'),
]
