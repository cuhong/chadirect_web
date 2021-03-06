import os.path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

site_header = '차다이렉트'
admin.site.site_header = site_header
admin.site.site_title = site_header
admin.site.index_title = site_header


def trigger_error(request):
    division_by_zero = 1 / 0


def elb_status(request):
    return HttpResponse(status=200)


def manifest_view(request):
    with open(os.path.join(settings.BASE_DIR, 'itechs', 'pwa', 'manifest.json'), 'r') as file:
        return HttpResponse(file, content_type='application/json; charset=utf8')


def sw_view(request):
    with open(os.path.join(settings.BASE_DIR, 'itechs', 'pwa', 'sw.js'), 'r') as file:
        return HttpResponse(file, content_type='application/javascript')


urlpatterns = [
    path('', include('car_cms.urls_fc_app', namespace='car_cms_fc_app')),
    path('affiliate/', include('car_cms.urls_affiliate', namespace='car_cms_affiliate')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('admin/', admin.site.urls),
    path('carcompare/', include('carcompare.urls', namespace='carcompare')),
    path('link/', include('link.urls', namespace='link')),
    path('sentry-debug/', trigger_error),
    path('elb-status/', elb_status),
    path('manifest.json', manifest_view),
    path('sw.js', sw_view)
]

if settings.STAGE == 'local':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
