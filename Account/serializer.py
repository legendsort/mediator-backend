from rest_framework import serializers
from Account.models import Role, Permission, User
from django.apps import apps


# permission
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', ]


# roles
class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'codename', 'permissions']


# User serializer
class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role'
        ]
