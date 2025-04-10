# chat/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Route WebSocket connections for URLs like /ws/chat/{room_uuid}/
    re_path(r'ws/chat/(?P<room_id>[0-9a-f-]+)/$', consumers.ChatConsumer.as_asgi()),
    # The regex matches a standard UUID format
]