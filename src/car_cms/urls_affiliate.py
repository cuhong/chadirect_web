from django.urls import path
from car_cms.views.affiliate import IndexView, SignupView, LogoutView, LoginView, UserListView, UserDetailView, \
    Handle403View, ExternalSignupView, AddUserView, ContractListView, ContractSuccessListView

app_name = 'car_cms_affiliate'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/signup/external/', ExternalSignupView.as_view(), name='signup_external'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserListView.as_view(), name='user_list'),
    path('user/<uuid:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('contract/', ContractListView.as_view(), name='contract_list'),
    path('contract/success/', ContractSuccessListView.as_view(), name='contract_success_list'),
    path('user/add/', AddUserView.as_view(), name='user_add'),
    path('auth/403/', Handle403View.as_view(), name='403'),
]
