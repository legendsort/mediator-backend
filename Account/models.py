from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from Account.managers import UserManager
from django.utils.translation import gettext_lazy as _
import hashlib
from django.utils import timezone
from django.apps import apps
from Account.services.NotificationService import NotificationService


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Permission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    codename = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def get_codename(self) -> str:
        return self.codename


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

    def get_codename(self) -> str:
        return self.codename

    def assign_permissions(self, permissions):
        self.permissions.clear()
        for permission in permissions:
            try:
                permission = Permission.objects.get(pk=permission['id'])
                self.permissions.add(permission)
            except Permission.DoesNotExist:
                continue
        return True


class Membership(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['role', 'permission']


class BusinessType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    codename = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField(max_length=1024)


class Unit(models.Model):
    name = models.CharField(max_length=255, unique=True)
    super_origination = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    businesses = models.ManyToManyField(
        BusinessType,
        through='UnitBusiness',
        through_fields=('unit', 'business'),
        blank=True,
    )

    def __str__(self):
        return self.name

    def assign_business(self, businesses):
        self.businesses.clear()
        for business in businesses:
            try:
                business = BusinessType.objects.get(pk=business['id'])
                self.businesses.add(business)
            except BusinessType.DoesNotExist:
                continue
        return True


class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin):
    username = models.CharField(max_length=192, unique=True)
    real_name = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(default='0.0.0.0')
    is_online = models.BooleanField(default=False)
    is_remove = models.BooleanField(default=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True)
    profile = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = UserManager()
    role = models.ForeignKey(Role, related_name='user_roles', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username

    def update_online(self, status=False):
        self.is_online = status
        self.save()
        return True

    def has_perm(self, perm: str, obj=None):
        if self.is_active and self.is_superuser:
            return True
        if not self.role or not self.role.permissions:
            return False
        if self.role.permissions.filter(codename=perm).exists():
            return True
        return False

    def has_perms(self, perms: dict, obj=None):
        return all(self.has_perm(perm, obj) for perm in perms)

    def assign_perms(self, perms: dict):
        pass

    def get_contact_list(self):
        Order = apps.get_model('Paper.Order')


class CustomerProfile(models.Model):
    position = models.CharField(max_length=255, null=True)
    department = models.CharField(max_length=255, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    user = GenericRelation(User, related_query_name='customer_profile')

    def assign_remote_user_list(self, accounts):
        Journal = apps.get_model('Paper.Journal')
        add_id_list = []
        for account in accounts:
            try:
                if type(account.get('id')) == 'int' and RemoteAccount.objects.filter(pk=account.get('id')).exists():
                    remote_user = RemoteAccount.objects.get(pk=account['id'])
                else:
                    remote_user = RemoteAccount()
                remote_user.username = account['username']
                remote_user.password = account['password']
                remote_user.host = account['host']
                remote_user.profile = self
                if Journal.objects.filter(pk=account.get('journal')).exists():
                    remote_user.journal = Journal.objects.get(pk=account.get('journal'))
                if BusinessType.objects.filter(pk=account.get('type')).exists():
                    remote_user.type = BusinessType.objects.get(pk=account.get('type'))
                remote_user.save()
                add_id_list.append(remote_user.id)
            except Exception as e:
                print('assign remote user account', e)
                continue
        RemoteAccount.objects.filter(profile=self).exclude(id__in=add_id_list).delete()
        return True


class UnitBusiness(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    business = models.ForeignKey(BusinessType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['unit', 'business']


class RemoteAccount(models.Model):
    profile = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='profile_remote_account', null=True)
    type = models.ForeignKey(BusinessType, on_delete=models.CASCADE, related_name='user_account_business', null=True)
    journal = models.ForeignKey('Paper.Journal', on_delete=models.CASCADE, related_name='user_account_journal', null=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    host = models.CharField(max_length=255, null=True)
    is_available = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['profile', 'type', 'username']


class Log(TimeStampMixin):
    type = models.ForeignKey(BusinessType, on_delete=models.CASCADE, related_name='log_type')
    date = models.DateField(auto_now_add=True)
    logs = models.JSONField(null=True)


class Message(models.Model):
    by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_from_message')
    to = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_to_message')
    content = models.TextField(null=True)
    additional_info = models.JSONField(null=True)
    type = models.ForeignKey(BusinessType, on_delete=models.DO_NOTHING, related_name='message_business')
    created_at = models.DateTimeField(auto_now_add=True)
    is_view = models.BooleanField(default=False)
    is_highlight = models.BooleanField(default=False)


class Post(TimeStampMixin):
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_post')
    title = models.CharField(max_length=255)
    body = models.TextField(null=True)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def __repr__(self):
        return f"<Post {self.author}:{self.title}>"

    def __str__(self):
        return f"{self.author}:{self.title}"


class Comment(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_comment')
    content = models.TextField(null=True)
    post = models.ForeignKey(Post, on_delete=models.DO_NOTHING, related_name='post_comment')


class Notice(TimeStampMixin):
    receiver = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='notice_receiver', null=True)
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='notice_sender', null=True)
    content = models.TextField(null=True)
    additional_info = models.JSONField(null=True)
    is_read = models.BooleanField(default=False)
    is_highlight = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def send_notice(self):
        if not self.sender or not self.receiver or self.sender == self.receiver:
            return False
        else:
            notify = NotificationService(self.receiver)
            return notify.notify(self.get_message())

    def get_message(self):
        return {
            'type': 'notify',
            'message': self.content,
            'additional_info': self.additional_info,
            'is_read': self.is_read,
            'is_highlight': self.is_highlight,
            'created_at': str(self.created_at),
            'from': self.sender.username
        }


def user_directory_path(instance, filename):
    return f"upload/{hashlib.md5(str(instance.user.id).encode('utf-8')).hexdigest()}/{filename}"

