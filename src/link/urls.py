from django.urls import path

from link.views import ShortLinkView

app_name = 'link'

urlpatterns = [
    path('s/<str:short_code>/', ShortLinkView.as_view(), name='shortner'),
]