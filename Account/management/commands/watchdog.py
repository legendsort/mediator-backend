from django.core.management.base import BaseCommand
from Account.service import WatchService, Handler


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        watch = WatchService()
        watch.run()
        print('------>')
        watch.stop()

