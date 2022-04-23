import json

import requests as req
from django.conf import settings


class ConfigService:
    def __init__(self, token):
        self.base_url = f"{getattr(settings, 'CONFIG_API_BASE_URL', '')}"
        print ("====>", self.base_url)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Authorization': f"Bearer {token}"
        }
        self.token = token
        self.username = None
        self.host = None
        self.password = None
        

    def call(self, url='', data=None, files=None, method='post'):
        try:
            if files:
                headers = {
                    'token': ''
                }
                res = req.post(f"{url}", headers=headers, data={'data': json.dumps(data)}, files=files)
            elif method == 'get':
                res = req.get(url, params=data, headers=self.headers)
            else:
                res = req.post(url, json=data, headers=self.headers)
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

    def fetch(self):
        try:
            url = f"{self.base_url}/fetch"
            print ("url ===>", url)
            response_code, res_data = self.call(url=url, method='get')
            if response_code and res_data['response_code'] is True:
                return res_data['data']
            else:
                print(response_code, res_data)
        except Exception as e:
            print('fetch bank data exceptions', e)
            return False


