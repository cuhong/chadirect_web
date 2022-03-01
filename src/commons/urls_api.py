from django.urls import path
from commons import views_api

app_name = 'commons_api'
urlpatterns = [
    path('utils/aes/', views_api.AESTestViewView.as_view(), name='aes')
]
