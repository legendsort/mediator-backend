import json
from channels.generic.websocket import AsyncWebsocketConsumer
from Account.models import Message, Notice, User
from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from Account.serializers import NoticeSerializer


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


@database_sync_to_async
def create_notice(data):
    notice = Notice()
    try:
        sender = User.objects.get(pk=data['sender_id'])
        if data.get('receiver_id'):
            receiver = User.objects.get(pk=data['receiver_id'])
        else:
            receiver = User.objects.filter(is_superuser=True).first()
        notice.sender = sender
        notice.receiver = receiver
        notice.content = data['content']
        notice.additional_info = data['additional_info']
        notice.save()
        return notice
    except Exception as e:
        print('---->', e)
        return False


class NotifierConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = f"notify_{self.scope['user'].username}"
        # Join room group
        try:
            if self.scope['user'].username:
                await sync_to_async(self.scope['user'].update_online)(True)
        except Exception as e:
            print('notify websocket connection error', e)
            return True
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print(self.room_group_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        print('disconnecting-----', self.room_group_name)
        await sync_to_async(self.scope['user'].update_online)(False)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
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
        await self.send(text_data=json.dumps(message))


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
    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
            notice = await create_notice(text_data_json)
            text_data_json = NoticeSerializer(notice).data
            text_data_json['type'] = 'message'
            await self.channel_layer.group_send(
                self.get_room_name(notice.receiver.username),
                {
                    'type': 'chat_message',
                    'message': text_data_json
                }
            )
        except Exception as e:
            print('<------>', e)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'type': 'error'
                    }
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
