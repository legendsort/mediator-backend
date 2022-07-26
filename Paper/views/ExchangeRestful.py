import django.db.utils
from django.http import JsonResponse
import json
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
import Paper.serializers
from Paper.models import Journal, Status, Resource, Exchange
from Paper.serializers import ExchangeListSerializer, ExchangeDetailSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Paper.helper import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_tricks import filters
from Paper.helper import filter_params
from Account.models import BusinessType
from django.apps import apps
from django.db.models import Q
from Paper.policies import RequestAccessPolicy
from Paper.services.ExchangeService import ExchangeService
import mimetypes
from django.http import HttpResponse
import os


class ExchangeFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    id = django_filters.CharFilter(method='search_by_order_id', lookup_expr='icontains')    
    start_updated_at = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gt')
    end_updated_at = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lt')
    status = django_filters.CharFilter(method='search_by_status_id', lookup_expr='icontains')
    type = django_filters.CharFilter(method='search_by_type', lookup_expr='icontains')
    dealer = django_filters.CharFilter(method='search_by_dealer', lookup_expr='icontains')

    class Meta:
        model = Exchange
        fields = {
            'title': ['icontains']
        }

    @staticmethod
    def search_by_order_id(queryset, name, value):
        return queryset.filter(order__id=value)

    @staticmethod
    def search_by_status_id(queryset, name, value):
        status_id = Status.objects.get(id=value)
        return queryset.filter(order__status_id=status_id) 

    @staticmethod
    def search_by_type(queryset, name, value): 
        return queryset.filter(order__type_id=value)     

    @staticmethod
    def search_by_dealer(queryset, name, value): 
        return queryset.filter(dealer__username=value)                      


class ExchangeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Exchange
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer]
    filterset_class = ExchangeFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = {
        'id': 'id',
        'title': 'title',
        'updated_at': 'updated_at',
        'order': 'order',
        'dealer': 'dealer'
    }
    ordering = ['-updated_at']

    def get_base_data(self):
        return filter_params(self.request.data, [
            'title',
            'detail',
            'purpose',
            'additional_info',
            'site_url',
            'attachment'
        ])

    def get_queryset(self):
        auth_user = self.request.user
        if auth_user.is_superuser:
            return Exchange.objects.filter()
        elif auth_user.has_perm('view_exchange'):
            return Exchange.objects.filter(order__user=auth_user, )
        elif auth_user.has_perm('manage_exchange'):
            return Exchange.objects.filter(Q(dealer=auth_user) | Q(dealer=None))
        else:
            return Exchange.objects.filter(pk=None)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExchangeDetailSerializer
        return ExchangeListSerializer

    def create(self, request, *args, **kwargs):
        try:
            base_data = self.get_base_data()
            serializer = ExchangeDetailSerializer(data=base_data)
            if serializer.is_valid():
                serializer.save()
                user = request.user
                instance = serializer.instance
                status = Status.objects.get(name='Requested')
                instance.set_order(user=request.user, status=status)
                instance.update_status(Status.objects.get(name='Requested'),
                                       message=f"Exchange has been started by {user.username}")
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
        except Status.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create Status instance'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create Resource'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            order = instance.get_order()
            if order.status != Status.objects.get(name='Requested'):
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': 'This request could not update content'
                })
            serializer = ExchangeDetailSerializer(instance, data=self.get_base_data(), partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': serializer.errors
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Request has been updated'
            })
            pass
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'server has error'
            })

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
                'message': 'Can not remove this  instance'
            })
            
    # accept request
    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        instance = self.get_object()
        try:
            user = request.user
            instance.dealer = user
            instance.update_status(Status.objects.get(name='Accepted'),
                                   message=f"Exchange has been started by {user.username}")
            instance.save()
            return JsonResponse({
                'response_code': True,
                'data': self.get_serializer(instance).data,
                'message': 'Exchange has been accepted'
            })
        except Status.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': f"RequestStatus has no Accepted status"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })

    # accept request
    @action(detail=True, methods=['post'], url_path='send')
    def send(self, request, pk=None):
        instance = self.get_object()
        try:
            ex_service = ExchangeService(instance)
            res_data = ex_service.send()
            if res_data:
                return JsonResponse(res_data)
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': "Sending failed"
                })
        except Status.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': f"RequestStatus has no Accepted status"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })

    # accept request

    @action(detail=True, methods=['GET'], url_path='download')
    def download(self, request, pk=None):
        instance = self.get_object()
        try:
            ex_service = ExchangeService(instance)
            ex_service.make_zip_file()
            if os.path.exists(ex_service.zip_file_path):
                with open(ex_service.zip_file_path, 'rb') as fh:
                    mimetype, _ = mimetypes.guess_type(ex_service.zip_file_path)
                    response = HttpResponse(fh.read(), content_type=mimetype)
                    response['Content-Length'] = os.path.getsize(ex_service.zip_file_path)
                    response['Content-Disposition'] = "attachment; filename={}".format(
                        os.path.basename(ex_service.zip_file_path))
                    return response
        except Status.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': f"RequestStatus has no Accepted status"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })
    # accept request
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        instance = self.get_object()
        try:
            user = request.user
            instance.dealer = user            
            instance.update_status(Status.objects.get(name='Canceled'),
                                   message=f"{request.data.get('message')}")
            instance.save()
            return JsonResponse({
                'response_code': True,
                'data': self.get_serializer(instance).data,
                'message': 'RequestStatus has been accepted'
            })
        except Status.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': f"RequestStatus has no Accepted status"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        instance = self.get_object()
        try:
            user = request.user
            instance.dealer = user
            instance.update_status(Status.objects.get(id=request.data.get('status')),
                                   message=f"{request.data.get('message')}")
            instance.save()
            return JsonResponse({
                'response_code': True,
                'data': self.get_serializer(instance).data,
                'message': 'Exchange has been accepted'
            })
        except Status.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': f"Exchange has no Accepted status"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })
