import datetime
import hashlib
import django.conf
import rest_framework.parsers
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from Account.serializer import UserSerializer, RoleSerializer
from Account.models import User


class UserViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.exclude(is_remove=False)

    @action(detail=False, url_path='get-self-info')
    def get_self_info(self, request):
        try:
            user = self.request.user
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
