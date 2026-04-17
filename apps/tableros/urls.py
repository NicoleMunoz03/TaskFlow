from django.urls import path
from . import views

app_name = 'tableros'

urlpatterns = [
    path('<int:pk>/', views.tablero_detail, name='detalle'),
    path('crear/<int:proyecto_pk>/', views.crear_tablero, name='crear'),
    path('<int:pk>/editar/', views.editar_tablero, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_tablero, name='eliminar'),
]
