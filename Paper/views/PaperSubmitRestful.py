import django.db.utils
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

    def create(self, request, *args, **kwargs):
        try:
            base_data = self.get_base_data()
            serializer = self.serializer_class(data=base_data)
            if serializer.is_valid():

                serializer.save()
                instance = serializer.instance
                instance.user = request.user
                instance.save()
            else:
                print(serializer.errors)
                return JsonResponse({
                    'response_code': False,
                    'data': serializer.errors,
                    'message': 'Duplicated name'
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Successfully created!'
            })
        except Exception as e:
            print('----', e)
            if instance:
                instance.delete()
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create journal'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = JournalSerializer(instance, data=self.get_base_data(), partial=True)
            if serializer.is_valid():
                if request.data.getlist('products') is not []:
                    instance.assign_product(request.data.getlist('products'))
                if request.data.getlist('countries') is not []:
                    instance.assign_country(request.data.getlist('countries'))
                if request.data.getlist('categories') is not []:
                    instance.assign_category(request.data.getlist('categories'))
                if request.data.get('review_type') and ReviewType.objects.filter(
                        pk=int(request.data.get('review_type'))).exists():
                    instance.review_type = ReviewType.objects.get(pk=int(request.data.get('review_type')))
                if request.data.get('frequency') and Frequency.objects.filter(
                        pk=int(request.data.get('frequency'))).exists():
                    instance.frequency = Frequency.objects.get(pk=int(request.data.get('frequency')))
                if request.data.get('publisher') and Publisher.objects.filter(
                        pk=int(request.data.get('publisher'))).exists():
                    instance.publisher = Publisher.objects.get(pk=int(request.data.get('publisher')))
                serializer.save()
                instance.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': serializer.errors
                })
            return JsonResponse({
                'response_code': False,
                'data': serializer.data,
                'message': 'Duplicated name'
            })
            pass
        except Exception as e:
            print(e)
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

