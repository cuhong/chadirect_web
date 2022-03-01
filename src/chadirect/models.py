import datetime

from django.db import models
import requests
# AES 암호화키 (이전 메일과 동일) : dbfire!#dbfire@$dbfire!$chdirect
# 고객정보 레이아웃중 JEHUSA_CD : C5364  으로 보내주시면됩니다
import urllib
from commons.models import DateTimeMixin
from commons.utils.aes_cipher import AESCipher
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class GenderChoices(models.TextChoices):
    MALE = 'male', '남성'
    FEMALE = 'female', '여성'


class DBCustomer(DateTimeMixin, models.Model):
    class Meta:
        verbose_name = 'DB 제휴고객'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)


    registered_at = models.DateTimeField(
        auto_now_add=True, verbose_name='고객등록일시'
    )
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='담당자', editable=False, on_delete=models.PROTECT)
    ssn_prefix = models.CharField(max_length=6, null=False, blank=False, verbose_name='주민번호 앞자리')
    gender = models.CharField(max_length=6, null=False, blank=False, choices=GenderChoices.choices, verbose_name='성별')
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='성명')
    contact = models.CharField(max_length=100, null=False, blank=False, verbose_name='전화번호')
    memo = models.TextField(null=True, blank=True, verbose_name='메모')
    is_db_registered = models.BooleanField(default=False, null=False, blank=False, verbose_name='DB 등록')
    db_registered_at = models.DateTimeField(null=True, blank=True, verbose_name='DB 등록일시')
    error = models.TextField(null=True, blank=True, verbose_name='DB 등록에러')

    @property
    def ssn(self):
        gender_code = "1" if self.gender == GenderChoices.MALE else "2"
        return f"{self.ssn_prefix}{gender_code}000000"

    @property
    def birthdate(self):
        return datetime.datetime.strptime(self.ssn_prefix, "%y%m%d").date()

    def generate_url(self):
        cipher = AESCipher("dbfire!#dbfire@$dbfire!$chdirect")
        query_dict = dict(
            dispatchMethod="insCmCustomer",
            PERSONAL_ID=cipher.encrypt_to_string(self.ssn),
            CSTM_NM_KR=cipher.encrypt_to_string(self.name),
            MOBILE_PHN_NUM=cipher.encrypt_to_string(self.contact),
            INIT_MSG=cipher.encrypt_to_string('운전자보험'),
            JEHUSA_CD="C5364"
        )
        # https://www.promydirect.com/DTAS/action/INTERFACE?dispatchMethod=insCmCustomer&컬럼ID1=암호화된 값&컬럼ID2=암호화된 값&…
        query = urllib.parse.urlencode(query_dict)
        url = f"https://www.promydirect.com/DTAS/action/INTERFACE?{query}"
        return url

    def send_data(self):
        if self.is_db_registered is True:
            raise Exception('이미 전송된 정보입니다.')
        url = self.generate_url()
        response = requests.get(url)
        if response.status_code == 200:
            response_text = response.text  # ERROR_CD:TRUE|MSG:SUCCESS\n
            response_text_list = response_text.split("|")
            if "ERROR_CD:TRUE" in response_text_list:
                result = True
                self.is_db_registered = True
                self.db_registered_at = timezone.now()
                self.error = None
            else:
                result = False
                self.is_db_registered = False
                self.error = response_text
        else:
            result = False
            self.is_db_registered = False
            self.error = f"status code : {response.status_code}"
        self.save()
        return result
