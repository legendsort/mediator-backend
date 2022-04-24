import json
import requests as req
from django.conf import settings


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


