import threading
from django.core.mail import send_mail
from django.conf import settings


def enviar_correo_asincrono(subject, message, recipient_list):
    """Ejecuta el envío de correo en un hilo separado para no bloquear la solicitud principal."""
    def _target():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=True,
            )
        except Exception:
            pass

    threading.Thread(target=_target).start()


def enviar_notificacion_asignacion(usuario, tarea):
    """Guarda notificación en BD y dispara el envío de email asíncrono."""
    from apps.notificaciones.models import Notificacion

    proyecto_nombre = tarea.columna.tablero.proyecto.nombre
    mensaje = f'Has sido asignado a la tarea "{tarea.titulo}" en el proyecto "{proyecto_nombre}".'

    # Guardar en base de datos (Síncrono, es rápido)
    Notificacion.objects.create(usuario=usuario, mensaje=mensaje)

    # Enviar email (Asíncrono, no bloquea al usuario)
    subject = f'[TaskFlow] Nueva tarea asignada: {tarea.titulo}'
    body = f'Hola {usuario.get_short_name()},\n\n{mensaje}\n\n— TaskFlow Pro'
    enviar_correo_asincrono(subject, body, [usuario.email])


def marcar_leida(notificacion_id, usuario):
    """Marca una notificación como leída."""
    from apps.notificaciones.models import Notificacion
    try:
        n = Notificacion.objects.get(pk=notificacion_id, usuario=usuario)
        n.leido = True
        n.save(update_fields=['leido'])
        return True
    except Notificacion.DoesNotExist:
        return False


def marcar_todas_leidas(usuario):
    """Marca todas las notificaciones del usuario como leídas."""
    from apps.notificaciones.models import Notificacion
    Notificacion.objects.filter(usuario=usuario, leido=False).update(leido=True)


def contar_no_leidas(usuario):
    """Retorna el conteo de notificaciones no leídas."""
    from apps.notificaciones.models import Notificacion
    return Notificacion.objects.filter(usuario=usuario, leido=False).count()
