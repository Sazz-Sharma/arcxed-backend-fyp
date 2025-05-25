# your_project_name/asgi.py

import os
import django # 1. Import django
import sys
sys.path.append(r'd:\arcxed\arcxed-backend-fyp\questions\agents\study_plan\src')
# 2. Set the default settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') # <-- Make sure 'core.settings' matches your project

# 3. Call django.setup() to initialize Django apps and settings
django.setup()

# 4. NOW it's safe to import modules that depend on Django's setup
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import socketroom.routing  # <-- Import your routing configuration here

# 5. Get the standard Django ASGI application
django_asgi_app = get_asgi_application()

# 6. Define the ProtocolTypeRouter
application = ProtocolTypeRouter({
    "http": django_asgi_app, # Handles standard HTTP requests
    "websocket": AuthMiddlewareStack( # Handles WebSocket requests, includes auth
        URLRouter(
            socketroom.routing.websocket_urlpatterns # Use the imported routing
        )
    ),
})