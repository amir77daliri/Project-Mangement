from django.urls import re_path

from .consumer import TaskNotificationConsumer

websocket_urlpatterns = [
    re_path(r"ws/notifications/$", TaskNotificationConsumer.as_asgi()),
]
