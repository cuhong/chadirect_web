import uuid
from django.db import models, transaction
from django.utils import timezone
from encrypted_fields.fields import EncryptedCharField, EncryptedEmailField, EncryptedDateField
from sequences import get_next_value

from itechs.storages import ProtectedFileStorage



class VehicleInsurerChoices(models.TextChoices):
    MERITZ = 'meritz', '메리츠화재'
    HANHWA = 'hanwha', '한화손해보험'
    LOTTE = 'lotte', '롯데손해보험'
    MG = 'mg', 'MG손해보험'
    HEUNGKUK = 'heungkuk', '흥국화재'
    SAMSUNG = 'samsung', '삼성화재'
    HYUNDAI = 'hyundai', '현대해상'
    KB = 'kb', 'KB 손해보험'
    DB = 'db', 'DB 손해보험'
    CARROT = 'carrot', '캐롯 손해보험'
    AXA = 'axa', 'AXA 손해보험'
    HANA = 'hana', '하나 손해보험'
    ETC = 'etc', '기타/미분류'


class SerialMixin(models.Model):
    class Meta:
        abstract = True

    SERIAL_PREFIX = None
    SERIAL_LENGTH = 10

    serial = models.CharField(max_length=100, null=True, blank=True, verbose_name='일련번호', editable=False)

    @classmethod
    def _get_serial(cls):
        with transaction.atomic():
            _sequence = get_next_value(f"{cls._meta.app_label}__{cls._meta.model_name}")
            sequence = f"{cls.SERIAL_PREFIX}-{str(_sequence).zfill(10)}" if cls.SERIAL_PREFIX else {
                str(_sequence).zfill(10)}
        return sequence

    @transaction.atomic
    def set_serial(self):
        if self.serial:
            raise Exception('이미 시리얼이 부여되었습니다.')
        self.serial = self._get_serial()
        self.save()
        return self.serial

    @classmethod
    def populate_serial(cls):
        with transaction.atomic():
            instance_list = cls.objects.select_for_update().filter(serial=None)
            for instance in instance_list:
                instance.set_serial()


class UUIDPkMixin(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(
        default=uuid.uuid4, null=False, blank=False,
        primary_key=True, db_index=True, unique=True,
        editable=False
    )


class DateTimeMixin(models.Model):
    class Meta:
        abstract = True

    registered_at = models.DateTimeField(
        auto_now_add=True, verbose_name='등록일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )


class Address(models.Model):
    class Meta:
        verbose_name = '주소'
        verbose_name_plural = verbose_name

    postcode = models.CharField(max_length=6, null=False, blank=False, verbose_name='우편번호')
    address = models.TextField(null=False, blank=False, verbose_name='주소')
    address_detail = models.TextField(null=False, blank=False, verbose_name='주소상세')


class ProtectedFileAbstract(UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '보안파일'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)
        abstract = True

    UPLOAD_PREFIX = None

    def upload_to(self, filename):
        now = timezone.now().date().strftime('%Y/%m/%d')
        uid = uuid.uuid4().hex
        file_path = f"{self.UPLOAD_PREFIX}/file/{now}/{uid}/{filename}" if self.UPLOAD_PREFIX else f"file/{now}/{uid}/{filename}"
        return file_path

    file = models.FileField(
        null=False, blank=False, verbose_name='파일', upload_to=upload_to, storage=ProtectedFileStorage()
    )


class ProtectedImageAbstract(UUIDPkMixin, models.Model):
    class Meta:
        verbose_name = '보안이미지'
        verbose_name_plural = verbose_name
        abstract = True

    UPLOAD_PREFIX = None

    def upload_to(self, filename):
        now = timezone.now().date().strftime('%Y/%m/%d')
        uid = uuid.uuid4().hex
        file_path = f"{self.UPLOAD_PREFIX}/file/{now}/{uid}/{filename}" if self.UPLOAD_PREFIX else f"file/{now}/{uid}/{filename}"
        return file_path

    image = models.ImageField(
        null=False, blank=False, verbose_name='파일', upload_to=upload_to, storage=ProtectedFileStorage(),
    )


class BankAccount(UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '계좌'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    BANK_CODE_CHOICES = (
        ("0002", "산업은행"), ("0011", "농협은행"), ("0027", "한국씨티은행"), ("0035", "제주은행"), ("0048", "신협"),
        ("0057", "JP모간체이스은행"), ("0064", "산림조합"), ("0088", "신한은행"), ("0003", "기업은행"),
        ("0012", "지역농축협"), ("0031", "대구은행"), ("0037", "전북은행"), ("0050", "저축은행"), ("0060", "BOA은행"),
        ("0067", "중국건설은행"), ("0089", "케이뱅크"), ("0004", "국민은행"), ("0020", "우리은행"), ("0032", "부산은행"),
        ("0039", "경남은행"), ("0054", "HSBC은행"), ("0061", "BNP파리바은행"), ("0071", "우체국"), ("0090", "카카오뱅크"),
        ("0007", "수협중앙회"), ("0023", "SC은행"), ("0034", "광주은행"), ("0045", "새마을금고연합회"),
        ("0055", "도이치은행"), ("0062", "중국공상은행"), ("0081", "하나은행"), ("0209", "유안타증권"),
        ("0240", "삼성증권"), ("0262", "하이투자증권"), ("0266", "SK증권"), ("0278", "신한금융투자"), ("0290", "부국증권"),
        ("0218", "KB증권"), ("0243", "한국투자증권"), ("0263", "현대차증권"), ("0267", "대신증권"), ("0279", "DB금융투자"),
        ("0291", "신영증권"), ("0227", "KTB투자증권"), ("0247", "NH투자증권"), ("0264", "키움증권"),
        ("0269", "한화투자증권"), ("0280", "유진투자증권"), ("0292", "케이프투자증권"), ("0238", "미래에셋대우"),
        ("0261", "교보증권"), ("0265", "이베스트투자증권"), ("0270", "하나금융투자"), ("0287", "메리츠종합금융증권"),
        ("0294", "펀드온라인코리아"),
    )

    # base_affiliate = models.ForeignKey(BaseAffiliate, null=False, blank=False, verbose_name='제휴사',
    #                                    on_delete=models.PROTECT)
    bank_code = models.CharField(choices=BANK_CODE_CHOICES, max_length=4, null=False, blank=False,
                                 verbose_name='은행/증권사')
    account_no = models.CharField(max_length=30, null=False, blank=False, verbose_name='계좌번호')
    account_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='예금주명')
    ssn = EncryptedCharField(max_length=13, null=True, blank=True, verbose_name='주민번호')
    checked = models.BooleanField(default=None, null=True, blank=True, verbose_name='확인결과')
    result_code = models.CharField(max_length=50, null=True, blank=True, verbose_name='코드')
    result_msg = models.TextField(null=True, blank=True, verbose_name='메시지')
    check_datetime = models.DateTimeField(null=True, blank=True, verbose_name='확인일시')

    def __str__(self):
        return f"{self.get_bank_code_display()}/{self.account_no}/{self.account_name}"



class LocationMixin(models.Model):
    class Meta:
        abstract = True

    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='위도')
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='경도')
