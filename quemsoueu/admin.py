from django.contrib import admin

from .models import PartidaQSE


@admin.register(PartidaQSE)
class PartidaQSEAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'modo', 'dia', 'craque', 'status', 'pontos', 'premio')
    list_filter = ('modo', 'status', 'dia')
    search_fields = ('usuario__username', 'craque')
