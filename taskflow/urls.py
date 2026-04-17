from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('proyectos:lista')),
    path('', include('apps.usuarios.urls', namespace='usuarios')),
    path('proyectos/', include('apps.proyectos.urls', namespace='proyectos')),
    path('tablero/', include('apps.tableros.urls', namespace='tableros')),
    path('tareas/', include('apps.tareas.urls', namespace='tareas')),
    path('etiquetas/', include('apps.etiquetas.urls', namespace='etiquetas')),
    path('notificaciones/', include('apps.notificaciones.urls', namespace='notificaciones')),
]
