from django.contrib import admin

from car_cms.models import Account


class AccountInline(admin.TabularInline):
    model = Account
    readonly_fields = ['user', 'name', 'cellphone', 'is_active', 'is_admin']
    fields = ['username', 'name', 'cellphone', 'is_active', 'is_admin']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    date_hierarchy = 'registered_at'
    list_display = [
        'user', 'user_type', 'name', 'cellphone', 'is_active', 'is_admin', 'registered_at'
    ]
    list_filter = ['is_active', 'is_admin', 'user_type']
    search_fields = ['name__icontains', 'user__email__icontains', 'cellphone__icontains']
    autocomplete_fields = ['user']
