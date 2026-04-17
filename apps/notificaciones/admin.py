from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mensaje', 'leido', 'fecha')
    list_filter = ('leido', 'usuario')
    search_fields = ('mensaje', 'usuario__email')
    date_hierarchy = 'fecha'
    actions = ['marcar_como_leidas']

    def marcar_como_leidas(self, request, queryset):
        queryset.update(leido=True)
    marcar_como_leidas.short_description = 'Marcar como leídas'
