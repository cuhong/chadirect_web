import urllib

from django.conf import settings
from django.contrib import admin
from django.urls import reverse

from link.models import ProductLink, Shortlink, ShortlinkLog, generate_short_code


@admin.register(ProductLink)
class ProductLinkAdmin(admin.ModelAdmin):
    list_display = ['product']


class ShortlinkLogInline(admin.TabularInline):
    model = ShortlinkLog
    readonly_fields = ['device', 'referer', 'ip', 'registered_at']

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    extra = 0


@admin.register(Shortlink)
class ShortlinkAdmin(admin.ModelAdmin):
    list_display = ['product', 'short_code', 'short_url', 'user', 'compare', 'registered_at', 'last_log_at']
    list_filter = ['product']
    inlines = [ShortlinkLogInline]

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            readonly_fields = [
                'registered_at', 'short_code', 'short_url', 'last_log_at', 'user', 'compare'
            ]
        else:
            readonly_fields = [
                'product', 'registered_at', 'short_code', 'short_url', 'last_log_at', 'user', 'compare'
            ]
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if change is False:
            while True:
                short_code = generate_short_code()
                try:
                    base_url = settings.BASE_URL
                    uri = reverse('link:shortner', args=[short_code])
                    url = urllib.parse.urljoin(base_url, uri)
                    obj.user = request.user
                    obj.short_code = short_code
                    obj.short_url = url
                    break
                except:
                    continue
        super(ShortlinkAdmin, self).save_model(request, obj, form, change)
