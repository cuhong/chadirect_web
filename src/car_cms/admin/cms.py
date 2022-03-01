from functools import update_wrapper

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from car_cms.models import Compare


class CMSAdminSite(admin.AdminSite):
    site_header = "차다이렉트 관리자"
    site_title = site_header
    index_title = site_header

    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        user = request.user
        return user.is_authenticated and request.user.carcrm_user.is_admin


cms_admin_site = CMSAdminSite(name='post_admin')

cms_admin_site.register(Compare)
