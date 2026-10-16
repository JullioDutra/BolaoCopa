from django.contrib import admin

from .models import UsoIA


@admin.register(UsoIA)
class UsoIAAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'dia', 'chamadas', 'tokens_entrada', 'tokens_saida')
    list_filter = ('dia',)
    search_fields = ('usuario__username',)
