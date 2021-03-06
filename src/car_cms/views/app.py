import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django.db import transaction, models
from django.db.models import Count, Sum, When, Case, Value, Q, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.views.generic import TemplateView, ListView

from django import forms
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from sentry_sdk import capture_exception

from car_cms.exceptions.compare import CarCMSCompareError
from car_cms.models import Notice, Compare, CompareStatus
from commons.utils.age import lunar_age
from itechs.commons import KST
from payment.models import DanalAuthStatusChoice, DanalAuth


class AppTypeCheck():
    @property
    def app_type(self):
        return 'fc'


class PasswordChangeForm(forms.Form):
    class Meta:
        fields = ['password']

    password = forms.CharField(required=True)


class PasswordChangeView(AppTypeCheck, View):
    def get(self, request, fp_id):
        context = {"type": self.app_type}
        try:
            find_password = FindPassword.objects.get(id=fp_id)
            find_password.check_valid()
            context['result'] = True
        except FindPassword.DoesNotExist:
            context['result'] = False
            context['msg'] = '존재하지 않는 페이지'
        except FindPasswordError as e:
            context['result'] = False
            context['msg'] = e.msg
        except Exception as e:
            capture_exception(e)
            context['result'] = False
            context['msg'] = str(e)
        return render(request, 'car_cms/auth/change_password.html', context=context)

    def post(self, request, fp_id):
        form = PasswordChangeForm(request.POST)
        if form.is_valid() is False:
            response_data = {"result": False, "msg": "잘못된 요청"}
        else:
            try:
                find_password = FindPassword.objects.get(id=fp_id)
                password = form.cleaned_data.get('password')
                find_password.change_password(password)
                response_data = {"result": True}
            except FindPassword.DoesNotExist:
                response_data = {"result": False, "msg": "잘못된 접근"}
            except FindPasswordError as e:
                response_data = {"result": False, "msg": e.msg}
            except Exception as e:
                capture_exception(e)
                response_data = {"result": False, "msg": str(e)}
        return JsonResponse(response_data)


class PasswordChangeRequestView(AppTypeCheck, View):
    def post(self, request):
        try:
            email = request.POST.get('email')
            user = User.objects.get(email=email)
            FindPassword.request_change(user, app_type=self.app_type)
            response_data = {"result": True}
        except User.DoesNotExist:
            response_data = {"result": False, "msg": "존재하지 않는 이메일입니다."}
        except Exception as e:
            capture_exception(e)
            response_data = {"result": False, "msg": str(e)}
        return JsonResponse(response_data)


class CmsUserPermissionMixin(UserPassesTestMixin):

    def test_func(self):
        if self.request.user.is_authenticated is True:
            return self.request.user.is_active
        return False

    def dispatch(self, request, *args, **kwargs):
        self.cms_user = None
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_login_url(self):
        if "carcms_fc" in self.request.path:
            url = reverse('car_cms_fc_app:login')
        else:
            url = reverse('car_cms_app:login')
        return url


class LoginView(AppTypeCheck, DjangoLoginView):
    template_name = 'car_cms/auth/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_redirect_url())
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self):
        if self.app_type == "dealer":
            url = reverse_lazy('car_cms_app:index')
        else:
            url = reverse_lazy('car_cms_fc_app:index')
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loginError'] = True if context['form'].errors else False
        context['type'] = self.app_type
        return context


class LogoutView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, DjangoLogoutView):
    def get_next_page(self):
        _type = self.app_type
        if _type == "dealer":
            url = reverse_lazy('car_cms_app:login')
        else:
            url = reverse_lazy('car_cms_fc_app:login')
        return url


from account.models import User, FindPassword, FindPasswordError, Organization


class SignupForm(forms.Form):
    name = forms.CharField(required=True)
    cellphone = forms.CharField(required=True)
    username = forms.EmailField(required=True)
    password = forms.CharField(required=True)
    password2 = forms.CharField(required=True)
    organization = forms.CharField(required=True)
    namecard = forms.ImageField(required=True)
    referer_code = forms.CharField(required=False)

    def clean(self):
        vd = super(SignupForm, self).clean()
        if vd['password'] != vd['password2']:
            raise ValidationError('비밀번호가 일치하지 않습니다.')
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(email=username)
        except User.DoesNotExist:
            return username
        else:
            raise ValidationError('이미 사용중인 이메일입니다.')


class SignupView(AppTypeCheck, View):
    def get(self, request):
        form = SignupForm()
        organization_list = Organization.objects.values_list('name', flat=True).filter(is_searchable=True)
        context = dict(form=form, type=self.app_type, organization_list=organization_list)
        return render(request, 'car_cms/auth/signup.html', context=context)

    def post(self, request):
        try:
            form = SignupForm(data=request.POST, files=request.FILES)
            if form.is_valid() is True:
                data = form.cleaned_data
                with transaction.atomic():
                    user = User.objects.create_user(
                        data['username'], data['name'], password=data['password'],
                        cellphone=data['cellphone'], name_card=data['namecard'],
                        referer_code=data['referer_code'], user_type=self.app_type,
                        organization=data['organization']
                    )
                login(request, user)
                return HttpResponseRedirect(reverse('car_cms_fc_app:index'))
            else:
                context = dict(
                    form=form,
                    is_success=False,
                    errors=form.errors,
                    error=None,
                    type=self.app_type
                )
                return render(request, 'car_cms/auth/signup.html', context=context)
        except Exception as e:
            context = dict(
                form=form,
                is_success=False,
                errors=None,
                error=str(e),
                type=self.app_type
            )
            return render(request, 'car_cms/auth/signup.html', context=context)



class IndexView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, TemplateView):
    template_name = 'car_cms/index.html'

    def get_context_data(self, **kwargs):
        now = timezone.localdate()
        context = super(IndexView, self).get_context_data(**kwargs)
        context['cms_user'] = self.request.user
        context['notice_list'] = Notice.objects.values('id', 'title', 'registered_at').filter(is_open=True)[:3]
        context['year'] = now.year
        context['month'] = now.month
        context['type'] = self.app_type
        context['summary'] = Compare.objects.filter(
            account=self.request.user, registered_at__year=now.year, registered_at__month=now.month
        ).aggregate(
            total=Coalesce(Count('id'), 0),
            request=Coalesce(Sum(Case(When(status=0, then=1), default=0, output_field=models.IntegerField())), 0),
            calculating=Coalesce(Sum(Case(When(status=1, then=1), default=0, output_field=models.IntegerField())), 0),
            calculated=Coalesce(Sum(Case(When(status=2, then=1), default=0, output_field=models.IntegerField())), 0),
            deny=Coalesce(Sum(Case(When(status=3, then=1), default=0, output_field=models.IntegerField())), 0),
            contract=Coalesce(Sum(Case(When(status=4, then=1), default=0, output_field=models.IntegerField())), 0),
            contract_success=Coalesce(Sum(Case(When(status=5, then=1), default=0, output_field=models.IntegerField())),
                                      0),
            contract_fail=Coalesce(Sum(Case(When(status=6, then=1), default=0, output_field=models.IntegerField())), 0),
        )
        return context


class NoticeView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, ListView):
    template_name = 'car_cms/notice.html'
    model = Notice
    paginate_by = 10

    def get_queryset(self):
        queryset = super(NoticeView, self).get_queryset()
        return queryset.filter(is_open=True)

    def get_context_data(self, **kwargs):
        context = super(NoticeView, self).get_context_data(**kwargs)
        context['type'] = self.app_type
        return context


class NoticeDetailView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, TemplateView):
    template_name = 'car_cms/notice_detail.html'

    def get_context_data(self, **kwargs):
        context = super(NoticeDetailView, self).get_context_data(**kwargs)
        notice_id = kwargs.get('notice_id')
        notice = Notice.objects.values('title', 'is_open', 'body', 'registered_at').get(id=notice_id, is_open=True)
        context['notice'] = notice
        context['type'] = self.app_type
        return context


class CompareForm(forms.Form):
    customer_type = forms.IntegerField(required=True)
    customer_name = forms.CharField(required=True)
    customer_identification = forms.CharField(required=True)
    career = forms.CharField(required=True)
    customer_cellphone = forms.CharField(required=False)
    channel = forms.CharField(required=False)
    # channelCheck = forms.CharField(required=False)
    car_type = forms.IntegerField(required=True)
    manufacturer = forms.CharField(required=False)
    car_name = forms.CharField(required=True)
    car_price = forms.IntegerField(required=False)
    car_identification = forms.CharField(required=False)
    ssn = forms.CharField(required=False)
    # min_age = forms.IntegerField(required=False)
    min_age_birthdate = forms.DateField(required=False, input_formats=["%Y%m%d", "%Y-%m-%d"])
    driver_range = forms.IntegerField(required=True)
    memo = forms.CharField(required=False)
    attach_1 = forms.ImageField(required=False)
    attach_2 = forms.ImageField(required=False)
    attach_3 = forms.ImageField(required=False)
    request_auth = forms.BooleanField(required=False)


class CompareCreateView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, View):
    def get_template(self):
        contractor_type = self.request.GET.get('type', '')
        car_type = self.request.GET.get('carType', '')
        if contractor_type == '0' and car_type == '0':
            template_name = 'car_cms/compare_create_newcar_personal.html'
        elif contractor_type == '1' and car_type == '0':
            template_name = 'car_cms/compare_create_newcar_biz.html'
        elif contractor_type == '0' and car_type == '1':
            template_name = 'car_cms/compare_create_usedcar_personal.html'
        elif contractor_type == '1' and car_type == '1':
            template_name = 'car_cms/compare_create_usedcar_biz.html'
        else:
            template_name = 'car_cms/compare_type.html'
        return template_name

    def get(self, request):
        context = dict(
            form=CompareForm(),
            type=self.app_type
        )
        template_name = self.get_template()
        return render(request, template_name=template_name, context=context)

    def post(self, request):
        form = CompareForm(request.POST, files=request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            birthdate_string = data.get('customer_identification', None)
            try:
                birthdate = datetime.datetime.strptime(birthdate_string[:6], '%y%m%d').date()
            except:
                birthdate = None
            min_age_birthdate = data.get('min_age_birthdate', None)
            min_age = None if min_age_birthdate is None else lunar_age(min_age_birthdate)
            customer_name = data['customer_name']
            customer_cellphone = data.get('customer_cellphone')
            # 20220728 단기간 내에 동일 요청 여러건 하는 경우 필터링
            if Compare.objects.filter(
                account=request.user, customer_name=customer_name,
                customer_cellphone=customer_cellphone,
                registered_at__gte=timezone.now() - relativedelta(minutes=30)
            ).exists():
                context = dict(
                    form=CompareForm(),
                    type=self.app_type,
                    error="30분 이내에 동일한 고객이름, 전화번호로 요청한 건이 있습니다."
                )
                template_name = self.get_template()
                return render(request, template_name=template_name, context=context)

            danal_auth = DanalAuth.objects.create(
                title="자동차보험 견적 설계 동의",
                phone_no=data.get('customer_cellphone')
            ) if data.get('request_auth') is True else None
            compare = Compare.objects.create(
                account=request.user,
                customer_name=customer_name,
                career=data.get('career'),
                customer_cellphone=customer_cellphone,
                customer_type=data['customer_type'],
                customer_identification=data['customer_identification'],
                ssn=data.get('ssn', ''),
                channel=data['channel'],
                # channel='direct' if data.get('channelCheck', None) == 'on' else 'legacy',
                manufacturer=data.get('manufacturer', 'direct'),
                car_name=data['car_name'],
                car_type=data['car_type'],
                car_price=data.get('car_price', 0),
                car_identification=None if data.get('car_identification', None) == "" else data.get(
                    'car_identification', None),
                attach_1=data['attach_1'],
                attach_2=data['attach_2'],
                attach_3=data['attach_3'],
                min_age=min_age,
                min_age_birthdate=min_age_birthdate,
                driver_range=data['driver_range'],
                memo=data['memo'],
                insured_name=data['customer_name'],
                car_name_fixed=data['car_name'],
                driver_range_fixed=data['driver_range'],
                birthdate=birthdate,
                car_no=data.get('car_identification', None),
                vin=data.get('car_identification', None),
                danal_auth=danal_auth
            )
            if data.get('request_auth') is True:
                compare.send_auth_message()
            if self.app_type == "dealer":
                compare_url = reverse('car_cms_app:compare_detail', args=[compare.id])
            else:
                compare_url = reverse('car_cms_fc_app:compare_detail', args=[compare.id])
            return HttpResponseRedirect(compare_url)
        else:
            template_name = self.get_template()
            error = "입력 내용을 확인하세요."
            context = dict(form=form, type=self.app_type, error=error)
            return render(request, template_name=template_name, context=context)


class CompareListView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, ListView):
    model = Compare
    template_name = 'car_cms/compare_list.html'
    context_object_name = 'compare_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(CompareListView, self).get_context_data(**kwargs)
        context['type'] = self.app_type
        return context

    def get_queryset(self):
        queryset = super(CompareListView, self).get_queryset()
        return queryset.values('id', 'registered_at', 'status', 'customer_name', 'customer_cellphone',
                               'car_identification', 'car_name').filter(account=self.request.user).annotate(
            status_display=Case(
                When(status=0, then=Value('견적요청')),
                When(status=1, then=Value('견적 산출중')),
                When(status=2, then=Value('견적완료')),
                When(status=3, then=Value('견적거절')),
                When(status=4, then=Value('계약요청')),
                When(status=5, then=Value('계약체결')),
                When(status=6, then=Value('계약거절')),
                When(status=7, then=Value('견적산출 불가')),
                default=Value('기타'), output_field=models.CharField()
            )
        )


class CompareDetailView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, View):
    def get(self, request, compare_id):
        from link.models import ProductChoice
        template_name = 'car_cms/compare_detail.html'
        compare = Compare.objects.get(
            account=request.user, id=compare_id
        )
        from link.models import ProductLink
        _product_choices = ProductLink.objects.all()
        product_choices = [
            (product.product, product.get_product_display()) for product in _product_choices
        ]
        context = dict(compare=compare, type=self.app_type, product_choices=product_choices)
        return render(request, template_name, context=context)

    def post(self, request, compare_id):
        compare = Compare.objects.get(
            account=request.user, id=compare_id
        )
        action = request.POST.get('action', None)
        try:
            if action == 'requestLink':
                print(request.POST)
                product = request.POST.get('product')
                cellphone = request.POST.get('cellphone')
                link = compare.create_link(product, request.user, cellphone)
                print(link.short_url)
                response_data = {"result": True}
                print('response_data = {"result": True}')
            elif action == 'requestLinkResult':
                from link.models import ShortlinkLog
                links = compare.shortlink_set.annotate(
                    log_count=Coalesce(
                        Subquery(
                            ShortlinkLog.objects.filter(short_link=OuterRef('pk')).values('short_link').annotate(
                                count=Count('pk')
                            ).values('count')
                        ), 0
                    )
                ).all()
                link_list = [
                    {
                        "product": link.product.get_product_display(),
                        "registered_at": link.registered_at.astimezone(KST).strftime("%Y-%m-%d %H:%M"),
                        "last_log_at": link.last_log_at.astimezone(KST).strftime("%Y-%m-%d %H:%M") if link.last_log_at else "",
                        "count": link.log_count - 3
                    } for link in links
                ]
                response_data = {"result": True, "link_list": link_list}
            elif action == 'requestContract':
                memo = request.POST.get('memo')
                compare.start_contract(request.user, memo=memo)
                response_data = {"result": True}
            elif action == 'getContractData':
                response_data = {
                    "result": True,
                    "id": str(compare.id),
                    "customer_name": compare.customer_name,
                    "car_name": compare.car_name,
                    "car_no": compare.car_no,
                    "status_display": compare.get_status_display(),
                    "status": compare.status,
                    "insurer_display": compare.get_insurer_display(),
                    "premium": f"{compare.premium:,}" if compare.premium else None,
                    "customer_type_display": compare.get_customer_type_display(),
                    "customer_cellphone": compare.customer_cellphone,
                    "customer_identification": f"{compare.customer_identification[:6]}-*******" if compare.customer_type == 0 else compare.customer_identification,
                    "driver_range_display": compare.get_driver_range_display(),
                    "car_type_display": compare.get_car_type_display(),
                    "car_type": compare.car_type,
                    "car_identification": compare.car_identification,
                    "attach_1": None,
                    "attach_2": None,
                    "attach_3": None,
                }
                try:
                    response_data['attach_1'] = compare.attach_1.url
                except:
                    pass
                try:
                    response_data['attach_2'] = compare.attach_2.url
                except:
                    pass
                try:
                    response_data['attach_3'] = compare.attach_3.url
                except:
                    pass
            else:
                response_data = {"result": False, "msg": "잘못된 요청"}
        except Exception as e:
            print(e)
            response_data = {"result": False, "msg": f"오류 : {str(e)}"}
        return JsonResponse(response_data)


class CompareEstimateView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, View):
    # def get(self, request, compare_id):
    #     no = str(request.GET.get('no', '1'))
    #     compare = Compare.objects.exclude(status__in=[CompareStatus.REQUEST, CompareStatus.CALCULATE]).get(
    #         id=compare_id
    #     )
    #     if no == "2":
    #         estimate_image = compare.estimate_image_2
    #     elif no == "3":
    #         estimate_image = compare.estimate_image_3
    #     else:
    #         estimate_image = compare.estimate_image
    #     template_name = 'car_cms/estimate_detail_view.html'
    #     context = dict(
    #         compare=compare, url=estimate_image.url
    #     )
    #     return render(request, template_name, context=context)
    #

    def get(self, request, compare_id):
        no = str(request.GET.get('no', '1'))
        compare = Compare.objects.exclude(status__in=[CompareStatus.REQUEST, CompareStatus.CALCULATE]).get(
            id=compare_id
        )
        if no == "2":
            estimate_image = compare.estimate_image_2
        elif no == "3":
            estimate_image = compare.estimate_image_3
        else:
            estimate_image = compare.estimate_image
        return HttpResponseRedirect(estimate_image.url)

    def post(self, request, compare_id):
        no = request.POST.get('no')
        compare = Compare.objects.exclude(status__in=[CompareStatus.REQUEST, CompareStatus.CALCULATE]).get(
            id=compare_id
        )
        if no is None:
            estimate_image = compare.estimate_image.url
        elif str(no) == "1":
            estimate_image = compare.estimate_image.url
        elif str(no) == "2":
            estimate_image = compare.estimate_image_2.url
        elif str(no) == "3":
            estimate_image = compare.estimate_image_3.url
        context = dict(
            url=estimate_image
        )
        return JsonResponse(context)


class CompareEstimateAdminView(View):
    def get(self, request, compare_id):
        if any([request.user.is_staff, request.user.is_admin, request.user.is_superuser]) is False:
            raise Exception('권한이 없습니다.')
        template_name = 'car_cms/admin/estimate_detail_admin.html'
        # https://itechs.io/carcms/compare/818dcbeb-b834-4a69-94f6-2e28140d1f38/estimate/admin/
        compare = Compare.objects.exclude(status__in=[CompareStatus.REQUEST, CompareStatus.CALCULATE]).get(
            id=compare_id
        )
        context = dict(
            compare=compare
        )
        return render(request, template_name, context=context)


class ComparePolicyView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, View):
    def get(self, request, compare_id):
        compare = Compare.objects.get(
            id=compare_id, status=CompareStatus.CONTRACT_SUCCESS
        )
        return HttpResponseRedirect(compare.policy_image.url)


class PrivatePolicyView(AppTypeCheck, TemplateView):
    template_name = 'car_cms/privacyPolicy.html'

    def get_context_data(self, **kwargs):
        context = super(PrivatePolicyView, self).get_context_data(**kwargs)
        context['type'] = self.app_type
        return context


class UserPolicyView(AppTypeCheck, TemplateView):
    template_name = 'car_cms/userPolicy.html'

    def get_context_data(self, **kwargs):
        context = super(UserPolicyView, self).get_context_data(**kwargs)
        context['type'] = self.app_type
        return context


class PayRequestForm(forms.Form):
    payId = forms.UUIDField(required=True)


class PayListView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, ListView):
    model = Compare
    template_name = 'car_cms/pay_list.html'
    context_object_name = 'pay_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super(PayListView, self).get_queryset()
        return queryset.filter(
            account=self.request.user,
            status=CompareStatus.CONTRACT_SUCCESS
        )

    def get_context_data(self, **kwargs):
        context = super(PayListView, self).get_context_data(**kwargs)
        context['type'] = self.app_type
        return context

    def post(self, request):
        form = PayRequestForm(request.POST)
        try:
            if form.is_valid() is False:
                raise Exception('잘못된 요청')
            compare = Compare.objects.get(
                account=self.request.user, id=form.cleaned_data.get('payId'),
                status=CompareStatus.CONTRACT_SUCCESS
            )
            compare.request_pay()
            response_data = {"result": True, "msg": "요청되었습니다."}
        except Compare.DoesNotExist:
            response_data = {"result": False, "msg": "존재하지 않는 계약"}
        except CarCMSCompareError as e:
            response_data = {"result": False, "msg": e.msg}
        except Exception as e:
            response_data = {"result": False, "msg": str(e)}
        print(response_data)
        return JsonResponse(response_data)


class BankAccountForm(forms.Form):
    bank = forms.CharField(required=True)
    bank_account_no = forms.CharField(required=True)
    name = forms.CharField(required=True)
    ssn = forms.CharField(required=True)


class BankAccountView(AppTypeCheck, LoginRequiredMixin, CmsUserPermissionMixin, View):
    def get(self, request):
        response_data = {
            "bank": request.user.bank,
            "bank_account_no": request.user.bank_account_no,
            'real_name': request.user.real_name,
            'ssn': request.user.ssn
        }
        return JsonResponse(response_data)

    def post(self, request):
        form = BankAccountForm(request.POST)
        try:
            if form.is_valid() is False:
                raise Exception('잘못된 요청')
            account = request.user
            account.bank = form.cleaned_data.get('bank')
            account.bank_account_no = form.cleaned_data.get('bank_account_no')
            account.real_name = form.cleaned_data.get('name')
            account.ssn = form.cleaned_data.get('ssn')
            account.save()
            response_data = {"result": True}
        except Exception as e:
            response_data = {"result": False, "msg": str(e)}
        return JsonResponse(response_data)


class CustomerAuthView(View):
    def get(self, request, compare_id):
        compare = Compare.objects.exclude(danal_auth=None).select_related('danal_auth').get(id=compare_id)
        if compare.danal_auth.status == DanalAuthStatusChoice.COMPLETE:
            return HttpResponseRedirect(compare.danal_auth.auth_success_url)
        else:
            template_name = 'new_design/car_cms/danal_auth/danal_auth.html'
        return render(request, template_name, context={"compare": compare})
