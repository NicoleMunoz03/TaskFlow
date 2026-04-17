from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Tarea
from .forms import TareaForm
from .services import crear_tarea, mover_tarea, asignar_usuario, aplicar_filtros, agregar_dependencia, remover_dependencia, tarea_esta_bloqueada
from apps.tableros.models import Columna


@login_required
@require_POST
def crear_tarea_view(request):
    tablero_pk = request.POST.get('tablero_pk')
    columna_pk = request.POST.get('columna')

    try:
        columna = Columna.objects.get(pk=columna_pk, tablero__proyecto__usuario_proyectos__usuario=request.user, tablero__proyecto__usuario_proyectos__activo=True)
    except Columna.DoesNotExist:
        messages.error(request, 'Columna no válida.')
        return redirect('proyectos:lista')

    proyecto = columna.tablero.proyecto
    form = TareaForm(request.POST, proyecto=proyecto)

    if form.is_valid():
        tarea = form.save(commit=False)
        
        dependencias_nuevas = request.POST.getlist('dependencias')
        if dependencias_nuevas:
            col_pendiente = Columna.objects.filter(tablero=columna.tablero, nombre__iexact='pendiente').first()
            if not col_pendiente:
                col_pendiente = Columna.objects.filter(tablero=columna.tablero).order_by('orden').first()
            if col_pendiente:
                tarea.columna = col_pendiente
        
        tarea.save()
        
        # Guardar dependencias
        for dep_id in dependencias_nuevas:
            try:
                dep_obj = Tarea.objects.get(pk=dep_id, columna__tablero__proyecto=proyecto)
                agregar_dependencia(tarea, dep_obj)
            except (Tarea.DoesNotExist, ValueError):
                pass
                
        # Manejar usuarios y etiquetas con el services layer
        usuarios = form.cleaned_data.get('usuarios', [])
        etiquetas = form.cleaned_data.get('etiquetas', [])
        for usuario in usuarios:
            asignar_usuario(tarea, usuario)
        tarea.etiquetas.set(etiquetas)
        messages.success(request, f'Tarea "{tarea.titulo}" creada.')
        tablero = columna.tablero
        return redirect('tableros:detalle', pk=tablero.pk)
    else:
        messages.error(request, 'Error al crear la tarea. Revisa los campos.')
        tablero = columna.tablero
        return redirect('tableros:detalle', pk=tablero.pk)


@login_required
def editar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, columna__tablero__proyecto__usuario_proyectos__usuario=request.user, columna__tablero__proyecto__usuario_proyectos__activo=True)
    proyecto = tarea.columna.tablero.proyecto
    tablero = tarea.columna.tablero

    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea, proyecto=proyecto)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.save()
            # Re-asignar usuarios notificando solo los nuevos
            usuarios_nuevos = set(form.cleaned_data.get('usuarios', []))
            usuarios_actuales = set(tarea.usuarios.all())
            for usuario in usuarios_nuevos - usuarios_actuales:
                asignar_usuario(tarea, usuario)
            # Quitar los deseleccionados
            for usuario in usuarios_actuales - usuarios_nuevos:
                tarea.tarea_usuarios.filter(usuario=usuario).delete()
            tarea.etiquetas.set(form.cleaned_data.get('etiquetas', []))
            
            # Actualizar dependencias (reemplazar todas por las enviadas en el form)
            dependencias_nuevas = set(form.cleaned_data.get('dependencias', []))
            dependencias_actuales = set(tarea.dependencias.all())
            for dep in dependencias_actuales - dependencias_nuevas:
                remover_dependencia(tarea, dep)
            for dep in dependencias_nuevas - dependencias_actuales:
                try:
                    agregar_dependencia(tarea, dep)
                except ValueError:
                    pass
                    
            # Forzar la columna si queda bloqueada
            if tarea_esta_bloqueada(tarea) and tarea.columna.nombre.lower() not in ['pendiente', 'pending']:
                col_pendiente = Columna.objects.filter(tablero=tablero, nombre__iexact='pendiente').first()
                if not col_pendiente:
                    col_pendiente = Columna.objects.filter(tablero=tablero).order_by('orden').first()
                if col_pendiente:
                    tarea.columna = col_pendiente
                    tarea.save(update_fields=['columna'])
                    messages.warning(request, 'La tarea ha sido forzada a la columna Pendiente debido a sus prerrequisitos.')
            
            messages.success(request, 'Tarea actualizada correctamente.')
            return redirect('tableros:detalle', pk=tablero.pk)
        else:
            messages.error(request, 'Error al actualizar la tarea.')
    else:
        form = TareaForm(instance=tarea, proyecto=proyecto)

    return render(request, 'taskflow/tablero/tarea.html', {
        'form': form,
        'tarea': tarea,
        'tablero': tablero,
        'proyecto': proyecto,
    })


@login_required
def eliminar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, columna__tablero__proyecto__usuario_proyectos__usuario=request.user, columna__tablero__proyecto__usuario_proyectos__activo=True)
    tablero = tarea.columna.tablero
    if request.method == 'POST':
        nombre = tarea.titulo
        tarea.delete()
        messages.success(request, f'Tarea "{nombre}" eliminada.')
        return redirect('tableros:detalle', pk=tablero.pk)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
@require_POST
def mover_tarea_view(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, columna__tablero__proyecto__usuario_proyectos__usuario=request.user, columna__tablero__proyecto__usuario_proyectos__activo=True)
    nueva_columna_pk = request.POST.get('columna_id')
    try:
        nueva_columna = Columna.objects.get(
            pk=nueva_columna_pk,
            tablero__proyecto__usuario_proyectos__usuario=request.user, tablero__proyecto__usuario_proyectos__activo=True,
        )
        
        if tarea.columna.nombre.lower() in ['hecho', 'done', 'completado']:
            return JsonResponse({'ok': False, 'error': 'Esta tarea ya está completada y no puede moverse a otra columna.'}, status=400)

        if tarea_esta_bloqueada(tarea):
            if nueva_columna.nombre.lower() not in ['pendiente', 'pending']:
                return JsonResponse({'ok': False, 'error': 'La tarea está bloqueada y no puede ser movida a esta columna.'}, status=400)
                
        mover_tarea(tarea, nueva_columna)
        return JsonResponse({'ok': True, 'columna': nueva_columna.nombre})
    except Columna.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Columna inválida'}, status=400)


@login_required
@require_POST
def agregar_dependencia_view(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, columna__tablero__proyecto__usuario_proyectos__usuario=request.user, columna__tablero__proyecto__usuario_proyectos__activo=True)
    dependencia_id = request.POST.get('dependencia_id')
    try:
        dependencia = Tarea.objects.get(pk=dependencia_id, columna__tablero__proyecto__usuario_proyectos__usuario=request.user, columna__tablero__proyecto__usuario_proyectos__activo=True)
        agregar_dependencia(tarea, dependencia)
        return JsonResponse({'ok': True})
    except ValueError as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
    except Tarea.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Dependencia no encontrada'}, status=400)


@login_required
@require_POST
def remover_dependencia_view(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, columna__tablero__proyecto__usuario_proyectos__usuario=request.user, columna__tablero__proyecto__usuario_proyectos__activo=True)
    dependencia_id = request.POST.get('dependencia_id')
    try:
        dependencia = Tarea.objects.get(pk=dependencia_id, columna__tablero__proyecto__usuario_proyectos__usuario=request.user, columna__tablero__proyecto__usuario_proyectos__activo=True)
        remover_dependencia(tarea, dependencia)
        return JsonResponse({'ok': True})
    except Tarea.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Dependencia no encontrada'}, status=400)


@login_required
def filtrar_tareas(request):
    """Filtrado de tareas con parámetros GET — redirige al tablero con filtros aplicados."""
    tablero_pk = request.GET.get('tablero')
    if tablero_pk:
        params = request.GET.urlencode()
        return redirect(f'/tablero/{tablero_pk}/?{params}')
    return redirect('proyectos:lista')
