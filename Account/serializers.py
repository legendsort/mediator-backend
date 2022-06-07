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
    businesses = BusinessSerializer(many=True, read_only=True)

    class Meta:
        model = Unit
        fields = [
            'id',
            'name',
            'address',
            'phone_number',
            'super_origination',
            'created_at',
            'businesses'
        ]


# User serializer
class UserListSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)
    unit = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role',
            'is_active',
            'ip_address',
            'is_online',
            'real_name',
            'created_at',
            'unit',
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
    unit = UnitSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role',
            'username',
            'role',
            'is_active',
            'ip_address',
            'phone_number',
            'is_online',
            'real_name',
            'unit',
        ]

