import django.db
from django.core.management.base import BaseCommand

import Paper.models
from Account.message import Error
from Account.services import GatewayService
from Bank.task import run_fetch_bank_data


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        gateway_service = GatewayService()
        gateway_service.send_request(action='upload_resource', data={
            'user': 'paper_id',})

