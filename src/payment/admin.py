from django.contrib import admin

# Register your models here.
from payment.models import DanalAuth


@admin.register(DanalAuth)
class DanalAuthAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'phone_no', 'status', 'danal_name',
        'danal_iden', 'agree_1', 'agree_2', 'agree_3',
        'agree_at'
    ]
    readonly_fields = [
        'id', 'registered_at', 'updated_at', 'tid', 'title', 'success_url', 'phone_no',
        'status', 'danal_ci', 'danal_di', 'danal_name', 'danal_iden', 'agree_at', 'agree_1', 'agree_2', 'agree_3'
    ]
    list_filter = ['status', 'agree_1', 'agree_2', 'agree_3']
    search_fields = ['phone_no__icontains', 'danal_name__icontains']