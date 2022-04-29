import json

from django import forms
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView
from rest_framework.views import APIView

from account.models import User
from django.contrib.auth import logout as auth_logout

class AffiliateUserMixin(LoginRequiredMixin, UserPassesTestMixin):

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
        auth_logout(self.request)
        url = reverse('car_cms_affiliate:login')
        return redirect(url)


# /Users/cuhong/dev/itechs/chadirect/src/templates/static/atmos/css/atmos.min.css

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


class LogoutView(AffiliateUserMixin, DjangoLogoutView):
    def get_next_page(self):
        url = reverse('car_cms_affiliate:login')
        return url


# class IndexView(AffiliateUserMixin, TemplateView):
#     template_name = 'affiliate/index.html'

class IndexView(AffiliateUserMixin, View):
    def get(self, request):
        return HttpResponseRedirect(reverse('car_cms_affiliate:user_list'))

    def post(self, request):
        return HttpResponseRedirect(reverse('car_cms_affiliate:user_list'))


class SignupView(TemplateView):
    pass


class UserListFilterForm(forms.Form):
    name = forms.CharField(required=False)
    employee_no = forms.CharField(required=False)
    email = forms.CharField(required=False)
    cellphone = forms.CharField(required=False)
    sort = forms.CharField(required=False)

    def create_query(self):
        data = self.cleaned_data
        q = Q()
        print(data.get('name'))
        if data.get('name') != "":
            q.add(Q(name__icontains=data.get('name')), q.AND)
        if data.get('employee_no') != "":
            q.add(Q(employee_no__icontains=data.get('employee_no')), q.AND)
        if data.get('email') != "":
            q.add(Q(email__icontains=data.get('email')), q.AND)
        if data.get('cellphone') != "":
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
                'employee_no'
            ).filter(organization=self.request.user.organization).filter(query)
            filterform.create_query()
        else:
            print(filterform.errors)
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
