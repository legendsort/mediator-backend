from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Account.models import User, Role, Permission, Membership
from Account.forms import CustomUserCreationForm, CustomUserChangeForm
# Register your models here.


@admin.register(User)
class CustomizeUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'real_name', 'is_staff', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'real_name', 'is_active', 'is_staff', 'role')}),
        # ('Permissions', {'fields': ('is_staff', 'is_active')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('username', 'real_name', 'password1', 'password2', 'is_active', 'is_staff')
        }),
    )


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename',)
    inlines = (MembershipInline,)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename')
    inlines = (MembershipInline,)




