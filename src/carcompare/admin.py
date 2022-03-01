from django.contrib import admin

from carcompare.models import Compare, LegacyContract
from import_export.admin import ExportMixin


class ContractInlineAdmin(admin.TabularInline):
    model = LegacyContract
    readonly_fields = ['company_name', 'car_no', 'car_name', 'due_date']
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Compare)
class CompareAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['name', 'ssn_prefix', 'phone', 'status']
    list_filter = ['status']
    search_fields = ['name__icontains', 'ssn_prefix__icontains', 'car_name__icontains']
    inlines = [ContractInlineAdmin]

    def phone(self, obj):
        return f"{obj.phone1}-{obj.phone2}-{obj.phone3}"

    phone.short_description = '휴대전화'

# 'start_date', 'manufacturer', 'car_name'
