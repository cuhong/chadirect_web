import datetime
import pickle
import random
import time

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django.db.models import Case, When, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django import forms
from django.views.decorators.csrf import csrf_exempt

from account.models import Organization
from carcompare.models import Compare, StatusChoice, CarNo, CompareDetail
from carcompare.serializers import CompareDetailSerializer

User = get_user_model()

class AdminUserMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/admin/login'
    redirect_field_name = 'next'

    def test_func(self):
        return self.request.user.is_admin is True

    def get_login_url(self):
        if self.request.user.is_authenticated:
            return reverse('carcompare:start')
        return super().get_login_url()


class CompareStartForm(forms.ModelForm):
    class Meta:
        model = Compare
        fields = [
            'name',
            'ssn_prefix',
            'ssn_suffix',
            'phone_company',
            'phone1',
            'phone2',
            'phone3'
        ]

    def save(self, commit=True):
        instance = Compare.object.create_compare(
            name=self.cleaned_data.get('name'),
            ssn_prefix=self.cleaned_data.get('ssn_prefix'),
            ssn_suffix=self.cleaned_data.get('ssn_suffix'),
            phone_company=self.cleaned_data.get('phone_company'),
            phone1=self.cleaned_data.get('phone1'),
            phone2=self.cleaned_data.get('phone2'),
            phone3=self.cleaned_data.get('phone3'),
        )
        return instance


class CompareStartView(AdminUserMixin, View):
    def get(self, request):
        return render(request, 'carcompare/start.html')

    def post(self, request):
        form = CompareStartForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.user = request.user
            instance.save()
            instance.refresh_from_db()
            if instance.status == StatusChoice.WAIT_AUTH_NO:
                return JsonResponse({"result": True, "session_id": str(instance.id)}, status=200)
            else:
                return JsonResponse({"result": False, "error": str(instance.error)}, status=200)
        else:
            return HttpResponse(status=400)


class CompareShutDownView(AdminUserMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CompareShutDownView, self).dispatch(request, *args, **kwargs)

    def post(self, request, compare_id):
        try:
            compare = Compare.object.get(id=compare_id)
            compare.shutdown_session()
            compare.refresh_from_db()
        except Exception as e:
            pass
        response = JsonResponse({"result": True})
        return response


class CompareAuthView(AdminUserMixin, View):
    def post(self, request, compare_id):
        try:
            compare = Compare.object.get(id=compare_id)
            if compare.status == StatusChoice.WAIT_AUTH_NO:
                compare.check_auth_no(request.POST.get('auth_number', ''))
                compare.refresh_from_db()
                if compare.status == StatusChoice.AUTH_SUCCESS:
                    shutdown = False
                    response = JsonResponse({"result": True, "session_id": str(compare.id)}, status=200)
                elif compare.status == StatusChoice.AUTH_FAILED:
                    shutdown = True
                    response = JsonResponse({"result": False, "error": "????????? ????????? ????????? ????????? ??????????????????."}, status=200)
                elif compare.status == StatusChoice.ERROR:
                    shutdown = True
                    response = JsonResponse({"result": False, "error": "????????????"}, status=200)
                else:
                    shutdown = True
                    response = HttpResponse(status=400)
            else:
                shutdown = True
                response = JsonResponse({"result": False, "error": "???????????? ?????? ????????? ????????????."}, status=200)
        except Compare.DoesNotExist:
            shutdown = True
            response = HttpResponse(status=404)
        if shutdown is True:
            try:
                compare.shutdown_session()
            except:
                pass
        return response


class CompareView(AdminUserMixin, View):
    def get(self, request, compare_id):
        compare = Compare.object.prefetch_related('legacycontract_set', 'comparedetail_set').get(id=compare_id)
        manager_list = User.objects.filter(Q(is_admin=True) | Q(is_superuser=True)).annotate(
            is_me=Case(When(id=request.user.id, then=True), default=False, output_field=models.BooleanField())
        ).values(
            'name', 'cellphone', 'id', 'is_me'
        )
        organization_list = Organization.objects.values('id', 'name').filter(is_searchable=True)
        name = compare.name
        now_date = timezone.localdate()
        min_start_date = now_date + relativedelta(days=1)
        max_start_date = now_date + relativedelta(days=14)
        return render(request, 'carcompare/compare.html', context={
            "name": name, "compare_id": str(compare_id), "compare": compare,
            "min_start_date": min_start_date,
            "max_start_date": max_start_date,
            "manager_list": manager_list,
            "organization_list": organization_list
        })

    def post(self, request, compare_id):
        compare_data = request.POST
        with open('ipasd.txt', 'wb') as file:
            pickle.dump(compare_data, file)
        print(compare_data)
        compare = Compare.object.get(id=compare_id)
        # sample = {
        #     'start_date': ['2022-12-22'], 'manufacturer': ['??????'], 'car_name': ['?????????'], 'car_register_year': ['2011'],
        #     'detail_car_name': ['YF?????????2.0'], 'detail_option': ['5?????? Y20 ?????????,??????,?????????,P/S,ABS,AIR-D,IM(?????????)'],
        #     'treaty_range': ['????????????1???'], 'driver_1_birthdate': ['2003-03-07'], 'driver_2_birthdate': ['2003-03-07'],
        #     'coverage_bil': ['YES'], 'coverage_pdl': ['2??????'], 'coverage_mp_list': ['???????????????'],
        #     'coverage_mp': ['1??????/3?????????'], 'coverage_umbi': ['??????(2??????)'], 'coverage_cac': ['??????'], 'treaty_ers': ['YES'],
        #     'treaty_charge': ['50??????'], 'discount_bb': ['YES'], 'discount_bb_year': ['2022'],
        #     'discount_bb_month': ['01'], 'discount_bb_price': ['10'], 'discount_child': ['NO'],
        #     'csrfmiddlewaretoken': ['4bMhm7ORgvqAqErxBKMTsjzq6ekoAE3ucEjeGXASmFxj3R8cpvX63X40MkFAdSo0']
        # }
        driver_1_birthdate = datetime.datetime.strptime(compare_data.get('driver_1_birthdate'), "%Y-%m-%d").date()
        driver_2_birthdate = datetime.datetime.strptime(
            compare_data.get('driver_2_birthdate'), "%Y-%m-%d"
        ).date() if compare_data.get('driver_2_birthdate') not in ['', None] else None
        compare_detail = CompareDetail.objects.create(
            manager_id=compare_data.get('manager'),
            organization_id=None if compare_data.get('organization') in [None, ""] else int(compare_data.get('organization')),
            compare=compare,
            car_no=compare_data.get('carno'),
            start_date=datetime.datetime.strptime(compare_data.get('start_date'), "%Y-%m-%d").date(),
            manufacturer=compare_data.get('manufacturer'),
            car_name=compare_data.get('car_name'),
            car_register_year=compare_data.get('car_register_year'),
            detail_car_name=compare_data.get('detail_car_name'),
            detail_option=compare_data.get('detail_option'),
            treaty_range=compare_data.get('treaty_range'),
            driver_year=driver_1_birthdate.year,
            driver_month=driver_1_birthdate.month,
            driver_day=driver_1_birthdate.day,
            driver2_year=None if driver_2_birthdate is None else driver_2_birthdate.year,
            driver2_month=None if driver_2_birthdate is None else driver_2_birthdate.month,
            driver2_day=None if driver_2_birthdate is None else driver_2_birthdate.day,
            coverage_bil=compare_data.get('coverage_bil'),
            coverage_pdl=compare_data.get('coverage_pdl'),
            coverage_mp_list=compare_data.get('coverage_mp_list'),
            coverage_mp=compare_data.get('coverage_mp'),
            coverage_umbi=compare_data.get('coverage_umbi'),
            coverage_cac=compare_data.get('coverage_cac'),
            treaty_ers=compare_data.get('treaty_ers'),
            treaty_charge=compare_data.get('treaty_charge'),
            discount_bb=compare_data.get('discount_bb'),
            discount_bb_year=compare_data.get('discount_bb_year'),
            discount_bb_month=compare_data.get('discount_bb_month'),
            discount_bb_price="10" if compare_data.get('discount_bb_price') in ["", None] else compare_data.get(
                'discount_bb_price'),
        )
        compare_detail.request_estimate()
        compare_detail.refresh_from_db()
        if compare_detail.is_success is not True:
            response = JsonResponse({"result": False, "error": "????????? ????????? ??????????????????"}, status=200)
        else:
            response = JsonResponse({"result": True, "data": {
                "compare_detail_id": str(compare_detail.id),
                "car_no": compare_detail.car_no or "-",
                "start_date": compare_detail.start_date.strftime("%Y-%m-%d"),
                "manufacturer": compare_detail.manufacturer,
                "car_name": compare_detail.car_name,
            }}, status=200)
        return response


class CompareDetailView(AdminUserMixin, View):
    def get(self, request, compare_detail_id):
        try:
            compare_detail = CompareDetail.objects.get(id=compare_detail_id, is_success=True)
            # serializer = CompareDetailSerializer(instance=compare_detail)
            response = JsonResponse(data={"result": True, "data": compare_detail.image.url})
        except Exception as e:
            print(e)
            response = JsonResponse(data={"result": False, "msg": "???????????? ?????? ?????? id"})
        return response


class CarnoView(AdminUserMixin, View):
    def post(self, request):
        car_no = request.POST.get('car_no')
        instance = CarNo.object.search(car_no=car_no)
        if instance is None:
            response = JsonResponse({"result": False, "error": "?????? ?????? ??????"}, status=200)
        else:
            response = JsonResponse({
                "result": True,
                "data": {
                    "car_no": car_no,
                    "manufacturer": instance.manufacturer,
                    "car_name": instance.car_name,
                    "car_register_year": instance.car_register_year,
                    "detail_car_name": instance.detail_car_name,
                    "detail_option": instance.detail_option,
                    "car_code": instance.car_code,
                }
            })
        return response
