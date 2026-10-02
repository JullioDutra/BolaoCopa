from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .npc import MARCA


class NpcFilter(admin.SimpleListFilter):
    title = 'tipo'
    parameter_name = 'tipo'

    def lookups(self, request, model_admin):
        return [('reais', 'Pessoas (sem NPCs)'), ('npcs', 'NPCs do carreira')]

    def queryset(self, request, queryset):
        if self.value() == 'npcs':
            return queryset.filter(last_name=MARCA)
        if self.value() == 'reais':
            return queryset.exclude(last_name=MARCA)
        return queryset


class UsuarioAdmin(UserAdmin):
    list_filter = (NpcFilter,) + tuple(UserAdmin.list_filter)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if 'tipo' not in request.GET:     # por padrão, só pessoas
            qs = qs.exclude(last_name=MARCA)
        return qs


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
