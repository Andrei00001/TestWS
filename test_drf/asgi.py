"""
ASGI config for test_drf project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from friend_app import routing
from test_drf.auth import TokenAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_drf.settings')

# application = get_asgi_application()
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket":TokenAuthMiddleware(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
