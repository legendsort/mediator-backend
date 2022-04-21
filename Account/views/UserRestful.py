import datetime
import hashlib
import django.conf
import rest_framework.parsers
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from Account.serializers import UserSerializer, RoleSerializer, UserDetailSerializer
from Account.models import User
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from Paper.helper import StandardResultsSetPagination
from Paper.render import JSONResponseRenderer
from rest_framework_tricks.filters import OrderingFilter
from Account.policies import UserAccessPolicy
from Account.views import MyTokenObtainPairSerializer


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')

    class Meta:
        model = User
        fields = {
            'username': ['icontains']
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

    def get_serializer_class(self):
        if self.action == 'get_self_info':
            return UserDetailSerializer
        return UserSerializer

    def get_queryset(self):
        return User.objects.exclude(is_remove=True)

    @action(detail=False, url_path='get-self-info')
    def get_self_info(self, request):
        try:
            user = self.request.user
            token = MyTokenObtainPairSerializer.get_token(user)
            print(token)
            return JsonResponse({
                'response_code': True,
                'data': {
                    'username': user.username if user.username is not None else '',
                    'role': RoleSerializer(user.role).data

                }
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'message': 'server has error!'
            })
