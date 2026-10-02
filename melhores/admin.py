from django.contrib import admin

from .models import Aposta, Candidato, Categoria, Edicao


class CandidatoInline(admin.TabularInline):
    model = Candidato
    extra = 1


@admin.register(Edicao)
class EdicaoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'ativa', 'apostas_ate', 'margem_casa', 'coins_por_voto')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'edicao', 'tipo', 'ordem', 'aberta', 'liquidada', 'vencedor')
    list_filter = ('edicao', 'tipo', 'aberta', 'liquidada')
    list_editable = ('ordem', 'aberta')
    inlines = [CandidatoInline]


@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'votos_ano_anterior', 'votos_anos_anteriores')
    list_filter = ('categoria__edicao', 'categoria')
    search_fields = ('nome', 'texto')


@admin.register(Aposta)
class ApostaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'categoria', 'candidato', 'valor', 'odd_travada', 'status', 'retorno')
    list_filter = ('status', 'categoria__edicao', 'categoria')
    readonly_fields = ('criada_em', 'atualizada_em')
