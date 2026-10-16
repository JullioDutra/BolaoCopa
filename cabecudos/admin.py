from django.contrib import admin

from .models import PartidaCabecudos


@admin.register(PartidaCabecudos)
class PartidaCabecudosAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fase', 'gols_pro', 'gols_contra', 'status', 'premio', 'iniciada_em')
    list_filter = ('status', 'fase')
    search_fields = ('usuario__username',)
