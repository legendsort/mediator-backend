import json

import requests as req
from django.conf import settings


class ScriptConfigService:
    def __init__(self):
        self.base_url = f"{getattr(settings, 'CONFIG_API_BASE_URL', '')}"
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
        }

    def call(self, url='', data=None, files=None, method='post'):
        try:
            if files:
                headers = {
                    'token': ''
                }
                res = req.post(f"{url}", headers=headers, data={'data': json.dumps(data)}, files=files)
            elif method == 'get':
                res = req.get(url, params=data, headers=self.headers)
            elif method == 'post':
                res = req.post(url, json=data, headers=self.headers)
            else:
                res = req.delete(url, params=data, headers=self.headers)
            if 400 > res.status_code >= 200:
                pass
            elif res.status_code >= 400:
                return False, 'Server internal error'
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

    def fetch(self, params=None):
        try:
            url = f"{self.base_url}/fetch"
            
            response_code, response_data = self.call(url=url, method='get', data=params)
            if response_code and response_data['response_code'] is True:
                return response_code, response_data
            else:
                print(response_code, response_data)
        except Exception as e:
            print('fetch config data exceptions', e)
            return False
    
    def create(self, data = None):
        try:
            url = f"{self.base_url}/create"
            
            response_code, response_data = self.call(url=url, data=data)
            if response_code and response_data['response_code'] is True:
                code, response_data = self.fetch({"site": "all", "tag": "all"})
                return response_code, response_data
            else:
                print(response_code, response_data)
        except Exception as e:
            print('fetch config data exceptions', e)
            return False

    def update(self, data = None):
        try:
            url = f"{self.base_url}/update"
            response_code, response_data = self.call(url=url, data=data)
            
            if response_code and response_data['response_code'] is True:
                code, response_data = self.fetch({"site": "all", "tag": "all"})
                return response_code, response_data
            else:
                print(response_code, response_data)
        except Exception as e:
            print('fetch config data exceptions', e)
            return False

    def delete(self, data = None):
        try:
            url = f"{self.base_url}/delete"
            response_code, response_data = self.call(url=url, method='post', data=data)
            
            if response_code and response_data['response_code'] is True:
                code, response_data = self.fetch({"site": "all", "tag": "all"})
                return response_code, response_data
            else:
                return response_code, response_data
        except Exception as e:
            print('fetch config data exceptions', e)
            return False
