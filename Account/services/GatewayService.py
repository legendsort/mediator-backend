import datetime
import json
import os
from os.path import basename
from django.conf import settings
from django_q.tasks import async_task
from time import sleep
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser
from Account.message import Error
import time
import uuid
import glob
from typing import Optional


# Notify to user via channels
class NotificationService:
    def __init__(self, user=AnonymousUser()):
        self.user = user
        self.channel_prefix = 'notify'
        self.channel_layer = get_channel_layer()

    def set_user(self, user):
        self.user = user
        return self

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


# Notify parser procedure
class NotifyParserService:
    def __init__(self, data, mode: str, file_path: str, notifier: Optional['NotificationService'] = None):
        self.data = data
        self.file_path = file_path
        self.notifier = notifier
        if mode in self._instance_method_choices:
            self.mode = mode
        else:
            raise ValueError(f"Invalid Value for mode: {mode}")

    def do_notify(self, user, to_user) -> NotificationService:
        self.notifier = NotificationService(user)
        return self.notifier

    def remove_file(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def notify_system_info(self) -> bool:
        try:
            print(f"Value {self.data.get('usedpct') if self.data.get('usedpct') else self.data.get('loadpct')}")
            return True
        except IndexError:
            print('here')
        except Exception as e:
            print(e)
            return False

    _instance_method_choices = {
        "systeminfo-disk": notify_system_info,
        "systeminfo-cpu": notify_system_info,
    }

    def run(self):
        self._instance_method_choices[self.mode].__get__(self)()
        self.remove_file()


# Gateway service for connecting gateway service with different api
class GatewayService(NotificationService):
    NIS_SEND_DIR_PATH = getattr(settings, 'NIS_SEND_DIR_PATH', '/media')
    NIS_RECEIVE_DIR_PATH = getattr(settings, 'NIS_RECEIVE_DIR_PATH', '/media')

    def __init__(self, user=AnonymousUser()):
        super().__init__(user)
        self.request_id = str(uuid.uuid4())
        self.time_interval = 1

    def send_request(self, action: str = '', data=None, is_async=False):
        request_data = {
            'action': action,
            'data': data,
            'async': is_async
        }
        if not self.make_request(request_data):
            return False
        if is_async:
            return {
                'response_code': True,
                'message': f"{action} has been launched",
                'data': []
            }
        else:
            res_data = self.wait_for_getting_file()
            if res_data:
                self.deal_with_res_data(res_data)
                return res_data
            else:
                return False

    def deal_with_res_data(self, data):
        return data

    def get_receive_response_file_list(self):
        path = f"{self.NIS_RECEIVE_DIR_PATH}/*.json"
        files = glob.glob(path, recursive=True)
        try:
            for file_path in files:
                if f"{self.request_id}.json" == basename(file_path):
                    with open(file_path) as res_file:
                        data_loaded = json.load(res_file)
                        res_file.close()
                        return data_loaded
            return False
        except Exception as e:
            print('json dump error', e)
            return False

    def wait_for_getting_file(self):
        start_time = datetime.datetime.now()
        while True:
            diff = (datetime.datetime.now() - start_time).seconds
            time.sleep(self.time_interval)
            res_data = self.get_receive_response_file_list()
            if res_data:
                file_path = f"{self.NIS_RECEIVE_DIR_PATH}/{self.request_id}.json"
                if os.path.exists(file_path):
                    os.remove(file_path)
                return res_data
            if diff > 60:
                break
        return False

    def make_request(self, data):
        with open(f"{self.NIS_SEND_DIR_PATH}/{self.request_id}.json", 'w', encoding='utf-8') as request_json_file:
            request_json_file.write(json.dumps(data, ensure_ascii=False))
            request_json_file.close()
            return True
