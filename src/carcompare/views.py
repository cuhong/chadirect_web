import random
import time

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django import forms

from carcompare.models import Compare, StatusChoice, CarNo


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


class CompareStartView(View):
    def get(self, request):
        return render(request, 'carcompare/start.html')

    def post(self, request):
        form = CompareStartForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.refresh_from_db()
            if instance.status == StatusChoice.WAIT_AUTH_NO:
                return JsonResponse({"result": True, "session_id": str(instance.id)}, status=200)
            else:
                return JsonResponse({"result": False, "error": str(instance.error)}, status=200)
        else:
            return HttpResponse(status=400)


class CompareAuthView(View):
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
                    response = JsonResponse({"result": False, "error": "다모아 서비스 사용이 제한된 사용자입니다."}, status=200)
                elif compare.status == StatusChoice.ERROR:
                    shutdown = True
                    response = JsonResponse({"result": False, "error": "서버오류"}, status=200)
                else:
                    shutdown = True
                    response = HttpResponse(status=400)
            else:
                shutdown = True
                response = JsonResponse({"result": False, "error": "인증번호 대기 상태가 아닙니다."}, status=200)
        except Compare.DoesNotExist:
            shutdown = True
            response = HttpResponse(status=404)
        if shutdown is True:
            try:
                compare.shutdown_session()
            except:
                pass
        return response


class CompareView(View):
    def get(self, request, compare_id):
        compare = Compare.object.prefetch_related('legacycontract_set').get(id=compare_id)
        name = compare.name
        return render(request, 'carcompare/compare.html', context={
            "name": name, "compare_id": str(compare_id), "compare": compare
        })

    def post(self, request, compare_id):
        compare = Compare.object.get(id=compare_id)
        r = random.randint(8, 14)
        time.sleep(r)
        response = JsonResponse({"result": False, "error": "보험료 조회에 실패했습니다"}, status=200)
        return response


class CarnoView(View):
    def post(self, request):
        car_no = request.POST.get('car_no')
        instance = CarNo.object.search(car_no=car_no)
        if instance is None:
            response = JsonResponse({"result": False, "error": "차량 조회 실패"}, status=200)
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
