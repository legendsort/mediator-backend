import datetime
import hashlib
import django.conf
import rest_framework.parsers
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from Bank.serializers import DataSerializer
from Bank.models import Data, DataType
from Bank.service import BankService
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware
from Paper.render import JSONResponseRenderer
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class DataViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DataSerializer
    queryset = Data.objects.all().order_by('-real_data_created_at')
    renderer_classes = [JSONResponseRenderer, ]
    pagination_class = StandardResultsSetPagination

    @action(detail=False, url_path='latest')
    def get_latest_data(self, request):
        try:
            data = Data.objects.order_by('-real_data_created_at')[:1]
            if not len(data):
                return JsonResponse({
                    'response_code': True,
                    'message': 'There is no data',
                    'data': []
                })

            if self.request.query_params.get('datetime', None):
                start_datetime = parse_datetime(self.request.query_params.get('datetime', None))
                # start_datetime = make_aware(start_datetime)
                end_datetime = start_datetime + datetime.timedelta(seconds=1)
                data = Data.objects.filter(real_data_created_at__range=(start_datetime, end_datetime))
            else:
                latest_datetime = data[0].real_data_created_at
                start_datetime = latest_datetime - datetime.timedelta(minutes=1)
                data = Data.objects.filter(real_data_created_at__in=[start_datetime, latest_datetime])
            result = []
            for ele in data:
                result.append(DataSerializer(ele).data)
            return JsonResponse({
                'response_code': True,
                'message': 'Fetched!',
                'data': result
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'message': 'server has error!'
            })

    @action(detail=False, url_path='time-list')
    def get_time_list(self, request):
        try:
            start_date = parse_datetime(self.request.query_params.get('select_date'))
            end_datetime = start_date + relativedelta(days=1)
            data = Data.objects.filter(real_data_created_at__gte=start_date, real_data_created_at__lt=end_datetime)
            time_list = {}
            for ele in data:
                time_list[str(ele.real_data_created_at)] = True
            return JsonResponse({
                'response_code': True,
                'message': 'Fetched!',
                'data': [time for time in time_list]
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'message': 'server has error!'
            })

    @action(detail=False, url_path='logs')
    def get_logs(self, request):
        try:
            page_number = request.query_params.get('pageNumber', 1)
            page_size = request.query_params.get('pageSize', 10)
            bank = BankService()
            response_code, response_data = bank.fetch_crawling_logs(params={
                'pageNumber': page_number,
                'pageSize': page_size
            })
            return JsonResponse({
                'response_code': response_code,
                'message': response_data if not response_code else response_data['message'],
                'data': [] if not response_code else response_data['data'],
                'pageNumber': 0 if not response_code else response_data['pageNumber'],
                'pageSize': 0 if not response_code else response_data['pageSize'],
                'totalPages': 0 if not response_code else response_data['totalPages'],
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'message': 'server has error!'
            })
