from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Account.models import User, Role, Permission, Membership
# Register your models here.


@admin.register(User)
class CustomizeUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'role')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission', )

