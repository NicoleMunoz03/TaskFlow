from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
]
