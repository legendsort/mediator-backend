import json
import requests as req
from django.conf import settings
from django_q.tasks import async_task
from time import sleep
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser
from django.db import models


class APIBaseService:

    def __init__(self, token=None):
        self.base_url = getattr(settings, 'MEDIATOR_SERVICE_API_BASE_URL', '')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Authorization': f"Bearer {token}"
        }
        self.token = token

    def set_token(self, token=''):
        self.headers["Authorization"] = f"Bearer {token}"

    def call(self, url='', data=None, files=None, method='post'):
        try:
            message = 'Successfully call'
            if files:
                headers = {
                    'Authorization': f"Bearer {self.token}"
                }
                res = req.post(f"{url}", headers=headers, data={'data': json.dumps(data)}, files=files)
            elif method == 'get':
                res = req.get(url, params=data, headers=self.headers)
            elif method == 'delete':
                res = req.delete(url, json=data, headers=self.headers)
            else:
                res = req.post(url, json=data, headers=self.headers)
            if 400 > res.status_code >= 200:
                pass
            elif res.status_code >= 400:
                if res.status_code == 404:
                    message = 'Not Found'
                if res.status_code >= 500:
                    message = 'Server has error!'
                return False, message
            return True, res.json()
        except req.exceptions.InvalidURL:
            return False, 'invalid url'
        except req.exceptions.ConnectTimeout:
            return False, 'timeout'
        except req.HTTPError:
            return False, 'http error'
        except req.exceptions.ConnectionError:
            return False, 'connection error'
        except Exception as e:
            print('bank api calling error', e)
            return False, 'unknown error'


class MediatorService(APIBaseService):
    def __init__(self, token=None):
        self.base_url = getattr(settings, 'MEDIATOR_SERVICE_API_BASE_URL', '')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain',
            'Authorization': f"Bearer {token}"
        }
        self.token = token

    def connect(self):
        url = f"{self.base_url}/api/v1/connect/browser"
        return self.call(url=url)


class NotificationService:
    def __init__(self, user=AnonymousUser()):
        self.user = user
        self.channel_prefix = 'notify'
        self.channel_layer = get_channel_layer()

    def notify(self, message, to=AnonymousUser()):
        async_to_sync(self.channel_layer.group_send)(
            self.get_channel_name(to.username), {
                'type': 'notification',
                'message': message
            }
        )
        return True

    def get_channel_name(self, name):
        return f"{self.channel_prefix}_{name}"

