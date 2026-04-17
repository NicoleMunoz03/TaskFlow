from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=150, verbose_name='Nombre completo')
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    objects = UsuarioManager()

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.email})'

    def get_short_name(self):
        return self.nombre.split()[0] if self.nombre else self.email

    def get_initials(self):
        parts = self.nombre.strip().split()
        if len(parts) >= 2:
            return f'{parts[0][0]}{parts[1][0]}'.upper()
        return self.nombre[:2].upper() if self.nombre else 'US'
