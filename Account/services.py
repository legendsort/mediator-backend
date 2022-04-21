import datetime
import json
import os
from os.path import basename
import requests as req
from django.conf import settings
from django_q.tasks import async_task
from time import sleep
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser
from Account.message import Error
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.conf import settings
import uuid
import glob


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
            print('api calling ', res.status_code)
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


# Connecting API to mediator service
class MediatorService(APIBaseService):
    def __init__(self, token=None):
        super().__init__(token)
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


# Notify to user via channels
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


class WatchService:
    # Set the directory on watch
    watchDirectory = "/"

    def __init__(self):
        self.observer = Observer()

    def run(self, during=None):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        print('===start===')
        # try:
        #     time.sleep(1)
        #     print('========')
        #     # while True:
        #     #     time.sleep(10)
        # except Exception as e:
        #     print(e)
        #     self.observer.stop()
        #     print("Observer Stopped")
        print('===join===')
        self.observer.join()
        print('===joined===')

    def stop(self):
        self.observer.stop()
        print("Observer Stopped")


class Handler(FileSystemEventHandler):

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == 'modified':
            # Event is modified, you can process it now
            print("Watchdog received modified event - % s." % event.src_path)

    def on_deleted(self, event):
        pass


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
            pass
        else:
            return self.wait_for_getting_file()

    def wait_with_timeout(self, wait_time: int = 3):
        pass

    def deal_with_res_data(self, data):
        pass

    def get_receive_response_file_list(self):
        path = f"{self.NIS_RECEIVE_DIR_PATH}/*.json"
        files = glob.glob(path, recursive=True)
        try:
            for file_path in files:
                if f"{self.request_id}.json" == basename(file_path):
                    with open(file_path) as res_file:
                        data_loaded = json.load(res_file)
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
                return res_data
            if diff > 60:
                break
        return False

    def make_request(self, data):
        with open(f"{self.NIS_SEND_DIR_PATH}/{self.request_id}.json", 'w', encoding='utf-8') as request_json_file:
            request_json_file.write(json.dumps(data, ensure_ascii=False))
            return True
