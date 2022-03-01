import random
import uuid
from django.core.exceptions import ValidationError

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,
    PermissionsMixin)
from rest_framework_api_key.models import AbstractAPIKey


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name
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
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return "{}({})".format(self.name, self.email)

    @property
    def is_staff(self):
        return self.is_admin


class APIKey(AbstractAPIKey):
    pass


class ItechsPermission(models.Model):
    user = models.OneToOneField(User, null=False, blank=False, verbose_name='사용자', on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name='활성사용자')
    cp_inspection = models.BooleanField(default=False, blank=False, null=False, verbose_name='휴대폰 검수')
    cp_inspection_admin = models.BooleanField(default=False, blank=False, null=False, verbose_name='휴대폰 검수 관리자')
    cp_inspection_summary = models.BooleanField(default=False, blank=False, null=False, verbose_name='휴대폰 검수 요약')

    def clean(self):
        if any([self.user.is_admin is True, self.user.is_superuser is True]) is False:
            raise ValidationError('관리자 권한이 있는 사용자만 권한을 부여할 수 있습니다.')


class Affiliate(models.Model):
    class Meta:
        verbose_name = '제휴사'
        verbose_name_plural = verbose_name

    id = models.UUIDField(
        default=uuid.uuid4, null=False, blank=False,
        primary_key=True, db_index=True, unique=True,
        editable=False
    )

    registered_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    name = models.CharField(
        max_length=300,
        null=False,
        blank=False,
        unique=True,
        verbose_name='제휴사명'
    )
    api_key = models.OneToOneField(
        APIKey,
        null=False,
        blank=False,
        verbose_name='API 키',
        on_delete=models.PROTECT
    )
    active = models.BooleanField(
        default=True, null=False, blank=False,
        verbose_name='유효'
    )
    use_cp_inspection = models.BooleanField(
        default=False, null=False, blank=False,
        verbose_name='휴대전화 검수'
    )
    use_infotech_find_ins = models.BooleanField(
        default=False, null=False, blank=False,
        verbose_name='인포텍 내보험 찾아줌'
    )
    use_infotech_lookup_ins = models.BooleanField(
        default=False, null=False, blank=False,
        verbose_name='인포텍 내보험 다보여'
    )
    use_pm_insurance = models.BooleanField(
        default=False, null=False, blank=False,
        verbose_name='모빌리티보험 권한'
    )

    @classmethod
    def create(cls, name, active=True):
        u = uuid.uuid4().hex
        api_key, key = APIKey.objects.create_key(name=f"{name}_{u}")
        affiliate = cls.objects.create(name=name, active=active, api_key=api_key)
        return affiliate

    def __str__(self):
        return self.name

    def reset_api_key(self):
        u = uuid.uuid4().hex
        api_key, key = APIKey.objects.create_key(name=f"{self.name}_{u}")
        self.api_key = api_key
        self.save()
        return key


class AffiliateFkMixin(models.Model):
    class Meta:
        abstract = True

    affiliate = models.ForeignKey(
        Affiliate, null=False, blank=False, verbose_name='제휴사', on_delete=models.PROTECT
    )


class AffiliateO2OMixin(models.Model):
    class Meta:
        abstract = True

    affiliate = models.OneToOneField(
        Affiliate, null=False, blank=False, verbose_name='제휴사', on_delete=models.PROTECT
    )
