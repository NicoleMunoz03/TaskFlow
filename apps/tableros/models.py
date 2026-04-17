from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Tablero(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    proyecto = models.ForeignKey(
        'proyectos.Proyecto',
        on_delete=models.CASCADE,
        related_name='tableros',
        verbose_name='Proyecto',
    )

    class Meta:
        verbose_name = 'tablero'
        verbose_name_plural = 'tableros'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} — {self.proyecto.nombre}'


class Columna(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    tablero = models.ForeignKey(
        Tablero,
        on_delete=models.CASCADE,
        related_name='columnas',
        verbose_name='Tablero',
    )

    class Meta:
        verbose_name = 'columna'
        verbose_name_plural = 'columnas'
        ordering = ['orden']

    def __str__(self):
        return f'{self.nombre} ({self.tablero.nombre})'


# ── Signal: auto-crear tablero y columnas al crear un proyecto ──────────────
@receiver(post_save, sender='proyectos.Proyecto')
def crear_tablero_por_defecto(sender, instance, created, **kwargs):
    if created:
        tablero = Tablero.objects.create(
            nombre='Tablero Principal',
            proyecto=instance,
        )
        columnas_default = [
            ('Pendiente', 0),
            ('En Progreso', 1),
            ('Hecho', 2),
        ]
        for nombre, orden in columnas_default:
            Columna.objects.create(nombre=nombre, orden=orden, tablero=tablero)
