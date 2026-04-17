from django.urls import path
from . import views

app_name = 'proyectos'

urlpatterns = [
    path('', views.lista_proyectos, name='lista'),
    path('crear/', views.crear_proyecto, name='crear'),
    path('<int:pk>/', views.detalle_proyecto, name='detalle'),
    path('<int:pk>/editar/', views.editar_proyecto, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_proyecto, name='eliminar'),
    path('<int:pk>/agregar-miembro/', views.agregar_miembro, name='agregar_miembro'),
    path('<int:pk>/inhabilitar-miembro/<int:usuario_pk>/', views.inhabilitar_miembro, name='inhabilitar_miembro'),
    path('<int:pk>/habilitar-miembro/<int:usuario_pk>/', views.habilitar_miembro, name='habilitar_miembro'),
]
