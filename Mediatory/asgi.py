"""
ASGI config for Mediatory project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from Account.middleware import TokenAuthMiddlewareStack
from django.core.asgi import get_asgi_application
from Account.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mediatory.settings')


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    )
})
