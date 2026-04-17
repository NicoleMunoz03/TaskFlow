from django.contrib import admin
from .models import Tablero, Columna


class ColumnaInline(admin.TabularInline):
    model = Columna
    extra = 0
    ordering = ['orden']


@admin.register(Tablero)
class TableroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'proyecto')
    list_filter = ('proyecto',)
    inlines = [ColumnaInline]


@admin.register(Columna)
class ColumnaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden', 'tablero')
    list_filter = ('tablero',)
    ordering = ['tablero', 'orden']
