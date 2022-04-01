from django.urls import re_path
from Account.consumer import NotifierConsumer, ChattingConsumer

websocket_urlpatterns = [
    re_path(r'ws/notify/(?P<room_name>\w+)$', NotifierConsumer.as_asgi()),
    re_path(r'ws/notify', NotifierConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)$', ChattingConsumer.as_asgi()),
    re_path(r'ws/chat', ChattingConsumer.as_asgi()),
]
