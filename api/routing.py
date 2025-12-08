from django.urls import re_path

from .consumers import WorkChatConsumer, NotificationConsumer

websocket_urlpatterns = [
    # UUID (pk) + допускаем префикс слеша
    re_path(
        r'^/?ws/science_publishing/works/(?P<work_id>[0-9a-fA-F-]+)/chat/?$',
        WorkChatConsumer.as_asgi(),
    ),
    re_path(
        r'^/?ws/science_publishing/notifications/?$',
        NotificationConsumer.as_asgi(),
    ),
]
