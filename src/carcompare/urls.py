from django.urls import path

from carcompare.views import CompareStartView, CompareAuthView, CompareView, CarnoView, CompareShutDownView, \
    CompareDetailView

app_name = 'carcompare'

urlpatterns = [
    path('', CompareStartView.as_view(), name='start'),
    path('carno/', CarnoView.as_view(), name='carno'),
    path('<uuid:compare_id>/auth/', CompareAuthView.as_view(), name='start'),
    path('<uuid:compare_id>/compare/', CompareView.as_view(), name='compare'),
    path('<uuid:compare_id>/shutdown/', CompareShutDownView.as_view(), name='compare_shutdown'),
    path('detail/<int:compare_detail_id>/', CompareDetailView.as_view(), name='compare_detail'),
]