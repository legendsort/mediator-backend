import django.db
from django.core.management.base import BaseCommand

import Paper.models
from Account.message import Error
from Account.services import GatewayService
from Bank.task import run_fetch_bank_data
from Account.schedules import run_async_notify_scan, run_async_data_scan


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        run_async_data_scan()
        # gateway_service = GatewayService()
        # gateway_service.send_request(action='upload_resource', data={
        #     'user': 'paper_id',})

