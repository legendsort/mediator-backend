from rest_framework import serializers
from Account.models import Role, Permission, User, BusinessType, Unit, CustomerProfile, RemoteAccount, Notice, Post, Comment
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


class RemoteAccountSerializer(serializers.ModelSerializer):
    journal = serializers.PrimaryKeyRelatedField(read_only=True)
    type = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RemoteAccount
        fields = [
            'id',
            'username',
            'password',
            'host',
            'updated_at',
            'journal',
            'type',
        ]


# Customer Profile serializer
class CustomerProfileSerializer(serializers.ModelSerializer):
    profile_remote_account = RemoteAccountSerializer(many=True, read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'id',
            'position',
            'department',
            'profile_remote_account'
        ]


class ProfileSerializer(serializers.RelatedField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        if isinstance(value, CustomerProfile):
            serializer = CustomerProfileSerializer(value)
        else:
            return None
        return serializer.data


class UnitSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
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
            'is_online',
            'real_name',
            'role'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role',
            'is_active',
            'ip_address',
            'phone_number',
            'is_online',
            'real_name',
            'unit',
            'profile',
        ]


class UserManageUnitSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField(read_only=True)
    department = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'is_active',
            'ip_address',
            'phone_number',
            'is_online',
            'real_name',
            'position',
            'department'
        ]

    @staticmethod
    def get_position(obj):
        profile = obj.profile
        if isinstance(profile, CustomerProfile):
            return profile.position
        else:
            return None

    @staticmethod
    def get_department(obj):
        profile = obj.profile
        if isinstance(profile, CustomerProfile):
            return profile.department
        else:
            return None


#
class NoticeSerializer(serializers.ModelSerializer):
    receiver = serializers.StringRelatedField(read_only=True)
    sender = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Notice
        fields = [
            'id',
            'content',
            'receiver',
            'sender',
            'additional_info',
            'is_read',
            'is_highlight',
            'created_at'
        ]


#
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'content',
            'created_at',
            'user',
        ]


#
class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    comments = CommentSerializer(source='get_comments', many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'author',
            'body',
            'comments',
            'created_at'
        ]
