from django.contrib import admin

# Register your models here.
from commons.models import CustomerInfo


@admin.register(CustomerInfo)
class CustomerInfoAdmin(admin.ModelAdmin):
    pass
