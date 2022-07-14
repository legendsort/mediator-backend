import django.db.utils
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
import Account.serializers
from Account.models import BusinessType, Unit, Permission, Role, Notice, User, Post, Comment
from Account.serializers import BusinessSerializer, UserOutSideSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Paper.helper import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from Account.policies import PermissionAccessPolicy, UnitAccessPolicy
from rest_framework_tricks import filters
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action


# BusinessType API
class BusinessTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = BusinessType
        fields = {
            'name': ['icontains']
        }


class BusinessTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = BusinessSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = BusinessTypeFilter
    queryset = BusinessType.objects.all()

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


# Unit API
class UnitFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    start_created_at = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gt')
    end_created_at = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lt')
    businesses = django_filters.ModelMultipleChoiceFilter(field_name='businesses', queryset=BusinessType.objects.all())

    class Meta:
        model = Unit
        fields = {
            'name': ['icontains']
        }


class UnitViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, UnitAccessPolicy]
    serializer_class = Account.serializers.UnitSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = UnitFilter
    queryset = Unit.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = Account.serializers.UnitSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                businesses = request.data.get('businesses')
                unit = serializer.instance
                unit.assign_business(businesses)
                unit.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': serializer.errors,
                    'message': 'Validation error'
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Successfully created!'
            })
        except Exception as e:
            print('----', e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create Role'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = Account.serializers.UnitSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                if request.data.get('businesses') is not []:
                    instance.assign_business(request.data.get('businesses'))
                serializer.save()
                instance.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': serializer.errors
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Journal has been updated'
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
                'message': 'Can not remove this instance'
            })


# Permission API
class PermissionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Permission
        fields = {
            'name': ['icontains']
        }


class PermissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermissionAccessPolicy]
    serializer_class = Account.serializers.PermissionSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = PermissionFilter
    queryset = Permission.objects.all()

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
                'message': 'Can not remove this instance'
            })


# Role API
class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    permissions = django_filters.ModelMultipleChoiceFilter(field_name='permissions', queryset=Permission.objects.all())

    class Meta:
        model = Role
        fields = {
            'name': ['icontains']
        }


class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermissionAccessPolicy]
    serializer_class = Account.serializers.RoleSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RoleFilter
    queryset = Role.objects.exclude(codename='administrator')

    def create(self, request,  *args, **kwargs):
        try:
            serializer = Account.serializers.RoleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                permissions = request.data.get('permissions')
                role = serializer.instance
                role.assign_permissions(permissions)
                role.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': serializer.errors,
                    'message': 'Validation error'
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Successfully created!'
            })
        except Exception as e:
            print('----', e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create Role'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = Account.serializers.RoleSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                if request.data.get('permissions') is not []:
                    instance.assign_permissions(request.data.get('permissions'))
                serializer.save()
                instance.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': serializer.errors
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Journal has been updated'
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
                'message': 'Can not remove this instance'
            })


# Notice
class NoticeFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(field_name='content', lookup_expr='icontains')
    user = django_filters.NumberFilter(method='search_by_user', lookup_expr='exact')

    class Meta:
        model = Notice
        fields = {
            'content': ['icontains']
        }

    @staticmethod
    def search_by_user(queryset, name, value):
        return queryset.filter(Q(receiver__id=value) | Q(sender__id=value))


class NoticeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Account.serializers.NoticeSerializer
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = NoticeFilter

    def get_queryset(self):
        user = self.request.user
        if self.action == 'get_contact_list':
            return Notice.objects.all()
        if user.is_superuser and self.request.query_params.get('all'):
            return Notice.objects.all()
        elif user.has_perm('manage_contest') or user.has_perm('manage_wipo') or user.has_perm('manage_paper') or user.has_perm('manage_bank'):
            return Notice.objects.filter(Q(sender=user) | Q(receiver=user))
        else:
            return Notice.objects.filter(Q(sender=user) | Q(receiver=user))

    def create(self, request,  *args, **kwargs):
        try:
            serializer = Account.serializers.NoticeSerializer(data=request.data)
            receiver = User.objects.get(pk=request.data.get('receiver'))
            sender = request.user
            if serializer.is_valid():
                serializer.save()
                instance = serializer.instance
                instance.sender = sender
                instance.receiver = receiver
                instance.save()
                instance.send_notice()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': serializer.errors,
                    'message': 'Validation error'
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Successfully created!'
            })
        except User.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'You have to select correct receiver'
            })

        except Exception as e:
            print('----', e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create Role'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_read = True
            instance.save()
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': 'Successfully created!'
            })
        except User.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'You have to select correct receiver'
            })

        except Exception as e:
            print('----', e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create Role'
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
                'message': 'Can not remove this instance'
            })

    @action(detail=False, url_path='get-contacts')
    def get_contact_list(self, request):
        try:
            user = request.user
            if user.is_superuser:
                users = User.objects.exclude(is_superuser=True, pk=user.pk)
            elif user.has_perm('manage_contest'):
                users = User.objects.filter(Q(role__permissions__codename='view_contest'))
            elif user.has_perm('manage_paper'):
                users = User.objects.filter(Q(role__permissions__codename='view_paper'))
            elif user.has_perm('manage_wipo'):
                users = User.objects.filter(Q(role__permissions__codename='view_wipo'))
            elif user.has_perm('manage_bank'):
                users = User.objects.filter(Q(role__permissions__codename='view_bank'))
            elif user.has_perm('view_contest'):
                users = User.objects.filter(Q(role__permissions__codename='manage_contest'))
            elif user.has_perm('view_paper'):
                users = User.objects.filter(Q(role__permissions__codename='manage_paper'))
            elif user.has_perm('view_wipo'):
                users = User.objects.filter(Q(role__permissions__codename='manage_wipo'))
            elif user.has_perm('view_bank'):
                users = User.objects.filter(Q(role__permissions__codename='manage_bank'))
            else:
                users = User.objects.filter(pk=None)
            print(users.count())
            return JsonResponse({
                'response_code': True,
                'data': UserOutSideSerializer(users, many=True).data,
                'message': 'Successfully removed!'
            })
        except Exception as e:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Server has error'
            })
