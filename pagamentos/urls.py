from django.urls import path
from . import views

app_name = 'pagamentos'

urlpatterns = [
    path('deposito/', views.solicitar_deposito, name='solicitar_deposito'),
    path('pix/<int:deposito_id>/', views.pagar_pix, name='pagar_pix'),
    path('extrato/', views.extrato_carteira, name='extrato'), 
    path('saque/', views.solicitar_saque, name='solicitar_saque'),
    path('diretoria/', views.relatorio_gerencial, name='relatorio_gerencial'),
]