import json

import django.db.utils
import rest_framework.exceptions
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
import Paper.serializers
from Paper.models import Journal, Publisher, Country, ReviewType, Submit, UploadFile, Requirement,\
    Order, Frequency, Article
from Paper.serializers import JournalSerializer, PublisherSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Bank.views import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_tricks import filters
from Paper.policies import PublisherAccessPolicy
from Paper.helper import filter_params


# Order API
class OrderFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Order
        fields = {
            'id': ['icontains']
        }


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.OrderSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = OrderFilter
    queryset = Order.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            self.perform_destroy(self.get_object())
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': 'Successfully removed!'
            })
        except django.db.DatabaseError:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Can not remove this publisher'
            })


# Submit API
class SubmitFilter(django_filters.FilterSet):

    class Meta:
        model = Submit
        fields = {
            'id': ['exact', ]
        }


class SubmitViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.SubmitSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = SubmitFilter
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    queryset = Submit.objects.all()

    def get_base_data(self):
        return filter_params(self.request.data, [
            'title',
            'article_id',
        ])

    # new submit paper request
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                request_data = request.data
                journal_id = request_data.get('journal_id')
                article_id = request_data.get('article_id')
                authors = request.data.get('authors')
                upload_files = request.data.getlist('files')
                upload_files_key = request.data.getlist('files_requirement')
                if not journal_id or not Journal.objects.filter(pk=journal_id).exists():
                    raise ValidationError('journal_id')
                if not article_id or not Article.objects.filter(pk=article_id).exists():
                    raise ValidationError('article_id')
                if not authors or type(authors) is not str:
                    raise ValidationError('authors')
                if not upload_files:
                    raise ValidationError('upload_files')
                serializer.save()
                instance = serializer.instance
                instance.article = Article.objects.get(pk=article_id)
                instance.journal = Journal.objects.get(pk=journal_id)
                authors = json.loads(authors)
                result = instance.set_authors(authors)

                if len(result):
                    instance.delete()
                    return JsonResponse({
                        'response_code': False,
                        'data': result,
                        'message': 'Your submit has some errors. Please check details'
                    })
                instance.set_upload_files(upload_files, upload_files_key)
                instance.user = request.user
                instance.save()
            else:
                print(serializer.errors)
                return JsonResponse({
                    'response_code': False,
                    'data': serializer.errors,
                    'message': 'Your submit has some errors. Please check details'
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Successfully created!'
            })
        except ValidationError as e:
            return JsonResponse({
                'response_code': False,
                'data': str(e.message),
                'message': f"Your submit has some errors. Please check details {str(e.message)}"
            })
        except Exception as e:
            print('----', e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create journal'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Duplicated name'
            })
        except django.http.response.Http404:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Not Found'
            })
        except Exception as e:
            print(type(e))
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'server has error'
            })

    # remove journal element
    def destroy(self, request, *args, **kwargs):
        try:
            self.perform_destroy(self.get_object())
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': 'Successfully removed!'
            })
        except django.db.DatabaseError as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Can not remove this publisher'
            })

