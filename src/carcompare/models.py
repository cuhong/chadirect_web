import requests
from django.contrib.auth.base_user import BaseUserManager
from django.db import models

from commons.models import UUIDPkMixin, DateTimeMixin


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


class CompareManager(models.Manager):
    def create_compare(self, name, ssn_prefix, ssn_suffix, phone_company, phone1, phone2, phone3):
        compare = self.model(
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
    error = models.TextField(null=True, blank=True, verbose_name='에러')
    is_session_active = models.BooleanField(default=False, null=False, blank=False, verbose_name='세션켜짐')

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
        verbose_name = '비교 상세'
        verbose_name_plural = verbose_name

    object = CarNoManager()
    car_no = models.CharField(max_length=200, null=True, blank=True, verbose_name='차량번호')
    manufacturer = models.CharField(max_length=200, null=True, blank=True, verbose_name='제조사')
    car_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='차명')
    car_register_year = models.CharField(max_length=200, null=True, blank=True, verbose_name='등록년월')
    detail_car_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='세부차명')
    detail_option = models.CharField(max_length=200, null=True, blank=True, verbose_name='세부옵션')
    car_code = models.CharField(max_length=200, null=True, blank=True, verbose_name='차명코드')


class CompareDetail(models.Model):
    class Meta:
        verbose_name = '비교 상세'
        verbose_name_plural = verbose_name

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
    discount_mileage = models.CharField(max_length=200, null=True, blank=True, verbose_name='마일리지할인')
    discount_dist = models.CharField(max_length=200, null=True, blank=True, verbose_name='마일리지할인 거리')
    discount_child = models.CharField(max_length=200, null=True, blank=True, verbose_name='자녀할인')
    fetus = models.CharField(max_length=200, null=True, blank=True, verbose_name='태아여부',
                             help_text='자녀할인 YES시 값이 NULL이 아니면 태아로 인식')
    discount_child_year = models.CharField(max_length=200, null=True, blank=True, verbose_name='자녀생년')
    discount_child_month = models.CharField(max_length=200, null=True, blank=True, verbose_name='자녀생월')
    discount_child_day = models.CharField(max_length=200, null=True, blank=True, verbose_name='자녀생일')
    discount_pubtrans = models.CharField(max_length=200, null=True, blank=True, verbose_name='대중교통할인')
    discount_pubtrans_cost = models.CharField(max_length=200, null=True, blank=True, verbose_name='대중교통할인 요금')
    discount_safedriving = models.CharField(max_length=200, null=True, blank=True, verbose_name='안전운전할인(Tmap)')
    discount_safedriving_score = models.CharField(max_length=200, null=True, blank=True, verbose_name='티맵점수')
    discount_safedriving_h = models.CharField(max_length=200, null=True, blank=True, verbose_name='안전운전할인(현대)')
    discount_safedriving_score_h = models.CharField(max_length=200, null=True, blank=True, verbose_name='현대점수')
    discount_email = models.CharField(max_length=200, null=True, blank=True, verbose_name='이메일할인')
    discount_poverty = models.CharField(max_length=200, null=True, blank=True, verbose_name='서민할인')
    discount_premileage = models.CharField(max_length=200, null=True, blank=True, verbose_name='과거주행거리할인')
    discount_premileage_average = models.CharField(max_length=200, null=True, blank=True, verbose_name='과거연평균주행거리')
    discount_premileage_immediate = models.CharField(max_length=200, null=True, blank=True, verbose_name='직전연평균주행거리')
    discount_and = models.CharField(max_length=200, null=True, blank=True, verbose_name='사고통보장치할인')
    discount_adas = models.CharField(max_length=200, null=True, blank=True, verbose_name='차선이탈방지장치할인')
    discount_fca = models.CharField(max_length=200, null=True, blank=True, verbose_name='전방충돌방지장치확인')


class LegacyContract(models.Model):
    class Meta:
        verbose_name = '기존계약'
        verbose_name_plural = verbose_name

    compare = models.ForeignKey(Compare, null=False, blank=False, verbose_name='비교', on_delete=models.PROTECT)
    company_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='보험사')
    car_no = models.CharField(max_length=100, null=False, blank=False, verbose_name='차량번호')
    car_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='차명')
    due_date = models.CharField(max_length=100, null=False, blank=False, verbose_name='만기일')
