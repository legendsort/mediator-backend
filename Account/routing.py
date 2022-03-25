from django.urls import re_path
from Account.notify import NotifierConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', NotifierConsumer.as_asgi())
]
