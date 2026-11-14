from django.contrib import admin

from boletim.models import (
    Boletim, ConfiguracaoBoletim, FuncaoBoletim, ItemModeloOrdemCulto,
    ItemOrdemCulto, ModeloOrdemCulto, PedidoOracao, ProgramaSemanal,
)


class ItemOrdemCultoInline(admin.TabularInline):
    model = ItemOrdemCulto
    extra = 0


@admin.register(Boletim)
class BoletimAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'estado', 'publicado_em', 'actualizado_em']
    list_filter = ['estado']
    raw_id_fields = ['actividade']
    readonly_fields = ['publicado_em', 'criado_por', 'criado_em', 'actualizado_em']
    inlines = [ItemOrdemCultoInline]


@admin.register(ItemOrdemCulto)
class ItemOrdemCultoAdmin(admin.ModelAdmin):
    list_display = ['boletim', 'ordem', 'titulo_pt', 'detalhe']


class ItemModeloOrdemCultoInline(admin.TabularInline):
    model = ItemModeloOrdemCulto
    extra = 1


@admin.register(ModeloOrdemCulto)
class ModeloOrdemCultoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'activo']
    inlines = [ItemModeloOrdemCultoInline]


@admin.register(ItemModeloOrdemCulto)
class ItemModeloOrdemCultoAdmin(admin.ModelAdmin):
    list_display = ['modelo', 'ordem', 'titulo_pt', 'detalhe']


@admin.register(FuncaoBoletim)
class FuncaoBoletimAdmin(admin.ModelAdmin):
    list_display = ['funcao', 'rotulo_pt', 'rotulo_en', 'ordem']


@admin.register(ProgramaSemanal)
class ProgramaSemanalAdmin(admin.ModelAdmin):
    list_display = ['titulo_pt', 'dia_semana', 'hora_inicio', 'hora_fim', 'activo', 'ordem']
    list_filter = ['activo', 'dia_semana']


@admin.register(ConfiguracaoBoletim)
class ConfiguracaoBoletimAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return super().has_add_permission(request) and not ConfiguracaoBoletim.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PedidoOracao)
class PedidoOracaoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'estado', 'confidencial', 'criado_em']
    list_filter = ['estado', 'confidencial']
    raw_id_fields = ['caso_pastoral']
    readonly_fields = ['criado_em', 'ip_hash']
