import datetime
import hashlib
import django.conf
import rest_framework.parsers
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from Account.serializers import UserListSerializer, RoleSerializer, UserDetailSerializer, UserOutSideSerializer, UserManageUnitSerializer
from Account.models import User, Role, Unit, CustomerProfile
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from Paper.helper import StandardResultsSetPagination
from Paper.render import JSONResponseRenderer
from rest_framework_tricks.filters import OrderingFilter
from Account.policies import UserAccessPolicy
from Account.views import MyTokenObtainPairSerializer
from django.db.models import Q


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    real_name = django_filters.CharFilter(field_name='real_name', lookup_expr='icontains')
    start_created_at = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gt')
    end_created_at = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lt')
    role = django_filters.ModelMultipleChoiceFilter(field_name='role', queryset=Role.objects.all())
    unit = django_filters.ModelMultipleChoiceFilter(field_name='unit', queryset=Unit.objects.all())
    is_active = django_filters.CharFilter(field_name='is_active', lookup_expr='exact')
    class Meta:
        model = User
        fields = {
            'username': ['icontains'],
        }


class UserViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, UserAccessPolicy]
    filterset_class = UserFilter
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = {
        'real_name': 'real_name'
    }
    ordering = ['created_at']

    def get_queryset(self):
        if self.action == 'update' or self.action == 'partial_update' or self.action == 'update_profile':
            if self.request.user.is_superuser:
                return User.objects.exclude(Q(is_remove=True))
            else:
                return User.objects.filter(pk=self.request.user.pk)
        if self.request.user.is_superuser:
            return User.objects.exclude(Q(is_remove=True) | Q(is_superuser=True)).distinct()
        elif self.request.user.has_perm('manage_unit'):
            return User.objects.exclude(pk=self.request.user.pk).filter(unit=self.request.user.unit)

        return User.objects.filter(pk=None)

    def get_serializer_class(self):
        auth_user = self.request.user
        if self.action == 'get_self_info':
            return UserDetailSerializer
        if auth_user.is_superuser and self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'create':
            return UserDetailSerializer
        if (self.action == 'list' or self.action == 'retrieve') and not auth_user.is_superuser and auth_user.has_perm('manage_unit'):
            return UserManageUnitSerializer
        return UserListSerializer

    def create(self, request,  *args, **kwargs):
        try:
            serializer = UserDetailSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                instance = serializer.instance
                if request.data.get('role') and request.data.get('role')['id']:
                    instance.role = Role.objects.get(pk=request.data.get('role')['id'])
                    instance.save()
                if request.data.get('unit') and request.data.get('unit')['id']:
                    instance.unit = Unit.objects.get(pk=request.data.get('unit')['id'])
                    instance.save()
                instance.save()
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
        except Role.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Role does not exist'
            })
        except Unit.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Unit does not exist'
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
            serializer = UserDetailSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                instance = serializer.instance
                if request.data.get('role') and request.data.get('role')['id']:
                    instance.role = Role.objects.get(pk=request.data.get('role')['id'])
                    instance.save()
                if request.data.get('unit') and request.data.get('unit')['id']:
                    instance.unit = Unit.objects.get(pk=request.data.get('unit')['id'])
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
        except Role.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Role does not exist'
            })
        except Unit.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Unit does not exist'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'server has error'
            })

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance == request.user:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': 'You can not remove yourself'
                })
            instance.is_active = False
            instance.is_remove = True
            instance.save()
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

    @action(detail=False, url_path='get-self-info')
    def get_self_info(self, request):
        try:
            user = self.request.user
            return JsonResponse({
                'response_code': True,
                'data': UserDetailSerializer(user).data
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'message': 'server has error!'
            })

    @action(detail=True, methods=['put'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.set_password('12345678')
            instance.save()
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': 'Successfully reset!'
            })
        except django.db.DatabaseError:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Reset password failed'
            })
        pass

    @action(detail=True, url_path='change-password')
    def change_password(self, request):
        pass

    @action(detail=True, url_path='profile', methods=['put'])
    def update_profile(self, request, pk=None):
        try:
            instance = self.get_object()
            profile = instance.profile if instance.profile else CustomerProfile()
            profile.position = request.data.get('position', profile.position)
            profile.department = request.data.get('department', profile.department)
            profile.save()
            if request.data.get('profile_remote_account'):
                remote_accounts = request.data.get('profile_remote_account')
                profile.assign_remote_user_list(remote_accounts)
            instance.profile = profile
            instance.save()
            return JsonResponse({
                'response_code': True,
                'data': UserDetailSerializer(instance).data,
                'message': 'Successfully update profile!'
            })
        except django.db.DatabaseError:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Update profile failed'
            })

    @action(detail=False, url_path='check-password', methods=['post'])
    def check_password(self, request, pk=None):
        try:
            user = self.request.user
            password = request.data.get('password')
            user.check_password(password)
            return JsonResponse({
                'response_code': user.check_password(password),
                'data': [],
                'message': 'Checked'
            })
        except django.db.DatabaseError:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Update profile failed'
            })

    @action(detail=False, url_path='change-password', methods=['post'])
    def change_password(self, request, pk=None):
        try:
            user = self.request.user
            password = request.data.get('newPassword')
            print(password, request.data.get('oldPassword'))
            if user.check_password(request.data.get('oldPassword')):
                user.set_password(password)
                user.save()
            return JsonResponse({
                'response_code': user.check_password(request.data.get('newPassword')),
                'data': [],
                'message': 'Changed'
            })
        except django.db.DatabaseError:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Change failed'
            })

    @action(detail=False, url_path='fetch-transfers', methods=['get'])
    def fetch_transfers(self, request, pk=None):
        try:
            user = self.request.user
            users = User.objects.filter(role__permissions__codename__in=['manage_paper', 'mediate_paper']).exclude(pk=user.pk)
            return JsonResponse({
                'response_code': True,
                'data': UserOutSideSerializer(users, many=True).data,
                'message': 'Changed'
            })
        except django.db.DatabaseError:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Change failed'
            })

    @action(detail=False, url_path='create-user', methods=['post'])
    def create_user(self, request):
        try:
            serializer = UserManageUnitSerializer(data=request.data)
            auth_user = request.user
            unit = auth_user.unit
            role = auth_user.get_role_of_user()
            if serializer.is_valid():
                serializer.save()
                instance = serializer.instance
                instance.unit = unit
                instance.role = role
                instance.save()
                if request.data.get('position', None) or request.data.get('department', None):
                    profile = CustomerProfile(position=request.data.get('position'), department=request.data.get('department'))
                    profile.save()
                    instance.profile = profile
                    instance.save()

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

    @action(detail=True, url_path='update-user', methods=['put'])
    def update_user(self, request, pk=None):
        try:
            instance = self.get_object()
            auth_user = request.user
            if not auth_user.is_superuser and auth_user.unit != instance.unit:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': 'You have no permission with this action. Please contact administrator'
                })
            serializer = UserManageUnitSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                instance = serializer.instance
                if request.data.get('position', None) or request.data.get('department', None):
                    profile = instance.profile
                    if not profile:
                        profile = CustomerProfile(position=request.data.get('position'),
                                                  department=request.data.get('department'))
                    else:
                        profile.position = request.data.get('position', profile.position)
                        profile.department = request.data.get('department', profile.department)
                    profile.save()
                    instance.profile = profile
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
