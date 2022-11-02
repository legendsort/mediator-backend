from django.core.management.base import BaseCommand
from django.db import connections
import Paper.models
from Paper.models import Publisher, Journal, Language
from Account.message import Error
from Account.services import GatewayService
from Bank.task import run_fetch_bank_data
from Account.schedules import run_async_notify_scan, run_async_data_scan
import json
from phpserialize import unserialize
from Account.schedules import run_remove_chat_history


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        run_remove_chat_history()
        # gateway_service = GatewayService()
        # gateway_service.send_request(action='upload_resource', data={
        #     'user': 'paper_id',})


def convert_publisher():
    with connections['old'].cursor() as cursor:
        cursor.execute("SELECT name, url FROM publishers")
        rows = cursor.fetchall()

        for row in rows:
            if Publisher.objects.filter(name=row[0]).exists():
                publisher = Publisher.objects.get(name=row[0])
                publisher.site_address = row[1]
            else:
                publisher = Publisher()
                publisher.name = row[0]
                publisher.site_address = row[1]
            publisher.save()


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def convert_journals():
    with connections['old'].cursor() as cursor:
        field = {
          "language_ids": "a:1:{i:0;i:16;}",
          "product_ids": "a:6:{i:0;i:40;i:1;i:11;i:2;i:48;i:3;i:9;i:4;i:20;i:5;i:50;}",
          "category_ids": "a:6:{i:0;i:330;i:1;i:330;i:2;i:242;i:3;i:330;i:4;i:214;i:5;i:330;}",
        }
        cursor.execute("SELECT *  FROM journals")
        rows = dictfetchall(cursor)
        for row in rows:
            try:
                if Journal.objects.filter(name=row['name']).exists():
                    continue
                    # journal = Journal.objects.get(name=row['name'])
                else:
                    journal = Journal()
                    journal.name = row['name']
                journal.description = row['description']
                journal.issn = row['issn']
                journal.eissn = row['eissn']
                journal.open_access = True if int(row['open_access']) else False
                journal.impact_factor = row['impact_factor']
                journal.url = row['url']
                journal.issues_per_year = row['issues_per_year']
                journal.start_year = row['start_year']
                journal.flag = True if int(row['flag']) else False
                language_ids = unserialize_ids(row['language_ids'])
                product_ids = unserialize_ids(row['product_ids'])
                category_ids = unserialize_ids(row['category_ids'])

                cursor.execute("SELECT *  FROM publishers WHERE id=%s", [row['publisher_id']])
                publisher = cursor.fetchone()
                try:
                    publisher = get_publisher(name=publisher[1])
                except Exception as e:
                    print(e)
                journal.publisher = publisher
                cursor.execute("SELECT *  FROM frequencies WHERE id=%s", [row['frequency_id']])
                frequency = cursor.fetchone()
                try:
                    frequency = get_frequency(name=frequency[1], description=frequency[2])
                except Exception as e:
                    print(e)
                journal.frequency = frequency
                country = Paper.models.Country.objects.get(name=row['country']) if Paper.models.Country.objects.filter(name=row['country']).exists() else None
                journal.country = country
                journal.save()
                journal.assign_language(language_ids)
                journal.assign_product(product_ids)
                journal.assign_category(category_ids)
                print(journal)
            except Exception as e:
                print(e)


def unserialize_ids(ids: str):
    try:
        output = unserialize(ids.encode('utf-8'))
        output = [
            val.decode() if isinstance(val, bytes) else val
            for key, val in output.items()
        ]
        return output
    except Exception as e:
        print(e)
        return []


def get_frequency(name, description=None):
    try:
        if Paper.models.Frequency.objects.filter(name=name).exists():
            frequency = Paper.models.Frequency.objects.get(name=name)
        else:
            frequency = Paper.models.Frequency(name=name, description=description)
            frequency.save()
        return frequency
    except Exception as e:
        print(e)
        return False


def get_publisher(name):
    try:
        if Paper.models.Publisher.objects.filter(name=name).exists():
            publisher = Paper.models.Publisher.objects.get(name=name)
        else:
            return False
        return publisher
    except Exception as e:
        print(e)
        return False


def get_category(name):
    try:
        if Paper.models.Publisher.objects.filter(name=name).exists():
            publisher = Paper.models.Publisher.objects.get(name=name)
        else:
            return False
        return publisher
    except Exception as e:
        print(e)
        return False


def get_product_type(name):
    try:
        if Paper.models.ProductType.objects.filter(name=name).exists():
            product = Paper.models.ProductType.objects.get(name=name)
        else:
            return False
        return product
    except Exception as e:
        print(e)
        return False


def convert_language():
    with connections['old'].cursor() as cursor:
        cursor.execute("SELECT * FROM languages")
        rows = dictfetchall(cursor)
        for row in rows:
            if Language.objects.filter(code=row['code']).exists():
                language = Language.objects.get(code=row['code'])
                language.code = row['code']
            else:
                language = Language(name=row['code'], code=row['code'])
            language.save()


def convert_others():
    pass

