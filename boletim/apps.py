from django.apps import AppConfig


class BoletimConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boletim'
    verbose_name = 'Boletim Digital'

    def ready(self):
        from boletim import signals  # noqa: F401
