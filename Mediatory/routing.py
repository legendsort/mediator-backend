from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from Account.notify import NotifierConsumer
from Account.middleware import TokenAuthMiddlewareStack
from django.core.asgi import get_asgi_application


websocket_urlpatterns = [
    re_path(r'ws/notification', NotifierConsumer.as_asgi())
]

application = ProtocolTypeRouter({
    # "http": get_asgi_application(),
    'websocket': TokenAuthMiddlewareStack(URLRouter(
        websocket_urlpatterns,
    ))
})