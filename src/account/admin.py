from django.contrib import admin
from django.contrib.auth import get_user_model
from rest_framework_api_key.admin import APIKeyModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from account.models import APIKey, Affiliate, ItechsPermission

User = get_user_model()


class ItechsPermissionInlineAdmin(admin.TabularInline):
    model = ItechsPermission


@admin.register(User)
class UserAdmin(BaseUserAdmin):
# class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name']
    inlines = [ItechsPermissionInlineAdmin]
    search_fields = ['email__icontains', 'name__icontains']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions'),
        }),
        # ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    # list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_admin', 'is_superuser', 'is_active', 'groups')
    # search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(APIKey)
class APIKeyAdmin(APIKeyModelAdmin):
    readonly_fields = ['id']


@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_filter = ['name', 'active', 'use_cp_inspection']
    search_fields = ['name__icontains', 'email__icontains']

