from django.conf import settings
import glob
from time import sleep
from Account.services import NotificationService, NotifyParserService
import json


def run_async_notify_scan():
    try:
        SCAN_FOLDER_PATH = getattr(settings, 'NIS_RECEIVE_DIR_PATH')
        path = f"{SCAN_FOLDER_PATH}/*.json"
        files = glob.glob(path, recursive=True)
        for file_path in files:
            with open(file_path) as res_file:
                data_loaded = json.load(res_file)
                if data_loaded['notification']:
                    parser = NotifyParserService(data=data_loaded, mode=data_loaded['mode'], file_path=file_path)
                    parser.run()
        return True
    except Exception as e:
        print(e)
        return False
