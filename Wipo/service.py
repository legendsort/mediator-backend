from Account.services import APIBaseService
from django.conf import settings
import requests as req
from rest_framework.response import Response
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json

class FTPService(APIBaseService):

    def __init__(self, token):
        self.base_url = f"{getattr(settings, 'MEDIATOR_SERVICE_API_BASE_URL', '')}/api/v1/cloud"
        self.headers = {
            'Accept': '*/*',
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json',
        }
        self.token = token
        self.username = None
        self.host = None
        self.password = None
        self.get_ftp_account()

    def get_ftp_account(self):
        self.username = 'mediator'
        self.host = '192.168.4.82'
        self.password = 'qwe'
        return 'mediator', '192.168.4.82', 'qwe'

    def list(self, path):
        list_url = f"{self.base_url}/list"
        return self.call(url=list_url, method='get', data={
            'username': self.username,
            'password': self.password,
            'host': self.host,
            'path': path
        })

    def remove(self, path):
        url = f"{self.base_url}/remove"
        return self.call(url=url, data={
            'username': self.username,
            'password': self.password,
            'host': self.host,
            'path': path,
        }, method='delete')
        pass

    def rename(self, src_path, dst_path):
        url = f"{self.base_url}/rename"
        return self.call(url=url, data={
            'username': self.username,
            'password': self.password,
            'host': self.host,
            'srcPath': src_path,
            'dstPath': dst_path,
        })

    def copy(self, src_path, dst_path):
        url = f"{self.base_url}/copy"
        return self.call(url=url, data={
            'username': self.username,
            'password': self.password,
            'host': self.host,
            'srcPath': src_path,
            'dstPath': dst_path,
        })

    def upload(self, request):
        url = f"{self.base_url}/upload"
        try:
            src_path = request.data.get('src_path')
            files = request.data.getlist('files')
            print(files)
            for file in files:
                req.post(f"{url}", headers={'Authorization': f"Bearer {self.token}"}, data={'srcPath': src_path}, files={'file': file})
            pass
            return True
        except Exception as e:
            print('=====>', e)
            return False
            
            
        

    def download(self, src_path, dst_path):
        url = f"{self.base_url}/download"
        return self.call(url=url, data={
            'username': self.username,
            'password': self.password,
            'host': self.host,
            'srcPath': src_path,
            'dstPath': dst_path,
        })
        pass
