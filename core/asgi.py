# core/asgi.py

import os
import django
import sys
sys.path.append(r'd:\arcxed\arcxed-backend-fyp\questions\agents\study_plan\src')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()

from django.core.asgi import get_asgi_application

application = get_asgi_application()