from django.contrib import admin
from .models import Saque
from accounts.models import Carteira
from accounts.models import Transacao


@admin.register(Saque)
class SaqueAdmin(admin.ModelAdmin):
    # O que vai aparecer na tabela para você ler rápido
    list_display = ('usuario', 'valor', 'chave_pix', 'data_solicitacao', 'aprovado')
    
    # Filtro lateral para você ver só quem tá "Pendente"
    list_filter = ('aprovado', 'data_solicitacao')
    
    # Barra de pesquisa
    search_fields = ('usuario__username', 'usuario__email', 'chave_pix')
    
    # O Pulo do Gato: Permite você clicar no botão de "Aprovado" direto na lista, sem precisar abrir o pedido!
    list_editable = ('aprovado',)