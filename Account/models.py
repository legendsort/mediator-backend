from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser, Permission
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from Account.managers import UserManager
from django.utils.translation import gettext_lazy as _
import hashlib


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


class Unit(models.Model):
    name = models.CharField(max_length=255, unique=True)
    super_origination = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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

    def update_online(self, status=False):
        self.is_online = status
        self.save()
        return True


class CustomerProfile(models.Model):
    position = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    unit = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)
    account_is_active = models.BooleanField(default=True)
    account_is_staff = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    user = GenericRelation(User, related_query_name='customer_profile')


class BusinessType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=1024)


class RemoteAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_remote_account')
    type = models.ForeignKey(BusinessType, on_delete=models.DO_NOTHING, related_name='user_account_business')
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)


class Log(TimeStampMixin):
    type = models.ForeignKey(BusinessType, on_delete=models.DO_NOTHING, related_name='log_type')
    date = models.DateField(auto_now_add=True)
    logs = models.JSONField(null=True)


class Message(models.Model):
    by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_from_message')
    to = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_to_message')
    content = models.TextField(null=True)
    additional_info = models.JSONField(null=True)
    type = models.ForeignKey(BusinessType, on_delete=models.DO_NOTHING, related_name='message_business')
    # order =
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
    to = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='notice_to_user')
    content = models.TextField(null=True)
    additional_info = models.JSONField(null=True)
    is_view = models.BooleanField(default=False)
    is_highlight = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


def user_directory_path(instance, filename):
    return f"upload/{hashlib.md5(str(instance.user.id).encode('utf-8')).hexdigest()}/{filename}"


class Upload(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_upload')
    file = models.FileField(blank=False, null=False, upload_to=user_directory_path)
    submit = models.ForeignKey('Paper.Submit', on_delete=models.DO_NOTHING, null=True, related_name='user_upload')


