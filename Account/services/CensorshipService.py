from django.conf import settings
import pyzipper
from os.path import basename
import os
import zipfile
import re
from Paper.models import Order
from django.utils import timezone
from django.core.files import File


class CensorshipService:
    def __init__(self):
        self.DEPLOY_TEMP_FOLDER_PATH = getattr(settings, 'DEPLOY_TEMP_FOLDER_PATH')
        self.DEPLOY_ZIP_PASSWORD = 'qwe'

    def deploy(self, file_path):
        extract_folder_path = f"{self.DEPLOY_TEMP_FOLDER_PATH}/{os.path.splitext(basename(file_path))[0]}"
        zip_path = f"{self.DEPLOY_TEMP_FOLDER_PATH}/{basename(file_path)}"
        match = re.search(r'__\d+', file_path)
        if match:
            order_id = match.group().replace('__', '')
            try:
                order = Order.objects.get(pk=9)
                with pyzipper.AESZipFile(file_path) as zf:
                    zf.setpassword(str.encode(self.DEPLOY_ZIP_PASSWORD))
                    zf.extractall(extract_folder_path, pwd=str.encode(self.DEPLOY_ZIP_PASSWORD))
                    zf.close()
                if self.zip_directory(extract_folder_path, zip_path):
                    with open(zip_path, 'rb') as f:
                        order.censor_file = File(f)
                        order.download_at = timezone.now()
                        order.save()
                        f.close()
                        os.remove(file_path)
                        os.remove(zip_path)
            except Order.DoesNotExist:
                pass

    @staticmethod
    def zip_directory(folder_path, zip_path):
        with zipfile.ZipFile(zip_path, mode='w') as zf:
            len_dir_path = len(folder_path)
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zf.write(file_path, file_path[len_dir_path:])
                    os.remove(file_path)
            zf.close()
            os.rmdir(folder_path)
            return True

    def censorship(self):
        pass
