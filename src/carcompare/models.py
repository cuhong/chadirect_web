import datetime
import io
import os.path
import pickle
import uuid

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from sequences import get_next_value

from carcompare.utils.estimate import generate_estimate_image
from commons.models import UUIDPkMixin, DateTimeMixin, VehicleInsurerChoices
from itechs.storages import ProtectedFileStorageRemote, ProtectedFileStorageLocal


def generate_compare_serial():
    now_date = timezone.localdate().strftime('%Y%m%d')
    base = f"compare-{now_date}"
    sequence = get_next_value(base)
    return f"COMPARE-{now_date}-{str(sequence).zfill(5)}"


class PhoneCompanyChoice(models.TextChoices):
    SKT = '01', 'SKT'
    KT = '02', 'KT'
    LGU = '03', 'LGU+'
    SKT_A = '04', 'SKT 알뜰폰'
    KT_A = '05', 'KT 알뜰폰'
    LGU_A = '06', 'LGU+ 알뜰폰'


class StatusChoice(models.TextChoices):
    INIT = 'init', '초기화'
    WAIT_AUTH_NO = 'wait_auth_no', '인증번호 요청'
    AUTH_SUCCESS = 'auth_success', '인증 성공'
    AUTH_FAILED = 'auth_failed', '인증 실패'
    ERROR = 'error', '오류'


User = get_user_model()


class CompareManager(models.Manager):
    def create_compare(self, name, ssn_prefix, ssn_suffix, phone_company, phone1, phone2, phone3):
        compare = self.model(
            serial=generate_compare_serial(),
            name=name,
            ssn_prefix=ssn_prefix,
            ssn_suffix=ssn_suffix,
            phone_company=phone_company,
            phone1=phone1,
            phone2=phone2,
            phone3=phone3,
        )
        compare.save(using=self._db)
        # compare.init_session()
        # compare.refresh_from_db()
        compare.request_auth_no()
        return compare


class Compare(UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '견적비교'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    object = CompareManager()
    serial = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='시리얼', db_index=True,
        editable=False
    )
    user = models.ForeignKey(
        User, null=True, blank=True, verbose_name='사용자', on_delete=models.PROTECT,
        related_name='compare_user'
    )
    session_id = models.UUIDField(null=True, blank=True, verbose_name='세션 id')
    name = models.CharField(max_length=30, null=False, blank=False, verbose_name='성명')
    ssn_prefix = models.CharField(max_length=30, null=False, blank=False, verbose_name='주민번호 앞자리')
    ssn_suffix = models.CharField(max_length=30, null=False, blank=False, verbose_name='주민번호 뒷자리')
    phone_company = models.CharField(
        max_length=30, null=False, blank=False, verbose_name='통신사', choices=PhoneCompanyChoice.choices
    )
    phone1 = models.CharField(max_length=3, null=False, blank=False, verbose_name='휴대전화 1')
    phone2 = models.CharField(max_length=4, null=False, blank=False, verbose_name='휴대전화 2')
    phone3 = models.CharField(max_length=4, null=False, blank=False, verbose_name='휴대전화 3')
    status = models.CharField(
        max_length=30, null=False, blank=False, verbose_name='상태', default=StatusChoice.INIT,
        choices=StatusChoice.choices
    )
    auth_no = models.CharField(max_length=15, null=True, blank=True, verbose_name='인증번호', editable=False)
    error = models.TextField(null=True, blank=True, verbose_name='에러')
    is_session_active = models.BooleanField(default=False, null=False, blank=False, verbose_name='세션켜짐')

    def __str__(self):
        return self.serial or "-"

    @property
    def birthdate(self):
        _year = self.ssn_prefix[:2]
        month = self.ssn_prefix[2:4]
        day = self.ssn_prefix[4:6]
        _birthdate = datetime.date(int(f"20{_year}"), int(month), int(day))
        if _birthdate > timezone.localdate():
            return datetime.date(int(f"19{_year}"), int(month), int(day))
        else:
            return _birthdate

    def init_session(self):
        url = "https://its-api.net/api/service-init/"
        headers = {
            "content-type": "application/json; charset=utf-8",
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            self.session_id = response_data.get('session_id')
            self.is_session_active = True
        else:
            self.status = StatusChoice.ERROR
            self.error = '스크래핑 서버가 응답하지 않습니다.'
        self.save()

    def shutdown_session(self):
        url = "https://its-api.net/api/shutdown-browser/"
        headers = {
            "content-type": "application/json; charset=utf-8",
        }
        data = {
            "session_id": str(self.session_id),
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            self.is_session_active = False
        else:
            self.status = StatusChoice.ERROR
            self.error = '스크래핑 서버가 응답하지 않습니다.'
        self.save()

    def revive_session(self):
        url = "https://its-api.net/api/init-timeout/"
        headers = {
            "content-type": "application/json; charset=utf-8",
        }
        data = {
            "session_id": str(self.session_id),
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            self.is_session_active = response_data.get('message') != 'Fail'
        else:
            self.is_session_active = False
            self.status = StatusChoice.ERROR
            self.error = '스크래핑 서버가 응답하지 않습니다.'
        self.save()

    def request_auth_no(self):
        try:
            if self.session_id is None:
                url = "https://its-api.net/api/phone-auth-num/"
                headers = {
                    "content-type": "application/json; charset=utf-8",
                }
                data = {
                    "name": self.name,
                    "ssn_prefix": self.ssn_prefix,
                    "ssn_suffix": self.ssn_suffix,
                    "phone_company": self.phone_company,
                    "phone1": self.phone1,
                    "phone2": self.phone2,
                    "phone3": self.phone3
                }
            else:
                url = "https://its-api.net/api/send-auth-num/"
                headers = {
                    "content-type": "application/json; charset=utf-8",
                }
                data = {
                    "session_id": str(self.session_id),
                    "name": self.name,
                    "ssn_prefix": self.ssn_prefix,
                    "ssn_suffix": self.ssn_suffix,
                    "phone_company": self.phone_company,
                    "phone1": self.phone1,
                    "phone2": self.phone2,
                    "phone3": self.phone3
                }
            response = requests.post(url, json=data, headers=headers)
            status = int(response.status_code)
            print(status)
            print(response)
            if status == 200:
                response_data = response.json()
                print(response_data)
                if self.session_id is None:
                    self.session_id = response_data.get('session_id')
                self.status = StatusChoice.WAIT_AUTH_NO
                self.is_session_active = True
            elif status == 400:
                print(response.content)
                self.status = StatusChoice.ERROR
                self.error = '다모아 서비스가 정상적으로 응답하지 않습니다'
            elif status == 500:
                print(response.content)
                self.status = StatusChoice.ERROR
                self.error = '서버 오류'
        except Exception as e:
            self.status = StatusChoice.ERROR
            self.error = str(e)
        self.save()

    def check_auth_no(self, auth_no):
        response = None
        try:
            url = "https://its-api.net/api/phone-auth-check/"
            headers = {
                "content-type": "application/json; charset=utf-8",
            }
            data = {
                "session_id": str(self.session_id),
                "auth_number": auth_no
            }
            response = requests.post(url, json=data, headers=headers)
            self.auth_no = auth_no
            status_code = response.status_code
            if status_code == 200:
                self.status = StatusChoice.AUTH_SUCCESS
                self.get_ex_policy()
            elif status_code == 400:
                self.status = StatusChoice.ERROR
                self.error = '다모아 서비스가 정상적으로 응답하지 않습니다'
            elif status_code == 406:
                self.status = StatusChoice.AUTH_FAILED
                self.error = '다모아 서비스 사용이 제한된 사용자입니다.'
            elif status_code == 500:
                self.status = StatusChoice.ERROR
                self.error = '서버 오류'
        except Exception as e:
            self.status = StatusChoice.ERROR
            self.error = str(e)
        self.save()
        return response

    def get_ex_policy(self):
        response = None
        try:
            url = "https://its-api.net/api/expolicy-check/"
            headers = {
                "content-type": "application/json; charset=utf-8",
            }
            data = {
                "session_id": str(self.session_id),
            }
            response = requests.post(url, json=data, headers=headers)
            status_code = response.status_code
            if status_code == 200:
                response_data = response.json()
                LegacyContract.objects.bulk_create([
                    LegacyContract(
                        compare=self,
                        company_name=ex_policy.get('insu_name'),
                        car_no=ex_policy.get('car_no'),
                        car_name=ex_policy.get('car_name'),
                        due_date=ex_policy.get('due_date'),
                    ) for ex_policy in response_data.get('data', [])
                ])
            elif status_code == 500:
                self.status = StatusChoice.ERROR
                self.error = '서버 오류'
        except Exception as e:
            self.status = StatusChoice.ERROR
            self.error = str(e)
        self.save()
        return response


class CarNoManager(models.Manager):
    def search(self, car_no):
        try:
            instance = self.model.object.get(car_no=car_no)
            return instance
        except self.model.DoesNotExist:
            try:
                response = requests.post(
                    url="https://its-api.net/api/search-carnum/",
                    json={"car_no": car_no},
                    headers={
                        "content-type": "application/json; charset=utf-8",
                    }
                )
            except Exception as e:
                return None
            else:
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('message') == "Success":
                        car_data = response_data.get('data')
                        instance = self.model(
                            car_no=car_no,
                            manufacturer=car_data.get('manufacturer'),
                            car_name=car_data.get('car_name'),
                            car_register_year=car_data.get('register_year'),
                            detail_car_name=car_data.get('detail_name'),
                            detail_option=car_data.get('detail_option'),
                            car_code=car_data.get('car_code'),
                        )
                        instance.save(using=self._db)
                        return instance
                    else:
                        return None
                else:
                    return None


class CarNo(models.Model):
    class Meta:
        verbose_name = '차량번호'
        verbose_name_plural = verbose_name

    object = CarNoManager()
    car_no = models.CharField(max_length=200, null=True, blank=True, verbose_name='차량번호')
    manufacturer = models.CharField(max_length=200, null=True, blank=True, verbose_name='제조사')
    car_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='차명')
    car_register_year = models.CharField(max_length=200, null=True, blank=True, verbose_name='등록년월')
    detail_car_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='세부차명')
    detail_option = models.CharField(max_length=200, null=True, blank=True, verbose_name='세부옵션')
    car_code = models.CharField(max_length=200, null=True, blank=True, verbose_name='차명코드')


def compare_detail_upload_to(instance, filename):
    extension = filename.split(".")[-1]
    filename = f"{str(uuid.uuid4())}.{extension}"
    return os.path.join(timezone.localdate().strftime("%Y/%m/%d"), filename)


class CompareDetail(models.Model):
    class Meta:
        verbose_name = '비교 상세'
        verbose_name_plural = verbose_name

    manager = models.ForeignKey(User, null=True, blank=True, related_name='cd_user', on_delete=models.PROTECT, verbose_name='산출 담당자')
    compare = models.ForeignKey(Compare, null=False, blank=False, verbose_name='비교', on_delete=models.PROTECT)
    start_date = models.DateField(null=True, blank=True, verbose_name='보험개시일')
    car_no = models.CharField(max_length=200, null=True, blank=True, verbose_name='차량번호')
    manufacturer = models.CharField(max_length=200, null=True, blank=True, verbose_name='제조사')
    car_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='차명')
    car_register_year = models.CharField(max_length=200, null=True, blank=True, verbose_name='등록년월')
    detail_car_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='세부차명')
    detail_option = models.CharField(max_length=200, null=True, blank=True, verbose_name='세부옵션')
    treaty_range = models.CharField(max_length=200, null=True, blank=True, verbose_name='운전자범위')
    driver_year = models.CharField(max_length=200, null=True, blank=True, verbose_name='최소연령운전자 생년')
    driver_month = models.CharField(max_length=200, null=True, blank=True, verbose_name='최소연령운전자 생월')
    driver_day = models.CharField(max_length=200, null=True, blank=True, verbose_name='최소연령운전자 생일')
    driver2_year = models.CharField(max_length=200, null=True, blank=True, verbose_name='배우자 Or 지정 1인 생년')
    driver2_month = models.CharField(max_length=200, null=True, blank=True, verbose_name='배우자 Or 지정 1인 생월')
    driver2_day = models.CharField(max_length=200, null=True, blank=True, verbose_name='배우자 Or 지정 1인 생일')
    coverage_bil = models.CharField(max_length=200, null=True, blank=True, verbose_name='대인배상1')
    coverage_pdl = models.CharField(max_length=200, null=True, blank=True, verbose_name='대물배상')
    coverage_mp_list = models.CharField(max_length=200, null=True, blank=True, verbose_name='자손차상해 구분')
    coverage_mp = models.CharField(max_length=200, null=True, blank=True, verbose_name='자손차상해 가입금액')
    coverage_umbi = models.CharField(max_length=200, null=True, blank=True, verbose_name='무보험차상해')
    coverage_cac = models.CharField(max_length=200, null=True, blank=True, verbose_name='자기차량손해')
    treaty_ers = models.CharField(max_length=200, null=True, blank=True, verbose_name='긴급출동')
    treaty_charge = models.CharField(max_length=200, null=True, blank=True, verbose_name='물적사고 할증기준')
    discount_bb = models.CharField(max_length=200, null=True, blank=True, verbose_name='블랙박스 할인')
    discount_bb_year = models.CharField(max_length=200, null=True, blank=True, verbose_name='블랙박스 구입년')
    discount_bb_month = models.CharField(max_length=200, null=True, blank=True, verbose_name='블랙박스 구입월')
    discount_bb_price = models.CharField(max_length=200, null=True, blank=True, verbose_name='블랙박스 구입금액')
    discount_mileage = models.CharField(max_length=200, null=True, blank=True, verbose_name='마일리지할인', default="NO")
    discount_dist = models.CharField(max_length=200, null=True, blank=True, verbose_name='마일리지할인 거리')
    discount_child = models.CharField(max_length=200, null=True, blank=True, verbose_name='자녀할인', default="NO")
    fetus = models.CharField(max_length=200, null=True, blank=True, verbose_name='태아여부',
                             help_text='자녀할인 YES시 값이 NULL이 아니면 태아로 인식', default="")
    discount_child_year = models.CharField(max_length=200, null=True, blank=True, verbose_name='자녀생년')
    discount_child_month = models.CharField(max_length=200, null=True, blank=True, verbose_name='자녀생월')
    discount_child_day = models.CharField(max_length=200, null=True, blank=True, verbose_name='자녀생일')
    discount_pubtrans = models.CharField(max_length=200, null=True, blank=True, verbose_name='대중교통할인', default="NO")
    discount_pubtrans_cost = models.CharField(max_length=200, null=True, blank=True, verbose_name='대중교통할인 요금')
    discount_safedriving = models.CharField(max_length=200, null=True, blank=True, verbose_name='안전운전할인(Tmap)',
                                            default="NO")
    discount_safedriving_score = models.CharField(max_length=200, null=True, blank=True, verbose_name='티맵점수')
    discount_safedriving_h = models.CharField(max_length=200, null=True, blank=True, verbose_name='안전운전할인(현대)',
                                              default="NO")
    discount_safedriving_score_h = models.CharField(max_length=200, null=True, blank=True, verbose_name='현대점수')
    discount_email = models.CharField(max_length=200, null=True, blank=True, verbose_name='이메일할인', default="NO")
    discount_poverty = models.CharField(max_length=200, null=True, blank=True, verbose_name='서민할인', default="NO")
    discount_premileage = models.CharField(max_length=200, null=True, blank=True, verbose_name='과거주행거리할인', default="NO")
    discount_premileage_average = models.CharField(max_length=200, null=True, blank=True, verbose_name='과거연평균주행거리')
    discount_premileage_immediate = models.CharField(max_length=200, null=True, blank=True, verbose_name='직전연평균주행거리')
    discount_and = models.CharField(max_length=200, null=True, blank=True, verbose_name='사고통보장치할인', default="NO")
    discount_adas = models.CharField(max_length=200, null=True, blank=True, verbose_name='차선이탈방지장치할인', default="NO")
    discount_fca = models.CharField(max_length=200, null=True, blank=True, verbose_name='전방충돌방지장치확인', default="NO")
    is_success = models.BooleanField(default=None, null=True, blank=True, verbose_name='조회 성공 여부')
    error = models.TextField(null=True, blank=True, verbose_name='에러')
    image = models.ImageField(
        null=True, blank=True, storage=ProtectedFileStorageRemote(), upload_to=compare_detail_upload_to,
        verbose_name='견적서 이미지'
    )

    @property
    def car_title(self):
        return f"{self.manufacturer} {self.car_name} {self.detail_car_name}"

    @property
    def car_code(self):
        car_no_queryset = CarNo.object.filter(car_no=self.car_no)
        if car_no_queryset.exists():
            return car_no_queryset.first().car_code or None
        else:
            return None

    def render_image(self):
        _insurance_data = self.comparedetailestimate_set.values(
            'insurer', 'expect_cost', 'expect_cost_mileage_applied', 'dc_list'
        ).all()
        insurance_data = {}
        _min_cost = []
        for _data in _insurance_data:
            insurer = _data.get('insurer')
            if insurer in [
                VehicleInsurerChoices.HYUNDAI, VehicleInsurerChoices.KB, VehicleInsurerChoices.DB, VehicleInsurerChoices.HANHWA
            ]:
                _min_cost.append(_data.get('expect_cost'))
        min_cost = min(_min_cost)
        for _data in _insurance_data:
            expect_cost = _data.get('expect_cost')
            insurance_data[_data.get('insurer')] = {
                "expect_cost": expect_cost,
                "expect_cost_string": "산출불가" if expect_cost is None else f"{expect_cost:,}원",
                "dc_list": _data.get('dc_list'),
                "is_cheapest": expect_cost == min_cost
            }
        insurer_1 = insurance_data.get(VehicleInsurerChoices.HYUNDAI.value, None)
        insurer_2 = insurance_data.get(VehicleInsurerChoices.DB.value, None)
        insurer_3 = insurance_data.get(VehicleInsurerChoices.KB.value, None)
        insurer_4 = insurance_data.get(VehicleInsurerChoices.HANHWA.value, None)
        manager = self.manager or self.compare.user
        data = {
            "manager_name": manager.name,
            "manager_contact": manager.cellphone,
            "insured_name": self.compare.name,
            "insured_birthdate": self.compare.birthdate.strftime("%Y-%m-%d"),
            "car_name": self.car_title,
            "car_detail": f"차명코드 : {self.car_code or '-'}",
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "driver_range": self.treaty_range,
            "min_driver_birthdate": self.youngest_driver_birthdate.strftime("%Y-%m-%d"),
            "insure_1": "현대해상 다이렉트",
            "insure_1_premium": insurer_1.get('expect_cost_string') if insurer_1 else "산출불가",
            "insure_1_memo": "최저" if insurance_data.get(VehicleInsurerChoices.HYUNDAI.value, {}).get('is_cheapest', False) is True else None,
            "insure_2": "DB손해보험 다이렉트",
            "insure_2_premium": insurer_2.get('expect_cost_string') if insurer_2 else "산출불가",
            "insure_2_memo": "최저" if insurance_data.get(VehicleInsurerChoices.DB.value, {}).get('is_cheapest', False) is True else None,
            "insure_3": "KB손해보험 다이렉트",
            "insure_3_premium": insurer_3.get('expect_cost_string') if insurer_3 else "산출불가",
            "insure_3_memo": "최저" if insurance_data.get(VehicleInsurerChoices.KB.value, {}).get('is_cheapest', False) is True else None,
            "insure_4": "한화손해보험 다이렉트",
            "insure_4_premium": insurer_4.get('expect_cost_string') if insurer_4 else "산출불가",
            "insure_4_memo": "최저" if insurance_data.get(VehicleInsurerChoices.HANHWA.value, {}).get('is_cheapest', False) is True else None,
            "p_1": "의무",
            "p_2": self.coverage_pdl,
            "p_3": "무한",
            "p_4": f"{self.coverage_mp_list} {self.coverage_mp}",
            "p_5": self.coverage_umbi,
            "p_6": self.coverage_cac,
            "p_7": self.treaty_ers,
            "p_8": "가입" if self.discount_bb == "YES" else "미가입",
        }
        with io.BytesIO() as bytes_io:
            pil_image = generate_estimate_image(data)
            pil_image.save(fp=bytes_io, format='PNG')
            content = ContentFile(bytes_io.getvalue(), 'estimagte.png')
        self.image = content
        self.save()
        return self.image.url

    @property
    def driver_birthdate(self):
        return datetime.date(int(self.driver_year), int(self.driver_month), int(self.driver_day))

    @property
    def driver_2_birthdate(self):
        if any([self.driver2_year is None, self.driver2_month is None, self.driver2_day is None]) is True:
            return None
        return datetime.date(int(self.driver2_year), int(self.driver2_month), int(self.driver2_day))

    @property
    def youngest_driver_birthdate(self):
        if self.driver_2_birthdate is None:
            return self.driver_birthdate
        return min(self.driver_birthdate, self.driver_2_birthdate)

    def request_estimate(self):
        try:
            _data = {
                "auth_number": self.compare.auth_no,
                "car_no": self.car_no,
                "session_id": str(self.compare.session_id),
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "manufacturer": self.manufacturer,
                "car_name": self.car_name,
                "car_register_year": self.car_register_year,
                "detail_car_name": self.detail_car_name,
                "detail_option": self.detail_option,
                "treaty_range": self.treaty_range,
                "driver_year": self.driver_year,
                "driver_month": str(self.driver_month).zfill(2),
                "driver_day": str(self.driver_day).zfill(2),
                "driver2_year": self.driver2_year,
                "driver2_month": str(self.driver2_month).zfill(2),
                "driver2_day": str(self.driver2_day).zfill(2),
                "coverage_bil": self.coverage_bil,
                "coverage_pdl": self.coverage_pdl,
                "coverage_mp_list": self.coverage_mp_list,
                "coverage_mp": self.coverage_mp,
                "coverage_umbi": self.coverage_umbi,
                "coverage_cac": self.coverage_cac,
                "treaty_ers": self.treaty_ers,
                "treaty_charge": self.treaty_charge,
                "discount_bb": self.discount_bb,
                "discount_bb_year": self.discount_bb_year,
                "discount_bb_month": str(self.discount_bb_month).zfill(2),
                "discount_bb_price": self.discount_bb_price,
                "discount_mileage": self.discount_mileage,
                "discount_dist": self.discount_dist,
                "discount_child": self.discount_child,
                "fetus": self.fetus,
                "discount_child_year": self.discount_child_year,
                "discount_child_month": self.discount_child_month,
                "discount_child_day": self.discount_child_day,
                "discount_pubtrans": self.discount_pubtrans,
                "discount_pubtrans_cost": self.discount_pubtrans_cost,
                "discount_safedriving": self.discount_safedriving,
                "discount_safedriving_score": self.discount_safedriving_score,
                "discount_safedriving_h": self.discount_safedriving_h,
                "discount_safedriving_score_h": self.discount_safedriving_score_h,
                "discount_email": self.discount_email,
                "discount_poverty": self.discount_poverty,
                "discount_premileage": self.discount_premileage,
                "discount_premileage_average": self.discount_premileage_average,
                "discount_premileage_immediate": self.discount_premileage_immediate,
                "discount_and": self.discount_and,
                "discount_adas": self.discount_adas,
                "discount_fca": self.discount_fca,
            }
            for key, value in _data.items():
                if value is None:
                    _data[key] = ''
                else:
                    _data[key] = str(value)
            response = requests.post(
                url="https://its-api.net/api/result-list/",
                # url="https://its-api.net/api/recall-result/",
                # json=_data,
                data=_data,
                headers={
                    # "content-type": "application/json; charset=utf-8",
                    "content-type": "application/x-www-form-urlencoded",
                }
            )
            status_code = response.status_code
            if status_code == 200:
                response_data = response.json()
                with open('result.txt', 'wb') as file:
                    pickle.dump(response.json(), file)
                if response_data.get('message', None) != "Success":
                    self.is_success = False
                    self.error = '서버 오류'
                else:
                    self.is_success = True
                    premium_list = response_data.get('data')
                    for premium in premium_list:
                        _expect_cost = "".join([s for s in str(premium.get('expect_cost')) if s.isdigit()])
                        _expect_cost_mileage_applied = "".join(
                            [s for s in str(premium.get('applied_expect_cost')) if s.isdigit()])
                        expect_cost = None if _expect_cost == "" else int(_expect_cost)
                        expect_cost_mileage_applied = None if _expect_cost_mileage_applied == "" else int(
                            _expect_cost_mileage_applied)
                        dc_list = [dc.get('dcName') for dc in premium.get('dc_list', [])]
                        insurer_string = premium.get('insu_name')
                        if "메리츠" in insurer_string:
                            insurer = VehicleInsurerChoices.MERITZ
                        elif "한화" in insurer_string:
                            insurer = VehicleInsurerChoices.HANHWA
                        elif "롯데" in insurer_string:
                            insurer = VehicleInsurerChoices.LOTTE
                        elif "MG" in insurer_string:
                            insurer = VehicleInsurerChoices.MG
                        elif "흥국" in insurer_string:
                            insurer = VehicleInsurerChoices.HEUNGKUK
                        elif "삼성" in insurer_string:
                            insurer = VehicleInsurerChoices.SAMSUNG
                        elif "현대" in insurer_string:
                            insurer = VehicleInsurerChoices.HYUNDAI
                        elif "DB" in insurer_string:
                            insurer = VehicleInsurerChoices.DB
                        elif "캐롯" in insurer_string:
                            insurer = VehicleInsurerChoices.CARROT
                        elif "AXA" in insurer_string:
                            insurer = VehicleInsurerChoices.AXA
                        elif "하나" in insurer_string:
                            insurer = VehicleInsurerChoices.HANA
                        elif "KB" in insurer_string:
                            insurer = VehicleInsurerChoices.KB
                        else:
                            insurer = VehicleInsurerChoices.ETC
                        CompareDetailEstimate.objects.create(
                            compare_detail=self,
                            insurer=insurer,
                            expect_cost=expect_cost,
                            expect_cost_mileage_applied=expect_cost_mileage_applied,
                            dc_list=dc_list
                        )
                        try:
                            self.render_image()
                        except Exception as e:
                            print(e)
            elif status_code == 406:
                self.is_success = False
                self.error = '다모아 서비스 사용이 제한된 사용자입니다.'
            elif status_code == 500:
                self.is_success = False
                self.error = '서버 오류'
        except Exception as e:
            self.is_success = False
            self.error = str(e)
        self.save()


class CompareDetailEstimate(models.Model):
    class Meta:
        verbose_name = '견적 상세'
        verbose_name_plural = verbose_name

    compare_detail = models.ForeignKey(CompareDetail, null=False, blank=False, verbose_name='비교 상세',
                                       on_delete=models.PROTECT)
    insurer = models.CharField(
        max_length=100, null=False, blank=False, choices=VehicleInsurerChoices.choices, verbose_name='보험사'
    )
    expect_cost = models.PositiveIntegerField(null=True, blank=True, verbose_name='마일리지 할인 전 보험료')
    expect_cost_mileage_applied = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='마일리지 할인 전 보험료'
    )
    dc_list = ArrayField(
        models.CharField(max_length=100, null=False, blank=False), null=True, verbose_name='적용 할인'
    )


class LegacyContract(models.Model):
    class Meta:
        verbose_name = '기존계약'
        verbose_name_plural = verbose_name

    compare = models.ForeignKey(Compare, null=False, blank=False, verbose_name='비교', on_delete=models.PROTECT)
    company_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='보험사')
    car_no = models.CharField(max_length=100, null=False, blank=False, verbose_name='차량번호')
    car_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='차명')
    due_date = models.CharField(max_length=100, null=False, blank=False, verbose_name='만기일')

    @property
    def due_date_date_instance(self):
        try:
            return datetime.datetime.strptime(self.due_date, "%Y년%m월%d일").date()
        except:
            return None
