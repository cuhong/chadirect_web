from django.urls import path

from carcompare.views import CompareStartView, CompareAuthView, CompareView, CarnoView

app_name = 'carcompare'

urlpatterns = [
    path('', CompareStartView.as_view(), name='start'),
    path('carno/', CarnoView.as_view(), name='carno'),
    path('<uuid:compare_id>/auth/', CompareAuthView.as_view(), name='start'),
    path('<uuid:compare_id>/compare/', CompareView.as_view(), name='compare'),
]