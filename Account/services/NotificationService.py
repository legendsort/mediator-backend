from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import async_to_sync


class NotificationService:
    def __init__(self, to=AnonymousUser(), ):
        self.to = to
        self.channel_layer = get_channel_layer()

    def get_channel_name(self):
        return f"notify_{self.to.username}"

    def notify(self, message):
        try:
            async_to_sync(self.channel_layer.group_send)(self.get_channel_name(), {
                'type': 'chat_message',
                'message': message
            })
        except Exception as e:
            print('---', e)
            return False

        return True

    def set_user(self, to):
        self.to = to
