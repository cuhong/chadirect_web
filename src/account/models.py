import base64
import hashlib
import hmac
import random
import time
import urllib
import uuid

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,
    PermissionsMixin)
from django.urls import reverse
from django.utils import timezone

from car_cms.models import name_card_upload_to
from commons.models import DateTimeMixin, UUIDPkMixin
from itechs.storages import ProtectedFileStorage


class UserManager(BaseUserManager):
    def create_user(self, email, name, cellphone=None, name_card=None, referer_code=None, user_type=None, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name, cellphone=cellphone,
            name_card=name_card, referer_code=referer_code,
            user_type=user_type
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name
        )
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(PermissionsMixin, AbstractBaseUser):
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    id = models.UUIDField(default=uuid.uuid4, null=False, blank=False, unique=True, primary_key=True, editable=False)
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='가입일자')
    email = models.EmailField(
        verbose_name='이메일',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=50, null=False, blank=False, verbose_name='이름')
    cellphone = models.CharField(max_length=11, null=True, blank=True, verbose_name='핸드폰')
    name_card = models.ImageField(
        null=True, blank=True, upload_to=name_card_upload_to, storage=ProtectedFileStorage(),
        verbose_name='명함'
    )
    is_active = models.BooleanField(default=True, verbose_name='활성')
    is_admin = models.BooleanField(default=False, verbose_name='관리자(상담원)')
    bank = models.CharField(max_length=300, null=True, blank=True, verbose_name='은행')
    bank_account_no = models.CharField(max_length=300, null=True, blank=True, verbose_name='계좌번호')
    real_name = models.CharField(max_length=300, null=True, blank=True, verbose_name='계좌주명')
    ssn = models.CharField(max_length=300, null=True, blank=True, verbose_name='주민번호')
    referer_code = models.CharField(max_length=300, null=True, blank=True, verbose_name='추천인코드')
    user_type = models.CharField(
        choices=[('fc', '설계사'), ('dealer', '딜러')],
        max_length=50, null=True, blank=True, verbose_name='회원타입'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return "{}({})".format(self.name, self.email)

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def has_account(self):
        return all([self.bank is not None, self.bank_account_no is not None])

    def find_password(self):
        find_password = FindPassword.objects.create(account=self, is_complete=False)
        find_password.send_email()
        return find_password


class FindPasswordError(Exception):
    def __init__(self, msg):
        self.msg = msg


class FindPassword(DateTimeMixin, UUIDPkMixin, models.Model):
    class Meta:
        verbose_name = '비밀번호 찾기'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    account = models.ForeignKey(User, null=False, blank=False, on_delete=models.PROTECT, verbose_name='계정')
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
        receiver = self.user.email
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
            "title": f"[차다이렉트]{self.user.name}님의 비밀번호 초기화 링크를 보내드립니다.",
            "body": f"안녕하세요 {self.user.name}님\n차다이렉트 앱 비밀번호 초기화 링크를 보내드립니다. 아래 링크에서 비밀번호를 변경해주세요.\n\n{str(url)}",
            "recipients": [
                {"address": receiver, "name": self.user.name, "type": "R"},
            ],
            "individual": True,
            "advertising": False
        }
        res = requests.post("https://mail.apigw.ntruss.com/api/v1/mails", json=body, headers=headers)

    def change_password(self, password):
        self.check_valid()
        user = self.user
        user.set_password(password)
        user.save()
        self.is_complete = True
        self.save()

    def check_valid(self):
        if self.is_complete is True:
            raise FindPasswordError('이미 비밀번호가 변경되었습니다.')
        if timezone.now() >= self.registered_at + relativedelta(minutes=30):
            raise FindPasswordError('유효기간이 만료되었습니다.')

