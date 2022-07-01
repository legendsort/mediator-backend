from Account.services import APIBaseService
from django.conf import settings
import requests
from rest_framework.response import Response
from requests_toolbelt.multipart.encoder import MultipartEncoder


class FTPService(APIBaseService):

    def __init__(self, token):
        self.base_url = f"{getattr(settings, 'MEDIATOR_SERVICE_API_BASE_URL', '')}/api/v1/cloud"
        self.headers = {
            'Accept': '*/*',
            'Authorization': f"Bearer {token}",
            "Content-Type":"multipart/form-data"
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

    def upload(self, files):
        url = f"{self.base_url}/upload"
        try:
            multipart_data = MultipartEncoder(fields={
                    # a file upload field
                    'file': files,
                    'field0': 'value0', 
                    'field1': 'value1',
                }
            )

            return requests.post(url, headers={'Content-Type': multipart_data.content_type}, data=multipart_data )
            # return self.call(url=url, data={
            # 'srcPath': '/',
            # 'file': {'file': files}
            # })
        except Exception as e:
            print('=====>', e)
            
            
        

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
