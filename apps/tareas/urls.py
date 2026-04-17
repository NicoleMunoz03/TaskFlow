from django.urls import path
from . import views

app_name = 'tareas'

urlpatterns = [
    path('crear/', views.crear_tarea_view, name='crear'),
    path('<int:pk>/editar/', views.editar_tarea, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_tarea, name='eliminar'),
    path('<int:pk>/mover/', views.mover_tarea_view, name='mover'),
    path('filtrar/', views.filtrar_tareas, name='filtrar'),
    path('<int:pk>/agregar_dependencia/', views.agregar_dependencia_view, name='agregar_dependencia'),
    path('<int:pk>/remover_dependencia/', views.remover_dependencia_view, name='remover_dependencia'),
]
