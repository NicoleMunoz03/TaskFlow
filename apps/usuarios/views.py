from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistroForm, LoginForm


def registro_view(request):
    if request.user.is_authenticated:
        return redirect('proyectos:lista')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='apps.usuarios.backends.EmailBackend')
            messages.success(request, f'¡Bienvenido, {user.get_short_name()}! Tu cuenta ha sido creada.')
            return redirect('proyectos:lista')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroForm()
    return render(request, 'taskflow/auth/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('proyectos:lista')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'proyectos:lista')
                return redirect(next_url)
            else:
                messages.error(request, 'Correo o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor revisa los campos.')
    else:
        form = LoginForm()
    return render(request, 'taskflow/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('usuarios:login')
