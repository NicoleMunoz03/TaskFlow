from django.contrib import admin
from .models import Etiqueta


@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'color', 'proyecto')
    list_filter = ('proyecto',)
    search_fields = ('nombre',)
