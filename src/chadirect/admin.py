from dateutil.relativedelta import relativedelta
from django.contrib import admin, messages
from chadirect.models import *
from inline_actions.admin import InlineActionsModelAdminMixin
from import_export import resources as ie_resources
from import_export import admin as ie_admin
from import_export import fields as is_fields
from daterangefilter.filters import PastDateRangeFilter

class DBCustomerReserouce(ie_resources.ModelResource):
    class Meta:
        model = DBCustomer
        fields = [
            'registered_at', 'user_name', 'ssn_prefix', 'gender_display', 'name', 'contact', 'is_db_registered',
            'db_registered_at', 'memo'
        ]
        export_order = [
            'registered_at', 'user_name', 'name', 'ssn_prefix', 'gender_display', 'contact', 'is_db_registered',
            'db_registered_at', 'memo'
        ]

    registered_at = is_fields.Field(column_name='고객등록일시')
    ssn_prefix = is_fields.Field(column_name='생년월일')
    user_name = is_fields.Field(column_name='담당자명')
    name = is_fields.Field(column_name='성명')
    contact = is_fields.Field(column_name='연락처')
    memo = is_fields.Field(column_name='메모')
    gender_display = is_fields.Field(column_name='성멸')
    is_db_registered = is_fields.Field(column_name='보험사등록')
    db_registered_at = is_fields.Field(column_name='보험사등록일시')

    def dehydrate_registered_at(self, obj):
        registered_at = obj.registered_at + relativedelta(hours=9)
        return registered_at.strftime("%Y-%m-%d %H:%M:%S")

    def dehydrate_user_name(self, obj):
        return obj.user.name

    def dehydrate_gender_display(self, obj):
        return obj.get_gender_display()

    def dehydrate_is_db_registered(self, obj):
        return "등록" if obj.is_db_registered else "미등록"

    def dehydrate_db_registered_at(self, obj):
        db_registered_at = obj.db_registered_at + relativedelta(hours=9)
        return db_registered_at.strftime("%Y-%m-%d %H:%M:%S")


@admin.register(DBCustomer)
class DBCustomerAdmin(ie_admin.ExportMixin, InlineActionsModelAdminMixin, admin.ModelAdmin):
    list_display = ['registered_at', 'user', 'ssn_prefix', 'gender', 'name', 'contact', 'is_db_registered',
                    'db_registered_at']
    list_filter = ['is_db_registered', ('registered_at', PastDateRangeFilter), ('db_registered_at', PastDateRangeFilter)]
    resource_class = DBCustomerReserouce

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            readonly_fields = [
                'registered_at', 'updated_at', 'user', 'is_db_registered', 'db_registered_at', 'error',
                'render_inline_actions'
            ]
        elif obj.is_db_registered is True:
            readonly_fields = [
                'registered_at', 'updated_at', 'user',
                'ssn_prefix', 'gender', 'name', 'contact',
                'is_db_registered', 'db_registered_at', 'error', 'render_inline_actions'
            ]
        else:
            readonly_fields = [
                'registered_at', 'updated_at', 'user',
                'is_db_registered', 'db_registered_at', 'error', 'render_inline_actions'
            ]
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.user is None:
            obj.user = request.user
        return super(DBCustomerAdmin, self).save_model(request, obj, form, change)

    def get_inline_actions(self, request, obj=None):
        actions = super(DBCustomerAdmin, self).get_inline_actions(request, obj)
        if obj:
            if obj.is_db_registered is False:
                actions.append('send_data')
        return actions

    def send_data(self, request, obj, parent_obj=None):
        if obj.is_db_registered is True:
            messages.error(request, '이미 전송되었습니다.')
        else:
            result = obj.send_data()
            if result:
                messages.success(request, '전송되었습니다.')
            else:
                messages.error(request, '전송에 실패했습니다.')

    send_data.short_description = 'DB손보 전송'
