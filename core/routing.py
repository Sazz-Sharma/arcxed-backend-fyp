from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import socketroom.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            socketroom.routing.websocket_urlpatterns
        )
    ),
    # You can add additional protocols here if needed.
})
