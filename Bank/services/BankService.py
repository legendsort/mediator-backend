import json
import requests as req
from django.conf import settings
from Bank.models import Data, DataType


class BankService:
    def __init__(self):
        self.base_url = getattr(settings, 'BANK_API_BASE_URL', '')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain'
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
            url = f"{self.base_url}/trade-info/fetch"
            response_code, res_data = self.call(url=url, method='get')
            if response_code and res_data['response_code'] is True:
                fetched_data_id_list = []
                for ele in res_data['data']:
                    try:
                        data_type = ele['type']
                        if not DataType.objects.filter(name=data_type).count():
                            DataType.objects.create(name=data_type)
                        data_type = DataType.objects.get(name=data_type)
                        if Data.objects.filter(type=data_type, real_data_created_at=ele['upTime']).count():
                            continue
                        data = Data()
                        data.type = data_type
                        data.json = ele['data']
                        data.real_data_created_at = ele['upTime']
                        data.save()
                        fetched_data_id_list.append(ele['_id'])
                    except DataType.DoesNotExist:
                        pass
                self.send_fetched_data(data={'id': fetched_data_id_list})
            else:
                print(response_code, res_data)
        except Exception as e:
            print('fetch bank data exceptions', e)
            return False

    def send_fetched_data(self, data=None):
        try:
            url = f"{self.base_url}/trade-info/fetch-succeed"
            response_code, message = self.call(url=url, data=data)
            return response_code, message
        except Exception as e:
            print('exception send fetched data', e)
            return False

    def fetch_crawling_logs(self, params=None):
        url = f"{self.base_url}/crawl-history/fetch"
        return self.call(url=url, method='get', data=params)


