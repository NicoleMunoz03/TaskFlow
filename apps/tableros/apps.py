from django.apps import AppConfig


class TablerosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tableros'

    def ready(self):
        # Importar signals para que se registren
        import apps.tableros.models  # noqa
