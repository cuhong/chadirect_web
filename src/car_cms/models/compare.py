import io
import os
import urllib.parse
import uuid
from traceback import print_exc

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from sequences import get_next_value

from car_cms.exceptions.compare import CarCMSCompareError
from car_cms.models.upload import compare_attach_upload_to
from carcompare.utils.estimate import generate_estimate_image
from commons.models import DateTimeMixin, UUIDPkMixin, VehicleInsurerChoices
from itechs.storages import ProtectedFileStorage
from simple_history.models import HistoricalRecords

from payment.models import DanalAuth


class PhoneCompanyChoice(models.TextChoices):
    SKT = '01', 'SKT'
    KT = '02', 'KT'
    LGU = '03', 'LGU+'
    SKT_A = '04', 'SKT 알뜰폰'
    KT_A = '05', 'KT 알뜰폰'
    LGU_A = '06', 'LGU+ 알뜰폰'


class CompareStatus(models.IntegerChoices):
    REQUEST = 0, '견적요청'
    CALCULATE = 1, '견적 산출중'
    CALCULATE_COMPLETE = 2, '견적완료'
    CALCULATE_DENY = 7, '견적산출 불가'
    DENY = 3, '견적거절'
    CONTRACT = 4, '계약요청'
    CONTRACT_SUCCESS = 5, '계약체결'
    CONTRACT_FAIL = 6, '계약거절'


class DriverRangeChoices(models.IntegerChoices):
    ONLY = 0, '피보험자 1인'
    ONLY_1 = 1, '피보험자 1인+지정1인'
    ANY = 2, '누구나'
    COUPLE = 3, '부부'
    COUPLE_1 = 4, '부부+지정1인'
    FAMILY = 5, '가족'
    FAMILY_1 = 6, '가족+지정1인'
    FAMILY_BRO = 7, '가족+형제자매'
    PRIVATE_COMPANY = 8, '개인사업자(임직원한정)'
    CO_COMPANY_EMP = 9, '법인사업자(임직원한정)'
    CO_COMPANY = 10, '법인사업자(누구나)'


class CustomerTypeChoices(models.IntegerChoices):
    PERSONAL = 0, '개인'
    COMPANY = 1, '사업자'


class CarTypeChoices(models.IntegerChoices):
    NEW = 0, '신차'
    USED = 1, '기존 차량'


class BodilyInjuryChoices(models.IntegerChoices):
    F = 0, '미가입'
    T = 1, '가입'


class LiabilityChoices(models.IntegerChoices):
    F = 0, '미가입'
    T20 = 1, '2천만원'
    T30 = 2, '3천만원'
    T50 = 3, '5천만원'
    T100 = 4, '1억'
    T200 = 5, '2억'
    T300 = 6, '3억'
    T500 = 7, '5억'


class SelfInjuryChoices(models.IntegerChoices):
    F = 0, '미가입'
    N15_15 = 1, '자손 1천5백/1천5백'
    N30_15 = 2, '자손 3천/1천5백'
    N50_15 = 3, '자손 5천/1천5백'
    N100_30 = 4, '자손 1억/3천'
    S100_20 = 5, '자상 1억/2천'
    S100_30 = 6, '자상 1억/3천'
    S200_20 = 7, '자상 2억/2천'
    S200_30 = 8, '자상 2억/3천'


class UninsuredChoices(models.IntegerChoices):
    F = 0, '미가입'
    T200 = 1, '2억'


class SelfDamageChoices(models.IntegerChoices):
    F = 0, '미가입'
    T = 1, '가입'


class EmergencyChoices(models.IntegerChoices):
    F = 0, '미가입'
    N = 1, '일반형'
    S = 2, '고급형'


class BlackBoxChoices(models.IntegerChoices):
    F = 0, '미가입'
    T = 1, '가입'


class EstimateMixin(models.Model):
    class Meta:
        abstract = True

    insured_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='피보험자명')
    birthdate = models.DateField(null=True, blank=True, verbose_name='생년월일')
    car_no = models.CharField(max_length=50, null=True, blank=True, verbose_name='차량번호')
    vin = models.CharField(max_length=50, null=True, blank=True, verbose_name='차대번호')
    car_name_fixed = models.CharField(max_length=50, null=True, blank=True, verbose_name='차량모델')
    start_at = models.DateField(null=True, blank=True, verbose_name='개시날짜', default=timezone.localdate)
    driver_range_fixed = models.IntegerField(
        choices=DriverRangeChoices.choices, default=DriverRangeChoices.ONLY, null=True, blank=True,
        verbose_name='운전자 한정'
    )
    min_age = models.IntegerField(
        null=True, blank=True, verbose_name='최저운전자 나이', help_text='값이 없을 경우 미지정'
    )
    min_age_birthdate = models.DateField(
        null=True, blank=True, verbose_name='최저운전자 생년월일', help_text='값이 없을 경우 미지정'
    )
    bi_2 = models.IntegerField(
        choices=BodilyInjuryChoices.choices, default=BodilyInjuryChoices.T, blank=True, null=True, verbose_name='대인2',
    )
    li = models.IntegerField(
        choices=LiabilityChoices.choices, null=True, blank=True, default=LiabilityChoices.T300, verbose_name='대물배상'
    )
    self_injury = models.IntegerField(
        choices=SelfInjuryChoices.choices, null=True, blank=True, verbose_name='자손/자상',
        default=SelfInjuryChoices.S100_30
    )
    uninsured = models.IntegerField(
        choices=UninsuredChoices.choices, null=True, blank=True, default=UninsuredChoices.T200, verbose_name='무보험차상해'
    )
    self_damage = models.IntegerField(
        choices=SelfDamageChoices.choices, null=True, blank=True, default=SelfDamageChoices.T, verbose_name='자기차량손해'
    )
    emergency = models.IntegerField(
        choices=EmergencyChoices.choices, null=True, blank=True, default=EmergencyChoices.S, verbose_name='긴급출동'
    )
    blackbox = models.IntegerField(
        choices=BlackBoxChoices.choices, null=True, blank=True, default=BlackBoxChoices.T, verbose_name='블랙박스'
    )
    estimate_insurer_1 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 1',
        default=VehicleInsurerChoices.HYUNDAI
    )
    estimate_premium_1 = models.IntegerField(null=True, blank=True, verbose_name='보험료 1')
    estimate_memo_1 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 1')
    estimate_insurer_2 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 2',
        default=VehicleInsurerChoices.DB
    )
    estimate_premium_2 = models.IntegerField(null=True, blank=True, verbose_name='보험료 2')
    estimate_memo_2 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 2')
    estimate_insurer_3 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 3',
        default=VehicleInsurerChoices.KB
    )
    estimate_premium_3 = models.IntegerField(null=True, blank=True, verbose_name='보험료 3')
    estimate_memo_3 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 3')
    estimate_insurer_4 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 4',
        default=VehicleInsurerChoices.HANHWA
    )
    estimate_premium_4 = models.IntegerField(null=True, blank=True, verbose_name='보험료 4')
    estimate_memo_4 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 4')
    estimate_insurer_5 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 5',
        default=VehicleInsurerChoices.MERITZ
    )
    estimate_premium_5 = models.IntegerField(null=True, blank=True, verbose_name='보험료 5')
    estimate_memo_5 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 5')
    estimate_insurer_6 = models.CharField(
        max_length=10, default=VehicleInsurerChoices.HANA,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 6'
    )
    estimate_premium_6 = models.IntegerField(null=True, blank=True, verbose_name='보험료 6')
    estimate_memo_6 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 6')
    estimate_insurer_7 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 7'
    )
    estimate_premium_7 = models.IntegerField(null=True, blank=True, verbose_name='보험료 7')
    estimate_memo_7 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 7')
    estimate_insurer_8 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 8'
    )
    estimate_premium_8 = models.IntegerField(null=True, blank=True, verbose_name='보험료 8')
    estimate_memo_8 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 8')
    estimate_insurer_9 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 9'
    )
    estimate_premium_9 = models.IntegerField(null=True, blank=True, verbose_name='보험료 9')
    estimate_memo_9 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 9')
    estimate_insurer_10 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 10'
    )
    estimate_premium_10 = models.IntegerField(null=True, blank=True, verbose_name='보험료 10')
    estimate_memo_10 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 10')
    estimate_insurer_11 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 11'
    )
    estimate_premium_11 = models.IntegerField(null=True, blank=True, verbose_name='보험료 11')
    estimate_memo_11 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 11')
    estimate_insurer_12 = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사 12'
    )
    estimate_premium_12 = models.IntegerField(null=True, blank=True, verbose_name='보험료 12')
    estimate_memo_12 = models.CharField(max_length=100, null=True, blank=True, verbose_name='비고 12')

    insurer = models.CharField(
        max_length=10,
        choices=VehicleInsurerChoices.choices, null=True, blank=True, verbose_name='보험사'
    )
    premium = models.IntegerField(null=True, blank=True, verbose_name='보험료')
    policy_no = models.CharField(max_length=150, null=True, blank=True, verbose_name='증권번호')
    policy_image = models.FileField(
        null=True, blank=True, upload_to=compare_attach_upload_to, storage=ProtectedFileStorage(),
        verbose_name='증권이미지'
    )
    contract_memo = models.TextField(null=True, blank=True, verbose_name='계약 특이사항')

    def validate_success(self):
        # 계약완료 가능 여부를 확인한다.
        messages = []
        if self.insurer is None:
            messages.append('보험사')
        if self.premium is None:
            messages.append('보험료')
        if self.policy_no is None:
            messages.append('증권번호')
        if self.policy_image in ['', None]:
            messages.append('증권이미지')
        return messages

    def validate_calculate_complete(self, user):
        # 견적완료 가능 여부를 확인한다.
        messages = []
        if self.estimate_image.name == '':
            if self.insured_name is None:
                messages.append('피보험자명')
            if self.birthdate is None:
                messages.append('피보험자 생년월일')
            if self.car_type == CarTypeChoices.NEW:
                # 신차
                pass
            else:
                # 중고차
                if all([self.car_no is None, self.vin is None]):
                    messages.append('차량번호와 차대번호 중 하나')
            if self.car_name_fixed is None:
                messages.append('차량모델')
            if self.start_at is None:
                messages.append('개시일자')
            est_count = 0
            for i in range(1, 13):
                estimate_insurer = getattr(self, f"estimate_insurer_{i}")
                estimate_premium = getattr(self, f"estimate_premium_{i}")
                est = all([estimate_insurer is not None, estimate_premium is not None])
                if est:
                    est_count += 1
            if est_count == 0:
                messages.append('보험사와 보험료')
            if len(messages) == 0:
                # 견적서 이미지 생성 위한 데이터
                insurance_data = {}
                _min_cost = []
                for i in range(1, 13):
                    estimate_insurer = getattr(self, f"estimate_insurer_{i}")
                    estimate_premium = getattr(self, f"estimate_premium_{i}")
                    estimate_memo = getattr(self, f"estimate_memo_{i}")
                    if estimate_insurer in [
                        VehicleInsurerChoices.HYUNDAI, VehicleInsurerChoices.KB, VehicleInsurerChoices.DB,
                        VehicleInsurerChoices.HANHWA, VehicleInsurerChoices.HANA
                    ]:
                        _min_cost.append(estimate_premium)
                        insurance_data[estimate_insurer] = {
                            "expect_cost": estimate_premium,
                            "expect_cost_string": "산출불가" if estimate_premium is None else f"{estimate_premium:,}원",
                            "dc_list": [] if estimate_memo is None else [estimate_memo]
                        }
                for key, value in insurance_data.items():
                    _cheapest = value['expect_cost'] == min(_min_cost)
                    value['is_cheapest'] = "최저" if _cheapest is True else None
                insurer_1 = insurance_data.get(VehicleInsurerChoices.HYUNDAI.value, None)
                insurer_2 = insurance_data.get(VehicleInsurerChoices.DB.value, None)
                insurer_3 = insurance_data.get(VehicleInsurerChoices.KB.value, None)
                insurer_4 = insurance_data.get(VehicleInsurerChoices.HANHWA.value, None)
                insurer_5 = insurance_data.get(VehicleInsurerChoices.HANA.value, None)
                manager = user
                data = {
                    "manager_name": manager.name,
                    "manager_contact": manager.cellphone,
                    "insured_name": self.insured_name,
                    "insured_birthdate": self.birthdate.strftime("%Y-%m-%d"),
                    "car_name": self.car_name_fixed,
                    "car_detail": f"차명코드 : -",
                    "start_date": self.start_at.strftime("%Y-%m-%d"),
                    "driver_range": self.get_driver_range_fixed_display(),
                    "min_driver_birthdate": "-" if self.min_age is None else self.min_age,
                    "insure_1": "현대해상 다이렉트",
                    "insure_1_premium": insurer_1.get('expect_cost_string') if insurer_1 else "산출불가",
                    "insure_1_memo": "최저" if insurance_data.get(VehicleInsurerChoices.HYUNDAI.value, {}).get(
                        'is_cheapest', False) is True else None,
                    "insure_2": "DB손해보험 다이렉트",
                    "insure_2_premium": insurer_2.get('expect_cost_string') if insurer_2 else "산출불가",
                    "insure_2_memo": "최저" if insurance_data.get(VehicleInsurerChoices.DB.value, {}).get('is_cheapest',
                                                                                                        False) is True else None,
                    "insure_3": "KB손해보험 다이렉트",
                    "insure_3_premium": insurer_3.get('expect_cost_string') if insurer_3 else "산출불가",
                    "insure_3_memo": "최저" if insurance_data.get(VehicleInsurerChoices.KB.value, {}).get('is_cheapest',
                                                                                                        False) is True else None,
                    "insure_4": "한화손해보험 다이렉트",
                    "insure_4_premium": insurer_4.get('expect_cost_string') if insurer_4 else "산출불가",
                    "insure_4_memo": "최저" if insurance_data.get(VehicleInsurerChoices.HANHWA.value, {}).get(
                        'is_cheapest', False) is True else None,
                    "insure_5": "하나손해보험 다이렉트",
                    "insure_5_premium": insurer_5.get('expect_cost_string') if insurer_5 else "산출불가",
                    "insure_5_memo": "최저" if insurance_data.get(VehicleInsurerChoices.HANA.value, {}).get(
                        'is_cheapest', False) is True else None,
                    "p_1": "의무",
                    "p_2": self.get_li_display(),
                    "p_3": "무한",
                    "p_4": f"{self.get_self_injury_display()}",
                    "p_5": self.get_uninsured_display(),
                    "p_6": self.get_self_damage_display(),
                    "p_7": self.get_emergency_display(),
                    "p_8": self.get_blackbox_display(),
                }
                try:
                    backgroud_image_url = self.account.organization.estimate_background.url
                except:
                    backgroud_image_url = None
                with io.BytesIO() as bytes_io:
                    pil_image = generate_estimate_image(data, backgroud_image_url=backgroud_image_url)
                    pil_image.save(fp=bytes_io, format='PNG')
                    content = ContentFile(bytes_io.getvalue(), 'estimagte.png')
                self.estimate_image = content
                self.save()
            return messages
        else:
            return messages


class ChannelChoices(models.TextChoices):
    DIRECT = 'direct', '다이렉트'
    LEGACY = 'legacy', '일반'


m_dat = [
    {'code': 'l01', 'name': 'hyundai', 'static_path': 'car_cms/manufacturer/local_01_hyundai.png'},
    {'code': 'l02', 'name': 'kia', 'static_path': 'car_cms/manufacturer/local_02_kia.png'},
    {'code': 'l03', 'name': 'genesis', 'static_path': 'car_cms/manufacturer/local_03_genesis.png'},
    {'code': 'l04', 'name': 'renault', 'static_path': 'car_cms/manufacturer/local_04_renault.png'},
    {'code': 'l05', 'name': 'chevrolet', 'static_path': 'car_cms/manufacturer/local_05_chevrolet.png'},
    {'code': 'l06', 'name': 'ssangyong', 'static_path': 'car_cms/manufacturer/local_06_ssangyong.png'},
    {'code': 'f01', 'name': 'benz', 'static_path': 'car_cms/manufacturer/foreign_01_benz.png'},
    {'code': 'f02', 'name': 'bmw', 'static_path': 'car_cms/manufacturer/foreign_02_bmw.png'},
    {'code': 'f03', 'name': 'audi', 'static_path': 'car_cms/manufacturer/foreign_03_audi.png'},
    {'code': 'f04', 'name': 'volkswagen', 'static_path': 'car_cms/manufacturer/foreign_04_volkswagen.png'},
    {'code': 'f05', 'name': 'volvo', 'static_path': 'car_cms/manufacturer/foreign_05_volvo.png'},
    {'code': 'f06', 'name': 'mini', 'static_path': 'car_cms/manufacturer/foreign_06_mini.png'},
    {'code': 'f07', 'name': 'lexus', 'static_path': 'car_cms/manufacturer/foreign_07_lexus.png'},
    {'code': 'f08', 'name': 'porsche', 'static_path': 'car_cms/manufacturer/foreign_08_porsche.png'},
    {'code': 'f09', 'name': 'honda', 'static_path': 'car_cms/manufacturer/foreign_09_honda.png'},
    {'code': 'f10', 'name': 'toyota', 'static_path': 'car_cms/manufacturer/foreign_10_toyota.png'},
    {'code': 'f11', 'name': 'jeep', 'static_path': 'car_cms/manufacturer/foreign_11_jeep.png'},
    {'code': 'f12', 'name': 'ford', 'static_path': 'car_cms/manufacturer/foreign_12_ford.png'},
    {'code': 'f13', 'name': 'landrover', 'static_path': 'car_cms/manufacturer/foreign_13_landrover.png'},
    {'code': 'f14', 'name': 'lincoln', 'static_path': 'car_cms/manufacturer/foreign_14_lincoln.png'},
    {'code': 'f15', 'name': 'peugeot', 'static_path': 'car_cms/manufacturer/foreign_15_peugeot.png'},
    {'code': 'f16', 'name': 'cadillac', 'static_path': 'car_cms/manufacturer/foreign_16_cadillac.png'},
    {'code': 'f16b', 'name': 'tesla', 'static_path': 'car_cms/manufacturer/foreign_16b_tesla.png'},
    {'code': 'f17', 'name': 'maserati', 'static_path': 'car_cms/manufacturer/foreign_17_maserati.png'},
    {'code': 'f18', 'name': 'bentley', 'static_path': 'car_cms/manufacturer/foreign_18_bentley.png'},
    {'code': 'f19', 'name': 'lamborghini', 'static_path': 'car_cms/manufacturer/foreign_19_lamborghini.png'},
    {'code': 'f20', 'name': 'citroen', 'static_path': 'car_cms/manufacturer/foreign_20_citroen.png'},
    {'code': 'f21', 'name': 'ds', 'static_path': 'car_cms/manufacturer/foreign_21_ds.png'},
    {'code': 'f22', 'name': 'jaguar', 'static_path': 'car_cms/manufacturer/foreign_22_jaguar.png'},
    {'code': 'f23', 'name': 'rollsroyce', 'static_path': 'car_cms/manufacturer/foreign_23_rollsroyce.png'},
    {'code': 'f51', 'name': 'Maybach', 'static_path': 'car_cms/manufacturer/foreign_51_Maybach.png'},
    {'code': 'f52', 'name': 'infiniti', 'static_path': 'car_cms/manufacturer/foreign_52_infiniti.png'},
    {'code': 'f53', 'name': 'fiat', 'static_path': 'car_cms/manufacturer/foreign_53_fiat.png'},
    {'code': 'f54', 'name': 'astonmartin', 'static_path': 'car_cms/manufacturer/foreign_54_astonmartin.png'},
]


class ManufacturerChoices(models.TextChoices):
    L01 = 'l01', '현대'
    L02 = 'l02', '기아'
    L03 = 'l03', '제네시스'
    L04 = 'l04', '르노'
    L05 = 'l05', '쉐보레'
    L06 = 'l06', '쌍용'
    F01 = 'f01', '벤츠'
    F02 = 'f02', 'BMW'
    F03 = 'f03', '아우디'
    F04 = 'f04', '폭스바겐'
    F05 = 'f05', '볼보'
    F06 = 'f06', '미니'
    F07 = 'f07', '렉서스'
    F08 = 'f08', '포르쉐'
    F09 = 'f09', '혼다'
    F10 = 'f10', '도요타'
    F11 = 'f11', 'Jeep'
    F12 = 'f12', '포드'
    F13 = 'f13', '랜드로버'
    F14 = 'f14', '링컨'
    F15 = 'f15', '푸조'
    F16 = 'f16', '캐딜락'
    F16b = 'f16b', '테슬라'
    F17 = 'f17', '마세라티'
    F18 = 'f18', '벤틀리'
    F19 = 'f19', '람보르기니'
    F20 = 'f20', '시트로엥'
    F21 = 'f21', 'DS'
    F22 = 'f22', '재규어'
    F23 = 'f23', '롤스로이스'
    F51 = 'f51', '마이바흐'
    F52 = 'f52', '인피니티'
    F53 = 'f53', '피아트'
    F54 = 'f54', '에스턴마틴'


def compare_detail_upload_to(instance, filename):
    extension = filename.split(".")[-1]
    filename = f"{str(uuid.uuid4())}.{extension}"
    return os.path.join(timezone.localdate().strftime("%Y/%m/%d"), filename)


class Compare(DateTimeMixin, UUIDPkMixin, EstimateMixin, models.Model):
    class Meta:
        verbose_name = '02. 견적요청'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    serial = models.CharField(
        max_length=30, null=True, blank=False,
        db_index=True, editable=False, verbose_name='일련번호'
    )
    account = models.ForeignKey(
        'account.User', null=False, blank=False, verbose_name='요청자', on_delete=models.PROTECT
    )
    manager = models.ForeignKey(
        'account.User', null=True, blank=True, verbose_name='담당자', on_delete=models.PROTECT,
        related_name='compare_manager'
    )
    status = models.IntegerField(
        choices=CompareStatus.choices, null=False, blank=False, default=CompareStatus.REQUEST,
        verbose_name='상태'
    )
    reject_reason = models.TextField(null=True, blank=True, verbose_name='견적 실패 사유', help_text='견적 실패시 설계사 화면에 노출됩니다.')
    customer_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='고객명')
    career = models.CharField(
        max_length=30, null=True, blank=True, verbose_name='통신사', choices=PhoneCompanyChoice.choices
    )
    customer_cellphone = models.CharField(max_length=100, null=False, blank=False, verbose_name='고객 연락처')
    customer_type = models.IntegerField(
        choices=CustomerTypeChoices.choices, null=False, blank=False, default=CustomerTypeChoices.PERSONAL,
        verbose_name='고객타입'
    )
    customer_identification = models.CharField(max_length=100, null=False, blank=False, verbose_name='주민/사업자번호')
    ssn = models.CharField(max_length=100, null=True, blank=True, verbose_name='개인사업자 주민번호')
    car_price = models.IntegerField(null=True, blank=True, verbose_name='차량가액')
    channel = models.CharField(choices=ChannelChoices.choices, null=False, blank=False, default=ChannelChoices.DIRECT,
                               max_length=10, verbose_name='채널')
    manufacturer = models.CharField(max_length=5, null=True, blank=True, choices=ManufacturerChoices.choices,
                                    verbose_name='제조사')
    car_name = models.CharField(max_length=300, null=False, blank=False, verbose_name='차량모델')
    car_type = models.IntegerField(
        choices=CarTypeChoices.choices, null=False, blank=False, default=CarTypeChoices.NEW,
        verbose_name='신차구분'
    )
    car_identification = models.CharField(max_length=100, null=True, blank=True, verbose_name='차량/차대번호')
    attach_1 = models.FileField(
        null=True, blank=True, upload_to=compare_attach_upload_to, storage=ProtectedFileStorage(),
        verbose_name='첨부파일 1(견적서)'
    )
    attach_2 = models.FileField(
        null=True, blank=True, upload_to=compare_attach_upload_to, storage=ProtectedFileStorage(),
        verbose_name='첨부파일 2'
    )
    attach_3 = models.FileField(
        null=True, blank=True, upload_to=compare_attach_upload_to, storage=ProtectedFileStorage(),
        verbose_name='첨부파일 3'
    )
    driver_range = models.IntegerField(
        choices=DriverRangeChoices.choices, null=False, blank=False, verbose_name='운전자 한정'
    )
    memo = models.TextField(null=True, blank=True, verbose_name='요청사항')
    request_msg = models.TextField(null=True, blank=True, verbose_name='요청메모')
    deny_msg = models.TextField(null=True, blank=True, verbose_name='거절사유')
    contract_fail_msg = models.TextField(null=True, blank=True, verbose_name='계약 실패 사유')
    fee = models.PositiveIntegerField(null=True, blank=True, verbose_name='발생수수료')
    pay_request = models.BooleanField(default=False, null=False, blank=False, verbose_name='수수료 지급 요청')
    pay_request_at = models.DateTimeField(null=True, blank=True, verbose_name='수수료 지급 요청일')
    is_payed = models.BooleanField(default=False, null=False, blank=False, verbose_name='수수료 지급')
    payed_at = models.DateTimeField(null=True, blank=True, verbose_name='수수료 지급일')
    bank = models.CharField(max_length=300, null=True, blank=True, verbose_name='은행')
    bank_account_no = models.CharField(max_length=300, null=True, blank=True, verbose_name='계좌번호')
    estimate_image = models.ImageField(
        null=True, blank=True, storage=ProtectedFileStorage(), upload_to=compare_detail_upload_to,
        verbose_name='견적서 1 이미지'
    )
    estimate_image_comment = models.CharField(max_length=500, null=True, blank=True, verbose_name='견적서 1 커멘트')
    estimate_image_2 = models.ImageField(
        null=True, blank=True, storage=ProtectedFileStorage(), upload_to=compare_detail_upload_to,
        verbose_name='견적서 이미지'
    )
    estimate_image_2_comment = models.CharField(max_length=500, null=True, blank=True, verbose_name='견적서 2 커멘트')
    estimate_image_3 = models.ImageField(
        null=True, blank=True, storage=ProtectedFileStorage(), upload_to=compare_detail_upload_to,
        verbose_name='견적서 이미지'
    )
    estimate_image_3_comment = models.CharField(max_length=500, null=True, blank=True, verbose_name='견적서 3 커멘트')
    danal_auth = models.ForeignKey(DanalAuth, null=True, blank=True, verbose_name='본인인증', on_delete=models.PROTECT)

    @property
    def auth_url(self):
        url = reverse('car_cms_app:customer_auth', args=[self.id])
        return urllib.parse.urljoin(settings.BASE_URL, url)

    def send_auth_message(self):
        from car_cms.models import Message
        body = f"""안녕하세요 {self.customer_name} 고객님, 차다이렉트입니다.
{self.account.name}님께서 요청하신 자동차보험 설계 진행을 위해 문자 드립니다.

인증링크를 통해 서비스약관 및 개인정보처리 약관에 동의해주시면 자동차보험 설계가 진행됩니다.

인증링크 : {self.auth_url}

문의사항은 차다이렉트 고객센터(1544-7653)로 문의 부탁드립니다.

감사합니다.
"""
        message = Message.objects.create(
            receiver=self.customer_cellphone,
            msg=body, msg_type="LMS", title="자동차보험 설계 안내"
        )
        message.send()

    def request_pay(self):
        if self.status != CompareStatus.CONTRACT_SUCCESS:
            raise CarCMSCompareError(11, **{"status_display": self.get_status_display()})
        if self.pay_request is True:
            raise CarCMSCompareError(12)
        if self.account.has_account is False:
            raise CarCMSCompareError(13)
        self.pay_request = True
        self.pay_request_at = timezone.now()
        self.bank = self.account.bank
        self.bank_account_no = self.account.bank_account_no
        self.save()

    def _get_serial(self):
        now = timezone.localdate().strftime('%Y%m%d')
        serial_key = f"camcompare-{now}"
        with transaction.atomic():
            _seq = str(get_next_value(serial_key))
        return f"{now}-{_seq.zfill(3)}"

    def save(self, *args, **kwargs):
        if self.serial is None:
            self.serial = self._get_serial()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.serial

    def start_calculation(self, user, reset=False):
        # 견적 산출 시작 => 견적 산출중
        # if all([self.status != CompareStatus.REQUEST, reset is False]):
        #     raise CarCMSCompareError(2, **{"user": self.manager})
        if all([self.status not in [
            CompareStatus.REQUEST, CompareStatus.CALCULATE, CompareStatus.CALCULATE_COMPLETE, CompareStatus.CONTRACT
        ], reset is True]):
            raise CarCMSCompareError(3, **{"status_display": self.get_status_display()})
        self.manager = user
        self.status = CompareStatus.CALCULATE
        self.save()

    def _complete_calculate(self, user):
        # 견적 완료 상태로 변경
        messages = self.validate_calculate_complete(user)
        if len(messages) == 0:
            self.status = CompareStatus.CALCULATE_COMPLETE
            self.save()
            self.send_complete_calculate()
            return True
        else:
            raise Exception(f"{', '.join(messages)}를 확인하세요")

    def send_complete_calculate(self):
        from car_cms.models import Message
        body = f"""차다이렉트 안내
안녕하세요 {self.account.name}님, 차다이렉트입니다.
요청하신 {self.customer_name} 님의 자동차보험 견적 산출이 완료되었습니다.
차다이렉트 앱에서 상세 내용을 확인하세요."""
        message = Message.objects.create(
            receiver=self.account.cellphone,
            msg=body, msg_type="LMS", title="차다이렉트 안내"
        )
        message.send()

    def _deny_calculate(self, user):
        # 견적 완료 상태로 변경
        if self.reject_reason in [None, ""]:
            raise Exception('견적산출 실패사유를 입력하세요')
        if self.status != CompareStatus.CALCULATE:
            raise Exception('견적요청 상태의 건만 거절 가능합니다.')
        self.status = CompareStatus.CALCULATE_DENY
        self.manager = user
        self.save()
        from car_cms.models import Message
        body = f"""차다이렉트 안내
안녕하세요 {self.account.name}님, 차다이렉트입니다.
요청하신 {self.customer_name} 님의 자동차보험 견적 산출은 진행이 불가능합니다.

불가사유 : {self.reject_reason}

차다이렉트 앱에서 상세 내용을 확인하세요."""
        message = Message.objects.create(
            receiver=self.account.cellphone,
            msg=body, msg_type="LMS", title="차다이렉트 안내"
        )
        message.send()

    def deny_estimate(self, user, msg=None):
        # 견적서 거절
        if self.status != CompareStatus.CALCULATE_COMPLETE:
            raise CarCMSCompareError(7, **{"status_display": self.get_status_display()})
        self.deny_msg = msg
        self.manager = user
        self.status = CompareStatus.DENY
        self.save()

    def start_contract(self, user, memo=None):
        # 계약 요청에 따라 계약중 상태로 변경
        if self.status != CompareStatus.CALCULATE_COMPLETE:
            raise CarCMSCompareError(8, **{"status_display": self.get_status_display()})
        self.status = CompareStatus.CONTRACT
        self.manger = user
        self.memo = memo
        self.save()

    def success_contract(self, user):
        # 체결
        if self.status != CompareStatus.CONTRACT:
            raise CarCMSCompareError(9, **{"status_display": self.get_status_display()})
        messages = self.validate_success()
        if len(messages) != 0:
            raise Exception(f"{', '.join(messages)}를 확인하세요")
        self.status = CompareStatus.CONTRACT_SUCCESS
        self.manager = user
        self.save()
        self.send_success_contract()

    def revoke_success_contract(self):
        # 체결 취소
        if self.status != CompareStatus.CONTRACT_SUCCESS:
            raise CarCMSCompareError(9, **{"status_display": self.get_status_display()})
        self.status = CompareStatus.CONTRACT
        self.save()

    def send_success_contract(self):
        from car_cms.models import Message
        body = f"""차다이렉트 안내
안녕하세요 {self.account.name}님, 차다이렉트입니다.
요청하신 {self.customer_name} 님의 자동차보험 계약 체결이 완료되었습니다.
차다이렉트 앱에서 상세 내용을 확인하세요."""
        message = Message.objects.create(
            receiver=self.account.cellphone,
            msg=body, msg_type="LMS", title="차다이렉트 안내"
        )
        message.send()

    def fail_contract(self, user, msg=None):
        if self.status != CompareStatus.CONTRACT:
            raise CarCMSCompareError(9, **{"status_display": self.get_status_display()})
        self.status = CompareStatus.CONTRACT_FAIL
        self.contract_fail_msg = msg
        self.manager = user
        self.save()
        self.send_fail_contract()

    def send_fail_contract(self):
        from car_cms.models import Message
        body = f"""차다이렉트 안내
안녕하세요 {self.account.name}님, 차다이렉트입니다.
요청하신 {self.customer_name} 님의 자동차보험 계약 체결이 실패했습니다.
차다이렉트 앱에서 상세 내용을 확인하세요."""
        message = Message.objects.create(
            receiver=self.account.cellphone,
            msg=body, msg_type="LMS", title="차다이렉트 안내"
        )
        message.send()


class ComparePending(Compare):
    class Meta:
        verbose_name = '01. 인증대기건'
        verbose_name_plural = verbose_name
        proxy = True


class CompareAll(Compare):
    class Meta:
        verbose_name = '전체 견적요청'
        verbose_name_plural = verbose_name
        proxy = True
#
# m_dat = [
#     {'code': 'l01', 'name': 'hyundai', 'static_path': 'car_cms/manufacturer/local_01_hyundai.png'},
#     {'code': 'l02', 'name': 'kia', 'static_path': 'car_cms/manufacturer/local_02_kia.png'},
#     {'code': 'l03', 'name': 'genesis', 'static_path': 'car_cms/manufacturer/local_03_genesis.png'},
#     {'code': 'l04', 'name': 'renault', 'static_path': 'car_cms/manufacturer/local_04_renault.png'},
#     {'code': 'l05', 'name': 'chevrolet', 'static_path': 'car_cms/manufacturer/local_05_chevrolet.png'},
#     {'code': 'l06', 'name': 'ssangyong', 'static_path': 'car_cms/manufacturer/local_06_ssangyong.png'},
#     {'code': 'f01', 'name': 'benz', 'static_path': 'car_cms/manufacturer/foreign_01_benz.png'},
#     {'code': 'f02', 'name': 'bmw', 'static_path': 'car_cms/manufacturer/foreign_02_bmw.png'},
#     {'code': 'f03', 'name': 'audi', 'static_path': 'car_cms/manufacturer/foreign_03_audi.png'},
#     {'code': 'f04', 'name': 'volkswagen', 'static_path': 'car_cms/manufacturer/foreign_04_volkswagen.png'},
#     {'code': 'f05', 'name': 'volvo', 'static_path': 'car_cms/manufacturer/foreign_05_volvo.png'},
#     {'code': 'f06', 'name': 'mini', 'static_path': 'car_cms/manufacturer/foreign_06_mini.png'},
#     {'code': 'f07', 'name': 'lexus', 'static_path': 'car_cms/manufacturer/foreign_07_lexus.png'},
#     {'code': 'f08', 'name': 'porsche', 'static_path': 'car_cms/manufacturer/foreign_08_porsche.png'},
#     {'code': 'f09', 'name': 'honda', 'static_path': 'car_cms/manufacturer/foreign_09_honda.png'},
#     {'code': 'f10', 'name': 'toyota', 'static_path': 'car_cms/manufacturer/foreign_10_toyota.png'},
#     {'code': 'f11', 'name': 'jeep', 'static_path': 'car_cms/manufacturer/foreign_11_jeep.png'},
#     {'code': 'f12', 'name': 'ford', 'static_path': 'car_cms/manufacturer/foreign_12_ford.png'},
#     {'code': 'f13', 'name': 'landrover', 'static_path': 'car_cms/manufacturer/foreign_13_landrover.png'},
#     {'code': 'f14', 'name': 'lincoln', 'static_path': 'car_cms/manufacturer/foreign_14_lincoln.png'},
#     {'code': 'f15', 'name': 'peugeot', 'static_path': 'car_cms/manufacturer/foreign_15_peugeot.png'},
#     {'code': 'f16', 'name': 'cadillac', 'static_path': 'car_cms/manufacturer/foreign_16_cadillac.png'},
#     {'code': 'f16b', 'name': 'tesla', 'static_path': 'car_cms/manufacturer/foreign_16b_tesla.png'},
#     {'code': 'f17', 'name': 'maserati', 'static_path': 'car_cms/manufacturer/foreign_17_maserati.png'},
#     {'code': 'f18', 'name'적: 'bentley', 'static_path': 'car_cms/manufacturer/foreign_18_bentley.png'},
#     {'code': 'f19', 'name': 'lamborghini', 'static_path': 'car_cms/manufacturer/foreign_19_lamborghini.png'},
#     {'code': 'f20', 'name': 'citroen', 'static_path': 'car_cms/manufacturer/foreign_20_citroen.png'},
#     {'code': 'f21', 'name': 'ds', 'static_path': 'car_cms/manufacturer/foreign_21_ds.png'},
#     {'code': 'f22', 'name': 'jaguar', 'static_path': 'car_cms/manufacturer/foreign_22_jaguar.png'},
#     {'code': 'f23', 'name': 'rollsroyce', 'static_path': 'car_cms/manufacturer/foreign_23_rollsroyce.png'},
#     {'code': 'f51', 'name': 'Maybach', 'static_path': 'car_cms/manufacturer/foreign_51_Maybach.png'},
#     {'code': 'f52', 'name': 'infiniti', 'static_path': 'car_cms/manufacturer/foreign_52_infiniti.png'},
#     {'code': 'f53', 'name': 'fiat', 'static_path': 'car_cms/manufacturer/foreign_53_fiat.png'},
#     {'code': 'f54', 'name': 'astonmartin', 'static_path': 'car_cms/manufacturer/foreign_54_astonmartin.png'},
# ]
#
# for index, m in enumerate(m_dat):
#     span = f"<img src='{}'>"
