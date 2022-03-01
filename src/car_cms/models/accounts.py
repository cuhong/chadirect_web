import base64
import binascii
import hashlib
import hmac
import os
import time
import urllib.parse

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import models
from django.urls import reverse
from django.utils import timezone

from car_cms.exceptions import CarCMSCompanyError
from car_cms.models.upload import name_card_upload_to
from commons.models import DateTimeMixin, UUIDPkMixin
from itechs.storages import ProtectedFileStorage

User = get_user_model()


class Account(DateTimeMixin, UUIDPkMixin, models.Model):
    # 앱 사용자/회사 사용자 모두 여기서 관리한다.
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    user = models.OneToOneField(User, null=False, blank=False, verbose_name='계정', on_delete=models.PROTECT,
                                related_name='carcrm_user')
    name = models.CharField(max_length=50, null=False, blank=False, verbose_name='이름')
    cellphone = models.CharField(max_length=11, null=False, blank=False, verbose_name='핸드폰')
    name_card = models.ImageField(null=True, blank=True, upload_to=name_card_upload_to, storage=ProtectedFileStorage())
    is_active = models.BooleanField(default=True, null=False, blank=False, verbose_name='활성')
    is_admin = models.BooleanField(default=False, null=False, blank=False, verbose_name='회사 관리자 권한')
    bank = models.CharField(max_length=300, null=True, blank=True, verbose_name='은행')
    bank_account_no = models.CharField(max_length=300, null=True, blank=True, verbose_name='계좌번호')
    real_name = models.CharField(max_length=300, null=True, blank=True, verbose_name='계좌주명')
    ssn = models.CharField(max_length=300, null=True, blank=True, verbose_name='주민번호')
    referer_code = models.CharField(max_length=300, null=True, blank=True, verbose_name='추천인코드')
    user_type = models.CharField(
        choices=[('fc', '설계사'), ('dealer', '딜러')],
        max_length=50, null=True, blank=True, verbose_name='회원타입'
    )

    def __str__(self):
        return self.name

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def check_active_user(self, raise_exception=False):
        if raise_exception is True and self.is_active is False:
            raise CarCMSCompanyError(0, **{"name": self.name, "username": self.user.email})
        return self.is_active

    @property
    def has_account(self):
        return all([self.bank is not None, self.bank_account_no is not None])

    def find_password(self):
        find_password = FindPassword.objects.create(account=self, is_complete=False)
        find_password.send_email()
        return find_password

    #
    # def check_company_permission(self, raise_exception=False):
    #     # 상담 권한이 있는지 확인
    #     self.check_active_user()
    #     is_active_user = self.check_active_user(raise_exception=raise_exception)
    #     if is_active_user is False:
    #         return is_active_user
    #     has_company_permission = any([self.is_company_admin, self.is_company_user])
    #     if has_company_permission is False:
    #         raise CarCMSCompanyError(4, **{"name": self.name, "username": self.user.email})
    #     return has_company_permission


class AccountNullableFKMixin(models.Model):
    class Meta:
        abstract = True

    account = models.ForeignKey(
        'car_cms.Account', null=True, blank=True, verbose_name='사용자', on_delete=models.PROTECT
    )


class AccountFKMixin(models.Model):
    class Meta:
        abstract = True

    account = models.ForeignKey(
        'car_cms.Account', null=False, blank=False, verbose_name='사용자', on_delete=models.PROTECT
    )

class FindPasswordError(Exception):
    def __init__(self, msg):
        self.msg = msg


class FindPassword(DateTimeMixin, UUIDPkMixin, models.Model):
    class Meta:
        verbose_name = '비밀번호 찾기'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    account = models.ForeignKey(Account, null=False, blank=False, on_delete=models.PROTECT, verbose_name='계정')
    is_complete = models.BooleanField(default=False, null=False, blank=False, verbose_name='변경완료')

    def get_url(self, app_type):
        base_url = settings.BASE_URL
        if app_type == "dealer":
            uri = reverse('car_cms_app:password_change', args=[self.id])
        else:
            uri = reverse('car_cms_fc_app:password_change', args=[self.id])
        return urllib.parse.urljoin(base_url, uri)

    @classmethod
    def request_change(cls, account, app_type):
        find_password = cls.objects.create(account=account, is_complete=False)
        find_password.send_email(app_type=app_type)
        return find_password

    def send_email(self, app_type):
        receiver = self.account.user.email
        sender = "no-reply@directin.co.kr"
        access_key = settings.NAVER_ACCESS_KEY
        secret_key = settings.NAVER_SECRET_KEY
        now = int(round(time.time() * 1000))
        signiture_message = f"POST /api/v1/mails\n{str(now)}\n{access_key}"
        signature_hmac = hmac.new(
            bytes(secret_key, 'utf-8'), msg=bytes(signiture_message, 'utf-8'), digestmod=hashlib.sha256
        )
        signature = base64.b64encode(signature_hmac.digest()).decode()
        headers = {
            "content-type": "application/json",
            "x-ncp-apigw-timestamp": str(now),
            "x-ncp-iam-access-key": access_key,
            "x-ncp-apigw-signature-v2": signature,
        }
        url = self.get_url(app_type)
        body = {
            "senderAddress": sender,
            "senderName": "차다이렉트",
            "title": f"[차다이렉트]{self.account.user.name}님의 비밀번호 초기화 링크를 보내드립니다.",
            "body": f"안녕하세요 {self.account.user.name}님\n차다이렉트 앱 비밀번호 초기화 링크를 보내드립니다. 아래 링크에서 비밀번호를 변경해주세요.\n\n{str(url)}",
            "recipients": [
                {"address": receiver, "name": self.account.user.name, "type": "R"},
            ],
            "individual": True,
            "advertising": False
        }
        res = requests.post("https://mail.apigw.ntruss.com/api/v1/mails", json=body, headers=headers)


    def change_password(self, password):
        self.check_valid()
        user = self.account.user
        user.set_password(password)
        user.save()
        self.is_complete = True
        self.save()

    def check_valid(self):
        if self.is_complete is True:
            raise FindPasswordError('이미 비밀번호가 변경되었습니다.')
        if timezone.now() >= self.registered_at + relativedelta(minutes=30):
            raise FindPasswordError('유효기간이 만료되었습니다.')


