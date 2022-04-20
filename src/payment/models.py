import urllib.parse
import uuid

import requests
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from commons.models import DateTimeMixin, UUIDPkMixin
from payment.exceptions import DanalAuthError


class DanalAuthStatusChoice(models.TextChoices):
    READY = 'ready', '준비'
    COMPLETE = 'complete', '완료'


class DanalAuth(DateTimeMixin, UUIDPkMixin, models.Model):
    class Meta:
        verbose_name = '다날 본인인증'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    tid = models.CharField(max_length=40, null=False, blank=False, verbose_name='TID')
    title = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='인증 제목'
    )
    success_url = models.URLField(null=True, blank=True, verbose_name='성공시 URL')
    phone_no = models.CharField(max_length=30, null=True, blank=True, verbose_name='고객전화번호 고정값')
    status = models.CharField(
        max_length=10, choices=DanalAuthStatusChoice.choices, null=False, blank=False, verbose_name='상태',
        default=DanalAuthStatusChoice.READY
    )
    danal_ci = models.TextField(null=True, blank=True, verbose_name='CI')
    danal_di = models.TextField(null=True, blank=True, verbose_name='DI')
    danal_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='확인실명')
    danal_iden = models.CharField(max_length=50, null=True, blank=True, verbose_name='확인생년')
    agree_at = models.DateTimeField(null=True, blank=True, verbose_name='인증성공일시')
    agree_1 = models.BooleanField(default=False, null=False, blank=False, verbose_name='동의 1')
    agree_2 = models.BooleanField(default=False, null=False, blank=False, verbose_name='동의 2')
    agree_3 = models.BooleanField(default=False, null=False, blank=False, verbose_name='동의 3')


    @property
    def return_url(self):
        uri = reverse('payment:danal_auth', args=[str(self.id)])
        return urllib.parse.urljoin(settings.BASE_URL, uri)

    @property
    def auth_success_url(self):
        uri = reverse('payment:danal_auth_success', args=[str(self.id)])
        return urllib.parse.urljoin(settings.BASE_URL, uri)

    @property
    def auth_error_url(self):
        uri = reverse('payment:danal_auth_error', args=[str(self.id)])
        return urllib.parse.urljoin(settings.BASE_URL, uri)

    def auth_cp(self, agree_1=False, agree_2=False, agree_3=False):
        # 01. 가맹점 인증
        form_data = dict(
            TXTYPE="ITEMSEND",
            CPID="B010007424",
            CPPWD="E9ESKD0YOa",
            SERVICE="UAS",
            AUTHTYPE="36",
            TARGETURL=self.return_url,  # 인증 완료 파라메터가 넘어오는 url
            CPTITLE=self.title or '차다이렉트 인증',  # 인증 제목
            ORDERID=str(self.id),
            AGELIMIT="15",
        )
        url = "https://uas.teledit.com/uas/"
        response = requests.post(url, data=form_data)
        if response.status_code == 200:
            response_data = {
                data_list.split("=")[0]: data_list.split("=")[1] for data_list in response.text.split("&")
            }
            if response_data.get('RETURNCODE') == "0000":
                # 성공
                tid = response_data.get('TID')
                self.agree_1 = agree_1
                self.agree_2 = agree_2
                self.agree_3 = agree_3
                self.tid = tid
                self.save()
                return tid
            else:
                # 실패
                raise DanalAuthError(
                    msg=f"다날 응답 오류 : {response_data.get('RETURNCODE')} / {response_data.get('RETURNMSG')}"
                )
        else:
            raise DanalAuthError(msg=f"다날 서버 응답 실패 : status code {response.status_code}")

    def confirm_auth(self):
        # 02. 인증 결과 확인
        form_data = dict(
            TXTYPE="CONFIRM",
            TID=self.tid,
            CONFIRMOPTION="1",
            CPID="B010007424",
            ORDERID=str(self.id)
        )
        url = "https://uas.teledit.com/uas/"
        response = requests.post(url, data=form_data)
        if response.status_code == 200:
            response_data = {
                data_list.split("=")[0]: data_list.split("=")[1] for data_list in response.text.split("&")
                # data_list.split("=")[0]: data_list.split("=")[1] for data_list in response_text.split("&")
            }
            if response_data.get('RETURNCODE') == "0000":
                # 성공
                sample_response = {
                    'RETURNCODE': '0000', 'RETURNMSG': 'No information', 'TID': '202204192144370446356011',
                    'CI': '/qWM2RSH/eDX/pipDTEgiglHuV0MIJ/7cVKST3CFDwI2QFwUzt7wGQxHIRP+wJQSxABedWN8Nk8p+Nnbtm9Gyg',
                    'NAME': '홍찬의', 'ORDERID': '23ce5016-703d-40b8-9bc1-c5500cb622e3',
                    'DI': 'MC0GCCqGSIb3DQIJAyEAz5E0eO3dtXn7nX6tEECJHCdYuKC8zVoE6f/Z9VY6v5o', 'IDEN': '8609061'
                }
                self.danal_ci = response_data.get('CI')
                self.danal_di = response_data.get('DI')
                self.danal_name = response_data.get('NAME')
                self.danal_iden = response_data.get('IDEN')
                self.status = DanalAuthStatusChoice.COMPLETE
                self.agree_at = timezone.now()
                self.save()
            else:
                # 실패
                raise DanalAuthError(
                    msg=f"다날 응답 오류 : {response_data.get('RETURNCODE')} / {response_data.get('RETURNMSG')}"
                )
        else:
            raise DanalAuthError(msg=f"다날 서버 응답 실패 : status code {response.status_code}")


