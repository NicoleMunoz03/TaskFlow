from apps.tareas.models import Tarea, TareaUsuario, TareaDependencia
from apps.notificaciones.services import enviar_notificacion_asignacion


def crear_tarea(titulo, columna, descripcion='', fecha_limite=None, prioridad='media',
                usuarios=None, etiquetas=None):
    """Crea una tarea y asigna usuarios/etiquetas."""
    tarea = Tarea.objects.create(
        titulo=titulo,
        columna=columna,
        descripcion=descripcion,
        fecha_limite=fecha_limite,
        prioridad=prioridad,
    )
    if usuarios:
        for usuario in usuarios:
            asignar_usuario(tarea, usuario)
    if etiquetas:
        tarea.etiquetas.set(etiquetas)
    return tarea


def mover_tarea(tarea, nueva_columna):
    """Mueve una tarea a otra columna del mismo tablero o de otro."""
    tarea.columna = nueva_columna
    tarea.save(update_fields=['columna'])
    return tarea


def asignar_usuario(tarea, usuario):
    """Asigna un usuario a una tarea y envía notificación."""
    obj, created = TareaUsuario.objects.get_or_create(tarea=tarea, usuario=usuario)
    if created:
        enviar_notificacion_asignacion(usuario, tarea)
    return obj


def aplicar_filtros(tareas_qs, usuario_id=None, prioridad=None, etiqueta_id=None, fecha_limite=None):
    """Aplica filtros combinables sobre un queryset de Tarea."""
    if usuario_id:
        tareas_qs = tareas_qs.filter(usuarios__id=usuario_id)
    if prioridad:
        tareas_qs = tareas_qs.filter(prioridad=prioridad)
    if etiqueta_id:
        tareas_qs = tareas_qs.filter(etiquetas__id=etiqueta_id)
    if fecha_limite:
        tareas_qs = tareas_qs.filter(fecha_limite__lte=fecha_limite)
    return tareas_qs.distinct()


def tarea_esta_bloqueada(tarea):
    """Devuelve True si alguna de sus dependencias no está en estado 'Hecho'."""
    for dep in tarea.dependencias.all():
        if dep.columna.nombre.lower() not in ['hecho', 'done', 'completado']:
            return True
    return False


def validar_dependencia(tarea, dependencia):
    """Lanza ValueError si la dependencia es inválida (misma tarea, distinto proyecto, o circular)."""
    if tarea.pk == dependencia.pk:
        raise ValueError("Una tarea no puede depender de sí misma.")
        
    proyecto_tarea = tarea.columna.tablero.proyecto
    proyecto_dep = dependencia.columna.tablero.proyecto
    if proyecto_tarea.pk != proyecto_dep.pk:
        raise ValueError("Las dependencias deben pertenecer al mismo proyecto.")
        
    # Check if the intended dependency already depends on this task (circular A -> B -> A).
    # Since MVP says avoid graph parsing, a simple 1-level check is acceptable.
    if dependencia.dependencias.filter(pk=tarea.pk).exists():
        raise ValueError("Dependencia circular detectada.")


def agregar_dependencia(tarea, dependencia):
    """Agrega una dependencia a la tarea si es válida."""
    validar_dependencia(tarea, dependencia)
    TareaDependencia.objects.get_or_create(tarea=tarea, depende_de=dependencia)


def remover_dependencia(tarea, dependencia):
    """Elimina una dependencia existente."""
    TareaDependencia.objects.filter(tarea=tarea, depende_de=dependencia).delete()
