from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser, Permission
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from Account.managers import UserManager
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    codename = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    codename = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        through='Membership',
        through_fields=('role', 'permission'),
        blank=True,
    )

    def __str__(self):
        return self.name


class Membership(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=192, unique=True)
    real_name = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(default='0.0.0.0')
    is_online = models.BooleanField(default=False)
    is_remove = models.BooleanField(default=False)
    profile = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = UserManager()
    role = models.ForeignKey(Role, related_name='user_roles', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class CustomerProfile(models.Model):
    position = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    unit = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    users = GenericRelation(User, related_query_name='customer_profile')


