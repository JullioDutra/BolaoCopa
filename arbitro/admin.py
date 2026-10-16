from django.contrib import admin

from .models import PartidaArbitro


@admin.register(PartidaArbitro)
class PartidaArbitroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pontos', 'acertos', 'melhor_sequencia', 'status', 'premio', 'criado_em')
    list_filter = ('status',)
    search_fields = ('usuario__username', 'usuario__first_name')
    readonly_fields = ('lances', 'respostas')
