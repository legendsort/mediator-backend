import datetime
import hashlib
import django.conf
import rest_framework.parsers
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from Bank.serializer import DataSerializer
from Bank.models import Data, DataType
from Bank.service import BankService
from django.utils import timezone


class DataViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DataSerializer
    queryset = Data.objects.all().order_by('-real_data_created_at')

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
            latest_datetime = data[0].real_data_created_at
            start_datetime = latest_datetime - datetime.timedelta(minutes=1)
            data = Data.objects.filter(real_data_created_at__gte=start_datetime,
                                       real_data_created_at__lte=latest_datetime)
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

    @action(detail=False, url_path='logs')
    def get_logs(self, request):
        try:
            page_number = request.data.get('pageNumber', 1)
            page_size = request.data.get('pageSize', 10)
            bank = BankService()
            response_code, response_data = bank.fetch_crawling_logs(params={
                'pageNumber': page_number,
                'pageSize': page_size
            })
            return JsonResponse({
                'response_code': response_code,
                'message': response_data if not response_code else response_data['message'],
                'data': [] if not response_code else response_data['data']
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'message': 'server has error!'
            })
