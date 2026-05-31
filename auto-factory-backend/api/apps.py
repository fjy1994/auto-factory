from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'API接口'

    def ready(self):
        from .flashing_poller import start_poller
        start_poller()
