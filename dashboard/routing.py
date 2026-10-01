from django.urls import path
from .consumers import AdminConsumer
websocket_urlpatterns = [path("ws/admin/", AdminConsumer.as_asgi())]
