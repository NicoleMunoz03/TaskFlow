from django.contrib import admin
from .models import Proyecto, UsuarioProyecto


class UsuarioProyectoInline(admin.TabularInline):
    model = UsuarioProyecto
    extra = 1


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_creacion')
    search_fields = ('nombre',)
    inlines = [UsuarioProyectoInline]


@admin.register(UsuarioProyecto)
class UsuarioProyectoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'proyecto')
    list_filter = ('proyecto',)
