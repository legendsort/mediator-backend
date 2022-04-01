from Account.service import APIBaseService
from django.conf import settings


class FTPService(APIBaseService):

    def __init__(self, token):
        self.base_url = getattr(settings, 'MEDIATOR_SERVICE_API_BASE_URL', '')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain',
            'Authorization': f"Bearer {token}"
        }
        self.token = token

    def list(self):
        pass

    def remove(self):
        pass

    def rename(self):
        pass

    def move(self):
        pass

    def copy(self):
        pass

    def upload(self):
        pass

    def download(self):
        pass
