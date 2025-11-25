from django.apps import AppConfig


class SciencePublishingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.modules.science_publishing'
    label = 'science_publishing'
    verbose_name = 'Управление научными публикациями'
    auto_api = True

    def ready(self):
        # Импортируем сигналы при старте приложения
        from . import signals  # noqa: F401
