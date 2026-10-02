from django.contrib import admin

from .models import Atleta, Comparativo, Escalacao, Time, Voto


class AtletaInline(admin.TabularInline):
    model = Atleta
    extra = 0
    fields = ('nome', 'posicao', 'numero', 'overall')
    show_change_link = True


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pais', 'liga', 'fonte', 'atualizado_em')
    list_filter = ('pais', 'liga', 'fonte')
    search_fields = ('nome', 'nome_curto', 'sigla')
    inlines = [AtletaInline]


@admin.register(Atleta)
class AtletaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'time', 'posicao', 'numero', 'overall', 'fonte')
    list_filter = ('posicao', 'fonte', 'time__liga')
    search_fields = ('nome', 'time__nome')
    list_editable = ('overall',)


class EscalacaoInline(admin.TabularInline):
    model = Escalacao
    extra = 0


@admin.register(Comparativo)
class ComparativoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'criador', 'criado_em', 'encerrado')
    inlines = [EscalacaoInline]


admin.site.register(Voto)
