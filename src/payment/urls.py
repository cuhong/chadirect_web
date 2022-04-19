from django.urls import path

from payment.views import DanalAuthView, DanalAuthSuccessView, DanalAuthErrorView

app_name = 'payment'

urlpatterns = [
    path('danal_auth/<uuid:danal_auth_id>/', DanalAuthView.as_view(), name='danal_auth'),
    path('danal_auth/<uuid:danal_auth_id>/success/', DanalAuthSuccessView.as_view(), name='danal_auth_success'),
    path('danal_auth/<uuid:danal_auth_id>/error/', DanalAuthErrorView.as_view(), name='danal_auth_error'),
]