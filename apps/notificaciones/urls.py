from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.lista_notificaciones, name='lista'),
    path('<int:pk>/leer/', views.marcar_leida_view, name='marcar_leida'),
    path('contador/', views.contar_no_leidas_view, name='contador'),
]
