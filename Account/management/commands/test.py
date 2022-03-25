from django.core.management.base import BaseCommand
from Account.message import Error
from Bank.task import run_fetch_bank_data


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        run_fetch_bank_data()
