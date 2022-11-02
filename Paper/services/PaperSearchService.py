
import json
import requests as req
from django.conf import settings
from Bank.models import Data, DataType
from pymongo import MongoClient


class PaperSearchService:
    def __init__(self):
        self.base_url = getattr(settings, 'PAPER_SEARCH_API_BASE_URL', '')
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

    def search(self, data=None):
        try:
            url = f"{self.base_url}"
            response_code, res_data = self.call(url=url, method='post', data=data)
            if response_code and res_data['response_code'] is True:
                results = res_data['data']['results']
                paper_data = PaperData()
                for res in results:
                    paper_data.insert_update(res)
                    if '_id' in res.keys():
                        res['_id'] = None
                return res_data['data']
            else:
                return False
        except Exception as e:
            print('fetch bank data exceptions', e)
            return False


class PaperData:
    def __init__(self):
        self.database_url = getattr(settings, 'PAPER_DATABASE_URL', '')
        self.client = MongoClient(self.database_url)
        self.database = self.client['papers']

    def insert_update(self, data):
        if not self.database['papers'].find_one({'id': data['id']}):
            self.database['papers'].insert_one(data)


class CensorShipModule:
    def __init__(self):
        self.block_keywords = []

    def check_block_keyword(self):
        pass
