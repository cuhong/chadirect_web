import base64
import hashlib
import hmac
import random
import time
import urllib
import uuid

import requests
from ckeditor.fields import RichTextField
from dateutil.relativedelta import relativedelta
from django.conf import settings

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,
    PermissionsMixin)
from django.urls import reverse
from django.utils import timezone

from car_cms.models.upload import name_card_upload_to
from commons.models import DateTimeMixin, UUIDPkMixin
from itechs.storages import ProtectedFileStorage, MediaStorage

DEFAULT_TEL = "1544-7653"

def temp_organization():
    organization_list = [
        "ABL생명",
        "GA코리아주식회사",
        "글로벌금융판매",
        "메가",
        "사랑모아금융서비스",
        "신한금융플러스",
        "에이플러스에셋어드바이저",
        "엠금융서비스",
        "유퍼스트보험마케팅",
        "프라임에셋",
        "한국보험금융",
    ]

    for organization in organization_list:
        org, created = Organization.objects.get_or_create(
            name=organization, defaults={"is_searchable": True}
        )


class UserManager(BaseUserManager):
    def create_user(
            self, email, name, cellphone=None, name_card=None, referer_code=None, user_type=None, password=None,
            organization=None, is_organization_admin=False
    ):
        if all([organization is None, is_organization_admin is True]):
            raise ValueError('관리자 권한을 부여하려는 조직을 지정하세요.')
        if not email:
            raise ValueError('Users must have an email address')
        if organization is not None:
            organization_instance, created = Organization.objects.get_or_create(
                name=organization, defaults={"is_searchable": False}
            )
        else:
            organization_instance = None
        if organization_instance:
            if organization_instance.need_validate is True:
                employee_queryset = organization_instance.organizationemployee_set.filter(
                    name=name, contact="".join([s for s in cellphone if s.isdigit()])
                )
                if employee_queryset.exists() is False:
                    raise Exception(f'해당 조직의 직원으로 등록되지 않았습니다.\n관리자의 확인이 필요합니다.\n문의) {DEFAULT_TEL}')
        user = self.model(
            email=self.normalize_email(email),
            name=name, cellphone=cellphone,
            name_card=name_card, referer_code=referer_code,
            user_type=user_type, organization=organization_instance
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


def small_logo_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    file_path = f"file/car_cms/small_logo/{str(instance.id)}/{str(instance.id)}.{ext}"
    return file_path


def estimate_background_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    file_path = f"file/car_cms/estimate_background/{str(instance.id)}/{str(instance.id)}.{ext}"
    return file_path


def generate_guid():
    u_string = str(uuid.uuid4())
    return u_string.split("-")[0]


class Organization(models.Model):
    class Meta:
        verbose_name = '조직'
        verbose_name_plural = verbose_name
        ordering = ('name',)

    name = models.CharField(
        max_length=200, null=False, blank=False, unique=True, verbose_name='조직명'
    )
    small_logo = models.ImageField(
        null=True, blank=True, verbose_name='로고', upload_to=small_logo_upload_to, storage=MediaStorage()
    )
    estimate_background = models.ImageField(
        null=True, blank=True, verbose_name='견적서 배경', upload_to=estimate_background_upload_to, storage=MediaStorage()
    )
    is_searchable = models.BooleanField(
        default=False, null=False, blank=False, verbose_name='검색 표시'
    )
    guid = models.CharField(max_length=30, null=False, blank=False, default=generate_guid, editable=False)
    service_policy = RichTextField(null=True, blank=True, verbose_name='서비스 이용약관(계약서)')
    privacy_policy = RichTextField(null=True, blank=True, verbose_name='개인정보 처리방침')
    need_validate = models.BooleanField(default=False, null=False, blank=False, verbose_name='조직 사용인 검증')

    def __str__(self):
        return self.name

    @property
    def external_signup_url(self):
        base_url = settings.BASE_URL
        uri = reverse('car_cms_affiliate:signup_external')
        url = urllib.parse.urljoin(base_url, uri)
        url += f"?guid={self.guid}"
        return url


class OrganizationEmployee(models.Model):
    class Meta:
        verbose_name = '조직 사용인'
        verbose_name_plural = verbose_name

    organization = models.ForeignKey(
        Organization, null=False, blank=False, verbose_name='조직', on_delete=models.PROTECT
    )
    dept_1 = models.CharField(max_length=200, null=True, blank=True, verbose_name='부서 1')
    dept_2 = models.CharField(max_length=200, null=True, blank=True, verbose_name='부서 2')
    dept_3 = models.CharField(max_length=200, null=True, blank=True, verbose_name='부서 3')
    dept_4 = models.CharField(max_length=200, null=True, blank=True, verbose_name='부서 4')
    code = models.CharField(max_length=50, null=True, blank=True, verbose_name='사번')
    name = models.CharField(max_length=50, null=False, blank=False, verbose_name='성명')
    role = models.CharField(max_length=100, null=True, blank=True, verbose_name='직책')
    contact = models.CharField(max_length=50, null=False, blank=False, verbose_name='연락처')

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        _contact = "".join([s for s in str(self.contact) if s.isdigit()])
        self.contact = _contact if _contact[0] == "0" else f"0{_contact}"
        super(OrganizationEmployee, self).save(*args, **kwargs)


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
    organization = models.ForeignKey(
        Organization, null=True, blank=True, verbose_name='소속조직', on_delete=models.PROTECT
    )
    is_organization_admin = models.BooleanField(
        default=False, null=False, blank=False, verbose_name='조직 관리자'
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
    employee_no = models.CharField(max_length=100, null=True, blank=True, verbose_name='사번')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        if self.organization:
            return "[{}]{}({})".format(self.organization.name, self.name, self.email)
        else:
            return "{}({})".format(self.name, self.email)

    @property
    def is_staff(self):
        return self.is_admin or self.is_superuser

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
    def request_change(cls, user, app_type):
        find_password = cls.objects.create(account=user, is_complete=False)
        find_password.send_email(app_type=app_type)
        return find_password

    def send_email(self, app_type):
        from car_cms.models import Message
        receiver = self.account.email
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
        body_string = f"안녕하세요 {self.account.name}님\n\n차다이렉트 앱 비밀번호 초기화 링크를 보내드립니다. 아래 링크에서 비밀번호를 변경해주세요.\n\n{str(url)}"
        if self.account.cellphone:
            message = Message.objects.create(
                receiver=self.account.cellphone,
                msg=body_string, msg_type="LMS", title="차다이렉트 비밀번호 변경안내"
            )
            message.send()
        body = {
            "senderAddress": sender,
            "senderName": "차다이렉트",
            "title": f"[차다이렉트]{self.account.name}님의 비밀번호 초기화 링크를 보내드립니다.",
            "body": f"안녕하세요 {self.account.name}님\n차다이렉트 앱 비밀번호 초기화 링크를 보내드립니다. 아래 링크에서 비밀번호를 변경해주세요.\n\n<a href='{str(url)}'>{str(url)}</a>",
            "recipients": [
                {"address": receiver, "name": self.account.name, "type": "R"},
            ],
            "individual": True,
            "advertising": False
        }
        res = requests.post("https://mail.apigw.ntruss.com/api/v1/mails", json=body, headers=headers)

    def change_password(self, password):
        self.check_valid()
        user = self.account
        user.set_password(password)
        user.save()
        self.is_complete = True
        self.save()

    def check_valid(self):
        if self.is_complete is True:
            raise FindPasswordError('이미 비밀번호가 변경되었습니다.')
        if timezone.now() >= self.registered_at + relativedelta(minutes=30):
            raise FindPasswordError('유효기간이 만료되었습니다.')
