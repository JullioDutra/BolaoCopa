from django.contrib import admin
from .models import Saque, Deposito
from accounts.models import Carteira, Transacao

@admin.register(Saque)
class SaqueAdmin(admin.ModelAdmin):
    # Mostra essas colunas na tela principal
    list_display = ('usuario', 'valor', 'chave_pix', 'aprovado')
    
    # Cria um filtro lateral para você ver só os "Pendentes"
    list_filter = ('aprovado',)
    
    # A MÁGICA: Permite você marcar o check de "aprovado" direto na lista, sem precisar abrir o saque
    list_editable = ('aprovado',)
    
    # Barra de pesquisa
    search_fields = ('usuario__first_name', 'usuario__username', 'chave_pix')

@admin.register(Carteira)
class CarteiraAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'saldo')
    search_fields = ('usuario__username',)

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('carteira', 'tipo', 'valor', 'descricao')
    list_filter = ('tipo',)
    search_fields = ('carteira__usuario__username',)



@admin.register(Deposito)
class DepositoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'valor', 'data_solicitacao', 'aprovado')
    list_filter = ('aprovado',)
    list_editable = ('aprovado',) # Botão de aprovação rápida
    search_fields = ('usuario__username', 'usuario__first_name')