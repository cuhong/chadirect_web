import json

from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.auth import login as django_login
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, F
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView
from rest_framework.views import APIView

from account.models import User, Organization
from django.contrib.auth import logout as auth_logout

from car_cms.models import Compare, CompareStatus, CustomerTypeChoices, ChannelChoices
from commons.models import VehicleInsurerChoices


class AffiliateUserMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/affiliate/login/"

    def test_func(self):
        if self.request.user.is_authenticated is True:
            return all([self.request.user.is_active, self.request.user.is_organization_admin])
        return False

    def dispatch(self, request, *args, **kwargs):
        self.cms_user = None
        return super().dispatch(request, *args, **kwargs)

    def get_login_url(self):
        url = reverse('car_cms_affiliate:login')
        return url

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            url = reverse('car_cms_affiliate:403')
        else:
            url = reverse('car_cms_affiliate:login')
        return redirect(url)


# /Users/cuhong/dev/itechs/chadirect/src/templates/static/atmos/css/atmos.min.css
class Handle403View(TemplateView):
    template_name = 'affiliate/auth/403.html'


class LoginView(DjangoLoginView):
    template_name = 'affiliate/auth/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_redirect_url())
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self):
        url = reverse('car_cms_affiliate:index')
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loginError'] = True if context['form'].errors else False
        return context


class LogoutView(DjangoLogoutView):
    def get_next_page(self):
        url = reverse('car_cms_affiliate:login')
        return url


# class IndexView(AffiliateUserMixin, TemplateView):
#     template_name = 'affiliate/index.html'

class IndexView(AffiliateUserMixin, View):
    def get(self, request):
        # return render(request, 'affiliate/index.html')
        url = reverse('car_cms_affiliate:user_list')
        return HttpResponseRedirect(url)

    def post(self, request):
        url = reverse('car_cms_affiliate:user_list')
        return HttpResponseRedirect(url)


class SignupView(TemplateView):
    pass


class SignupForm(forms.Form):
    name = forms.CharField(required=True)
    cellphone = forms.CharField(required=True)
    username = forms.EmailField(required=True)
    password = forms.CharField(required=True)
    password2 = forms.CharField(required=True)
    namecard = forms.ImageField(required=True)

    def clean(self):
        vd = super(SignupForm, self).clean()
        if vd['password'] != vd['password2']:
            raise ValidationError({"password2": '비밀번호가 일치하지 않습니다.'})
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return username
        else:
            raise ValidationError('이미 사용중인 이메일입니다.')


class ExternalSignupView(View):
    def get(self, request):
        guid = request.GET.get('guid')
        form = SignupForm()
        organization = get_object_or_404(Organization, guid=guid)
        return render(request, 'affiliate/auth/signup/external.html', context={"organization": organization, "form": form})

    def post(self, request):
        form = SignupForm(data=request.POST, files=request.FILES)
        try:
            guid = request.GET.get('guid')
            organization = Organization.objects.get(guid=guid)
            if form.is_valid() is True:
                data = form.cleaned_data
                user = User.objects.create_user(
                    email=data.get('username'), name=data.get('name'), password=data.get('password'),
                    cellphone=data.get('cellphone'), name_card=data.get('namecard'),
                    user_type='fc', organization=organization
                )
                django_login(request, user)
                return redirect(reverse('car_cms_fc_app:index'))
            else:
                return render(
                    request, 'affiliate/auth/signup/external.html', context={"organization": organization, "form": form}
                )
        except Organization.DoesNotExist:
            return HttpResponse('존재하지 않는 조직 코드입니다.')
        except Exception as e:
            print(e)
            return render(
                request, 'affiliate/auth/signup/external.html', context={
                    "organization": organization, "form": form, "error": str(e)
                }
            )


class UserListFilterForm(forms.Form):
    name = forms.CharField(required=False)
    dept = forms.CharField(required=False)
    employee_no = forms.CharField(required=False)
    email = forms.CharField(required=False)
    cellphone = forms.CharField(required=False)
    sort = forms.CharField(required=False)

    def create_query(self):
        data = self.cleaned_data
        q = Q()
        print(data.get('name'))
        if data.get('name') not in ["", None]:
            q.add(Q(name__icontains=data.get('name')), q.AND)
        if data.get('dept') not in ["", None]:
            dept = data.get('dept')
            dept_q = Q(dept_1__icontains=dept) | Q(dept_2__icontains=dept) | Q(dept_3__icontains=dept) | Q(dept_4__icontains=dept)
            q.add(dept_q, q.AND)
        if data.get('employee_no') not in ["", None]:
            q.add(Q(employee_no__icontains=data.get('employee_no')), q.AND)
        if data.get('email') not in ["", None]:
            q.add(Q(email__icontains=data.get('email')), q.AND)
        if data.get('cellphone') not in ["", None]:
            q.add(Q(cellphone__icontains=data.get('cellphone')), q.AND)
        sort = "-registered_at" if data.get('sort') == "" else data.get('sort')
        return q, sort


class UserListView(AffiliateUserMixin, ListView):
    template_name = 'affiliate/user/list.html'
    queryset = User.objects.all()

    def get_paginate_by(self, queryset):
        return self.request.POST.get('perPage', 30)

    def get_queryset(self):
        queryset = super(UserListView, self).get_queryset()
        filterform = UserListFilterForm(self.request.GET)
        if filterform.is_valid():
            query, sort = filterform.create_query()
            queryset = queryset.order_by(sort).values(
                'id', 'email', 'name', 'cellphone', 'is_organization_admin', 'is_active', 'registered_at', 'last_login',
                'employee_no', 'role'
            ).annotate(
                dept_1_value=Case(When(dept_1=None, then=Value("-")), default=F('dept_1')),
                dept_2_value=Case(When(dept_2=None, then=Value("-")), default=F('dept_2')),
                dept_3_value=Case(When(dept_3=None, then=Value("-")), default=F('dept_3')),
                dept_4_value=Case(When(dept_4=None, then=Value("-")), default=F('dept_4')),
            ).annotate(
                dept=Concat(
                    F('dept_1_value'), Value("/"),
                    F('dept_2_value'), Value("/"),
                    F('dept_3_value'), Value("/"),
                    F('dept_4_value')
                )
            ).filter(organization=self.request.user.organization).filter(query)
            filterform.create_query()
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(UserListView, self).get_context_data(*args, **kwargs)
        user_list = []
        for user in context.get('object_list'):
            user_dict = dict(user)
            user_dict['registered_at'] = user_dict['registered_at'].strftime("%Y-%m-%d %H:%M:%S")
            user_dict['last_login'] = "미접속" if user_dict['last_login'] is None else user_dict['last_login'].strftime(
                "%Y-%m-%d %H:%M:%S")
            user_list.append(user_dict)
        context['json_object_list'] = user_list
        filterform = UserListFilterForm(self.request.GET)
        context['filterform'] = filterform
        return context


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'employee_no', 'cellphone', 'is_organization_admin']


class UserDetailView(AffiliateUserMixin, View):
    def get(self, request, user_id):
        try:
            user = User.objects.values(
                'id', 'registered_at', 'last_login', 'email', 'name', 'employee_no', 'cellphone',
                'is_organization_admin'
            ).get(id=user_id, organization=request.user.organization)
            user_data = dict(
                id=str(user.get('id')),
                registered_at=user.get('registered_at').strftime("%Y-%m-%d %H:%M:%S"),
                last_login=None if user.get('last_login') is None else user.get('last_login').strftime(
                    "%Y-%m-%d %H:%M:%S"),
                email=user.get('email'),
                name=user.get('name'),
                employee_no=user.get('employee_no'),
                cellphone=user.get('cellphone'),
                is_organization_admin=user.get('is_organization_admin'),
            )
            response_data = {
                "result": True, "data": user_data
            }
        except User.DoesNotExist:
            response_data = {"result": False, "msg": "존재하지 않는 회원 입니다."}
        except Exception as e:
            response_data = {"result": False, "msg": f"기타 에러 : {str(e)}"}
        return JsonResponse(response_data)

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, organization=request.user.organization)
            form = UserUpdateForm(request.POST, instance=user)
            if form.is_valid() is True:
                form.save()
                response_data = {"result": True, "data": None}
            else:
                response_data = {"result": False, "msg": "요청값이 올바르지 않습니다.", "error": form.errors}
        except User.DoesNotExist:
            response_data = {"result": False, "msg": "존재하지 않는 회원 입니다."}
        except Exception as e:
            response_data = {"result": False, "msg": f"기타 에러 : {str(e)}"}
        return JsonResponse(response_data)


class AddUserView(View):
    def get(self, request):
        url = request.user.organization.external_signup_url
        return render(request, 'affiliate/auth/signup/add_user.html', context={"url": url})



class ContractListFilterForm(forms.Form):
    status = forms.CharField(required=False)

    def create_query(self):
        data = self.cleaned_data
        q = Q()
        if data.get('status') != "":
            q.add(Q(status=data.get('status')), q.AND)
        return q


class ContractListView(AffiliateUserMixin, ListView):
    template_name = 'affiliate/contract/list.html'
    queryset = Compare.objects.all()

    def get_paginate_by(self, queryset):
        return self.request.POST.get('perPage', 30)

    def get_queryset(self):
        queryset = super(ContractListView, self).get_queryset()
        queryset = queryset.values(
            'id', 'account__name', 'account__cellphone', 'serial', 'status', 'insurer', 'premium', 'customer_type', 'channel', 'registered_at'
        ).filter(account__organization=self.request.user.organization)

        filterform = ContractListFilterForm(self.request.GET)
        if filterform.is_valid():
            query = filterform.create_query()
            queryset = queryset.filter(query)
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(ContractListView, self).get_context_data(*args, **kwargs)
        # user_list = []
        # for user in context.get('object_list'):
        #     user_dict = dict(user)
        #     user_dict['registered_at'] = user_dict['registered_at'].strftime("%Y-%m-%d %H:%M:%S")
        #     user_dict['last_login'] = "미접속" if user_dict['last_login'] is None else user_dict['last_login'].strftime(
        #         "%Y-%m-%d %H:%M:%S")
        #     user_list.append(user_dict)
        # context['json_object_list'] = user_list
        filterform = ContractListFilterForm(self.request.GET)
        context['filterform'] = filterform
        queryset = context.get('object_list')
        contract_list = [{
            "id": contract.get('id'),
            "account_name": f"{contract.get('account__name')}",
            "serial": contract.get('serial'),
            "status": contract.get('status'),
            "status_display": CompareStatus(contract.get('status')).label,
            "insurer": contract.get('insurer'),
            "insurer_display": VehicleInsurerChoices(contract.get('insurer')).label if contract.get('insurer') else "-",
            "premium": contract.get('premium'),
            "customer_type": contract.get('customer_type'),
            "customer_type_display": CustomerTypeChoices(contract.get('customer_type')).label,
            "channel": contract.get('channel'),
            "channel_display": ChannelChoices(contract.get('channel')).label,
            "registered_at": (contract.get('registered_at') + relativedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S"),
        } for contract in queryset]
        context['contract_list'] = contract_list
        context['status_list'] = CompareStatus.choices
        return context