from rest_framework import serializers
from Account.models import Role, Permission, User, BusinessType, Unit
from django.apps import apps


# permission
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', ]


# roles
class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'codename', 'permissions']


# Business type
class BusinessSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessType
        fields = ['id', 'name', 'codename', 'description', ]


# Unit
class UnitSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Unit
        fields = ['id', 'name', 'address', 'super_origination', 'created_at', 'updated_at']


# User serializer
class UserSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role'
        ]


class UserOutSideSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role'
        ]

