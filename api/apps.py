from django.apps import AppConfig


class SciencePublishingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # путь к приложению после переноса в modules/science_publishing/api
    name = 'modules.science_publishing.api'
    label = 'science_publishing'
    verbose_name = 'Управление научными публикациями'
    auto_api = True

    def ready(self):
        # Импортируем сигналы при старте приложения
        from . import signals  # noqa: F401
