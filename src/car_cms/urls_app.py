from django.urls import path

from car_cms.admin.cms import cms_admin_site
from car_cms.views.app import IndexView, LoginView, LogoutView, SignupView, NoticeDetailView, NoticeView, \
    CompareCreateView, CompareDetailView, CompareListView, CompareEstimateView, ComparePolicyView, PrivatePolicyView, \
    UserPolicyView, PayListView, BankAccountView, PasswordChangeView, PasswordChangeRequestView, \
    CompareEstimateAdminView

app_name = 'car_cms_app'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('policy/privacy/', PrivatePolicyView.as_view(), name='privacyPolicy'),
    path('policy/user/', UserPolicyView.as_view(), name='userPolicy'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password/request/', PasswordChangeRequestView.as_view(), name='password_change_request'),
    path('auth/password/<uuid:fp_id>/', PasswordChangeView.as_view(), name='password_change'),
    path('notice/', NoticeView.as_view(), name='notice'),
    path('notice/<int:notice_id>/', NoticeDetailView.as_view(), name='notice_detail'),
    path('compare/', CompareListView.as_view(), name='compare_list'),
    path('compare/pay/', PayListView.as_view(), name='pay_list'),
    path('compare/pay/bank/', BankAccountView.as_view(), name='bank_account'),
    path('compare/create/', CompareCreateView.as_view(), name='compare_create'),
    path('compare/<uuid:compare_id>/', CompareDetailView.as_view(), name='compare_detail'),
    path('compare/<uuid:compare_id>/estimate/', CompareEstimateView.as_view(), name='estimate_detail'),
    path('compare/<uuid:compare_id>/estimate/admin/', CompareEstimateAdminView.as_view(), name='estimate_detail_admin'),
    path('compare/<uuid:compare_id>/policy/', ComparePolicyView.as_view(), name='policy_detail'),
    path('admin/', cms_admin_site.urls, name='cms_admin'),
]
