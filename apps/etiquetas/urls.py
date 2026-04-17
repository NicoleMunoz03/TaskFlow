from django.urls import path
from . import views

app_name = 'etiquetas'

urlpatterns = [
    path('crear/<int:proyecto_pk>/', views.crear_etiqueta, name='crear'),
    path('<int:pk>/eliminar/', views.eliminar_etiqueta, name='eliminar'),
]
