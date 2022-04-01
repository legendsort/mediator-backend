import json
from channels.generic.websocket import AsyncWebsocketConsumer
from Account.models import Message
from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db import close_old_connections


@database_sync_to_async
def get_user(user_id):
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class NotifierConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = f"notify_{self.scope['user'].username}"
        # Join room group
        try:
            if self.scope['user'] is AnonymousUser():
                await sync_to_async(self.scope['user'].update_online)(True)
        except Exception as e:
            pass
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class ChattingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = self.get_room_name(self.scope['user'].username)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    def get_room_name(self, name):
        if 'room_name' in self.scope['url_route']['kwargs']:
            return f"chat_{self.scope['url_route']['kwargs']['room_name']}"
        else:
            return f"chat_{name}"

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            to_user_id = text_data_json['to']
            to_user = await get_user(to_user_id)
            await self.channel_layer.group_send(
                self.get_room_name(to_user.username),
                {
                    'type': 'chat_message',
                    'message': text_data_json
                }
            )
        except Exception as e:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': text_data_json
                }
            )
            pass

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
