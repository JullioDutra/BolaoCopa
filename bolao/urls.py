from django.urls import path
from . import views

app_name = 'bolao' # <--- É isso aqui que cria o "namespace" que o Django estava sentindo falta!

urlpatterns = [
    path('escolher-plano/', views.escolher_plano, name='escolher_plano'),
]