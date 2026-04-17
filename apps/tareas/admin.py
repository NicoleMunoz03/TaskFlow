from django.contrib import admin
from .models import Tarea, TareaUsuario, TareaEtiqueta


class TareaUsuarioInline(admin.TabularInline):
    model = TareaUsuario
    extra = 0


class TareaEtiquetaInline(admin.TabularInline):
    model = TareaEtiqueta
    extra = 0


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'prioridad', 'columna', 'fecha_limite', 'fecha_creacion')
    list_filter = ('prioridad', 'columna__tablero__proyecto')
    search_fields = ('titulo', 'descripcion')
    inlines = [TareaUsuarioInline, TareaEtiquetaInline]
    date_hierarchy = 'fecha_creacion'
