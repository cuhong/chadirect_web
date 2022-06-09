from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError

from account.models import Organization, OrganizationEmployee

User = get_user_model()


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_searchable']
    list_filter = ['is_searchable']
    search_fields = ['name__icontains']
    readonly_fields = ['guid']


@admin.register(OrganizationEmployee)
class OrganizationEmployeeAdmin(admin.ModelAdmin):
    list_display = ['organization', 'dept_1', 'code', 'role', 'name', 'contact']
    list_filter = ['organization']
    search_fields = ['name__icontains', 'contact__icontains']


class CustomUserChangeForm(UserChangeForm):
    def clean(self):
        cleaned_data = super().clean()
        if all([cleaned_data.get('is_organization_admin') is True, cleaned_data.get('organization') is None]):
            raise ValidationError({'is_organization_admin': ["조직을 지정하지 않은 경우 관리자로 지정할 수 없습니다."]})
        return cleaned_data


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # class UserAdmin(admin.ModelAdmin):
    autocomplete_fields = ['organization']
    list_display = ['email', 'name', 'organization', 'is_organization_admin']
    search_fields = ['email__icontains', 'name__icontains']
    form = CustomUserChangeForm
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('개인정보', {'fields': ('name', 'cellphone', 'name_card', 'ssn')}),
        ('계좌정보', {'fields': ('bank', 'bank_account_no', 'real_name')}),
        ('가입정보', {'fields': ('organization', 'is_organization_admin', 'referer_code', 'user_type')}),
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
    list_filter = ('organization', 'is_organization_admin', 'is_admin', 'is_superuser', 'is_active', 'groups')
    # search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
