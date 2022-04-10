from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from account.models import Organization

User = get_user_model()


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_searchable']
    list_filter = ['is_searchable']
    search_fields = ['name__icontains']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # class UserAdmin(admin.ModelAdmin):
    autocomplete_fields = ['organization']
    list_display = ['email', 'name']
    search_fields = ['email__icontains', 'name__icontains']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('개인정보', {'fields': ('name', 'cellphone', 'name_card', 'ssn')}),
        ('계좌정보', {'fields': ('bank', 'bank_account_no', 'real_name')}),
        ('가입정보', {'fields': ('organization', 'referer_code', 'user_type')}),
        ('권한', {
            'fields': (
                'is_active', 'is_admin', 'is_superuser',
                'groups',
                # 'user_permissions'
            ),
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
