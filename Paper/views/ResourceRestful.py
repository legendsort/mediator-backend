import django.db.utils
from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
import Paper.serializers
from Paper.models import Journal, Status, Resource
from Paper.serializers import ResourceUploadSerializer, ResourceDetailSerializer, ResourceUploadDetailSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Paper.helper import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_tricks import filters
from Paper.helper import filter_params
from Account.models import BusinessType
from rest_framework_tricks.filters import OrderingFilter
from django.apps import apps
from django.db.models import Q
from Paper.policies import RequestAccessPolicy


class ResourceFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    id = django_filters.CharFilter(method='search_by_order_id', lookup_expr='icontains')    
    start_updated_at = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gt')
    end_updated_at = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lt')
    status = django_filters.CharFilter(method='search_by_status_id', lookup_expr='icontains')
    type = django_filters.CharFilter(method='search_by_type', lookup_expr='icontains')
    dealer = django_filters.CharFilter(method='search_by_dealer', lookup_expr='icontains')

    class Meta:
        model = Paper.models.Resource
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


class ResourceUploadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.ResourceUploadSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer]
    filterset_class = ResourceFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    queryset = Resource.objects.filter(flag=True)
    ordering_fields = {
        'title': 'title',
        'id': 'id',
        'created_at': 'created_at'
    }
    ordering = ['created_at', 'title', 'id']

    def get_base_data(self):
        return filter_params(self.request.data, [
            'title',
            'detail',
            'created_at',
        ])

    def get_serializer_class(self):
        if self.action == 'createUpload':
            print("----serialize upload----")
            return ResourceUploadSerializer
        elif self.action == 'fetch' or self.action == 'fetchDetail':
            return ResourceUploadDetailSerializer
        return ResourceUploadSerializer
    
    def create(self, request, *args, **kwargs):
        instance = None
        try:
            base_data = self.get_base_data()
            serializer = ResourceUploadSerializer(data=base_data)
            codename = request.data.get('codename')
            if serializer.is_valid():
                serializer.save()
                instance = serializer.instance
                status = Status.objects.get(name='Requested')
                business_type = BusinessType.objects.get(codename=codename)
                instance.flag = 1
                order = instance.set_order(user=request.user, status=status, business_type=business_type)
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
                'message': 'Successfully normal resource created!'
            })
        except Status.DoesNotExist:
            if instance:
                instance.delete()
            pass
        except BusinessType.DoesNotExist:
            if instance:
                instance.delete()
            pass
        except Exception as e:
            print('----', e)
            if instance:
                instance.delete()
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create normal resource'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ResourceUploadSerializer(instance, data=self.get_base_data(), partial=True)
            if serializer.is_valid():
                order = instance.get_order()
                if order and order.status == Status.objects.get(name='Requested'):
                    codename = request.data.get('codename')
                    business_type = BusinessType.objects.get(codename = codename)
                    order.type = business_type
                    order.save()
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
                'message': 'Resource has been updated'
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
            
    # fetch resource
    @action(detail=False, methods=['get'], url_path='fetch')
    def fetch(self, request):
        try:
            serializer = ResourceUploadDetailSerializer(self.queryset, many=True)
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Successfully normal resource created!'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })

    # fetch resource
    @action(detail=True, methods=['get'], url_path='fetch-detail')
    def fetch_detail(self, request, pk=None):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': "Fetch succeed"
            })

        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })

    # upload resource create
    @action(detail=False, methods=['post'], url_path='create-upload')
    def create_upload(self, request):
        instance = None
        try:
            base_data = self.get_base_data()
            print(request.data)
            
            serializer = ResourceUploadSerializer(data=base_data)
            if serializer.is_valid():
                upload_files = request.data.getlist('files')
                codename = request.data.get('codename')
                # if not upload_files: 
                #     raise ValidationError('upload_files')
                
                serializer.save()
                instance = serializer.instance
                instance.user = request.user
                instance.set_upload_files(upload_files)
                instance.flag = 1
                instance.save()
                type = apps.get_model('Account.BusinessType').objects.get(codename=codename)
                status = Status.objects.get(name='New upload resource' if codename != 'contest' else 'Accepted')
                instance.set_order(request.user, status, type)
                pass
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
                'message': 'Successfully upload resource created!'
            })
        except Status.DoesNotExist:
            if instance:
                instance.delete()
            pass
        except BusinessType.DoesNotExist:
            if instance:
                instance.delete()
            pass
        except Exception as e:
            print('----', e)
            if instance:
                instance.delete()            
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed to create upload Resource'
            })

    # update resource status
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        instance = self.get_object()
        try:
            message = request.data.get('message')
            status_id = request.data.get('status_id')
            instance.update_status(Status.objects.get(pk=status_id), message=message)
            instance.save()
            return JsonResponse({
                'response_code': True,
                'data': self.get_serializer(instance).data,
                'message': 'Upload resource has been updated'
            })
        except Status.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Please submit correct status"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })
            

class ResourceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RequestAccessPolicy]
    serializer_class = Paper.serializers.ResourceSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer]
    filterset_class = ResourceFilter
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
            'updated_at',
            'id'
        ])

    def get_queryset(self):
        auth_user = self.request.user
        if auth_user.is_superuser:
            return Resource.objects.filter(flag=False)
        elif auth_user.has_perm('view_request'):
            return Resource.objects.filter(order__user=auth_user, flag=False)
        elif auth_user.has_perm('manage_request'):
            return Resource.objects.filter(Q(dealer=auth_user, flag=False) | Q(dealer=None, flag=False))
        else:
            return Resource.objects.filter(pk=None)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ResourceDetailSerializer
        return Paper.serializers.ResourceSerializer

    def create(self, request, *args, **kwargs):
        instance = None
        try:
            base_data = self.get_base_data()
            serializer = Paper.serializers.ResourceSerializer(data=base_data)
            if serializer.is_valid():
                serializer.save()
                user = request.user
                instance = serializer.instance
                status = Status.objects.get(name='Requested') 
                instance.set_order(user=request.user, status=status)
                instance.update_status(Status.objects.get(name='Requested'),
                                       message=f"RequestStatus has been started by {user.username}")
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
            if instance:
                instance.delete()
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create Status instance'
            })
        except BusinessType.DoesNotExist:
            if instance:
                instance.delete()
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create BusinessType instance'
            })
        except Exception as e:            
            if instance:
                instance.delete()            
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
            serializer = Paper.serializers.ResourceSerializer(instance, data=self.get_base_data(), partial=True)
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
                                   message=f"RequestStatus has been started by {user.username}")
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

    # accept request
    @action(detail=True, methods=['post'], url_path='pubcheck')
    def pub_check(self, request, pk=None):
        instance = self.get_object()
        try:
            user = request.user
            instance.dealer = user
            instance.update_status(Status.objects.get(name='Checking'),
                                   message=f"RequestStatus has been started by {user.username}")
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
