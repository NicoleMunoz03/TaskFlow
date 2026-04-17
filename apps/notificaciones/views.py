from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notificacion
from .services import marcar_leida, marcar_todas_leidas


@login_required
def lista_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    marcar_todas_leidas(request.user)
    return render(request, 'taskflow/notificaciones/lista.html', {
        'notificaciones': notificaciones,
    })


@login_required
@require_POST
def marcar_leida_view(request, pk):
    ok = marcar_leida(pk, request.user)
    return JsonResponse({'ok': ok})


@login_required
def contar_no_leidas_view(request):
    from .services import contar_no_leidas
    count = contar_no_leidas(request.user)
    return JsonResponse({'count': count})
