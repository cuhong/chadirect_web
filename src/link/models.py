import secrets
import urllib.parse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

from car_cms.models import Compare
from commons.models import VehicleInsurerChoices, DateTimeMixin

User = get_user_model()


class ProductChoice(models.TextChoices):
    HANHWA_VHC = 'hanwha_vehicle', '한화손해보험 다이렉트 자동차보험'
    # http://bit.ly/HanHwaDirect
    HANA_VHC = 'hana_vehicle', '하나손해보험 다이렉트 자동차보험'
    # https://www.educar.co.kr/cal/car?sAffiliatedConcernKey=cardirect
    CARROT_VHC = 'carrot_vehicle', '캐롯손해보험 다이렉트 자동차보험'
    # https://carrotins.com/common/url/calculation/car/personal?afccd=PA00040
    HYUNDAI_VHC = 'hyundai_vehicle', '현대해상 다이렉트 자동차보험'
    # https://direct.hi.co.kr/service.do?m=28680681ee&cnc_no=605&media_no=B430&companyId=605
    DB_VHC = 'db_vehicle', 'DB 손해보험 다이렉트 자동차보험'
    # https://www.directdb.co.kr/product/at/pvuatarc/step1/formStepPre.do?partner_code=C315
    KB_VHC = 'kb_vehicle', 'KB 손해보험 다이렉트 자동차보험'
    # https://direct.kbinsure.co.kr/websquare/promotion.jsp?pid=1090049&code=0872&page=step1
#
# data_list = [
#     {"product": "hanwha_vehicle", "url": "http://bit.ly/HanHwaDirect"},
#     {"product": "hana_vehicle", "url": "https://www.educar.co.kr/cal/car?sAffiliatedConcernKey=cardirect"},
#     {"product": "carrot_vehicle", "url": "https://carrotins.com/common/url/calculation/car/personal?afccd=PA00040"},
#     {"product": "hyundai_vehicle", "url": "https://direct.hi.co.kr/service.do?m=28680681ee&cnc_no=605&media_no=B430&companyId=605"},
#     {"product": "db_vehicle", "url": "https://www.directdb.co.kr/product/at/pvuatarc/step1/formStepPre.do?partner_code=C315"},
#     {"product": "kb_vehicle", "url": "https://direct.kbinsure.co.kr/websquare/promotion.jsp?pid=1090049&code=0872&page=step1"},
# ]
#
#
#
# for data in data_list:
#     ProductLink.objects.update_or_create(
#         product=data.get('product'),
#         defaults=dict(
#             pc_url=data.get('url'),
#             mobile_url=data.get('url'),
#         )
#     )

class DeviceChoice(models.TextChoices):
    PC = 'pc', '피씨'
    MOBILE = 'mobile', '모바일'


def generate_short_code():
    return secrets.token_urlsafe(nbytes=8)


class ProductLink(models.Model):
    class Meta:
        verbose_name = '상품'
        verbose_name_plural = verbose_name

    product = models.CharField(
        choices=ProductChoice.choices, max_length=100, null=False, blank=False, verbose_name='보험사',
        unique=True
    )
    pc_url = models.URLField(max_length=2048, null=False, blank=False, verbose_name='PC URL')
    mobile_url = models.URLField(max_length=2048, null=False, blank=False, verbose_name='Mobile URL')

    def __str__(self):
        return self.get_product_display()

    def generate_short_link(self, compare=None, user=None):
        while True:
            short_code = generate_short_code()
            # try:
            base_url = settings.BASE_URL
            uri = reverse('link:shortner', args=[short_code])
            url = urllib.parse.urljoin(base_url, uri)
            short_link_instance = Shortlink.objects.create(
                product=self, short_code=short_code, short_url=url, compare=compare, user=user
            )
            return short_link_instance
            # except:
            #     continue


class Shortlink(DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '단축 링크'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    user = models.ForeignKey(User, null=True, blank=True, verbose_name='사용자', on_delete=models.PROTECT)
    compare = models.ForeignKey(Compare, null=True, blank=True, verbose_name='비교', on_delete=models.PROTECT)
    product = models.ForeignKey(
        ProductLink, null=False, blank=False, verbose_name='상품링크', on_delete=models.PROTECT
    )
    short_code = models.CharField(
        max_length=30, null=False, blank=False, unique=True, db_index=True,
        verbose_name='Short Code', editable=False
    )
    short_url = models.URLField(null=False, blank=False, verbose_name='단축 url', editable=False)
    last_log_at = models.DateTimeField(null=True, blank=True, verbose_name='최종 접속일시', editable=False)

    def __str__(self):
        return self.short_url

    def create_history(self, is_mobile, referer, ip):
        self.last_log_at = timezone.now()
        self.save()
        log_instance = ShortlinkLog.objects.create(
            short_link=self, device=DeviceChoice.MOBILE if is_mobile else DeviceChoice.PC,
            referer=referer, ip=ip
        )
        return getattr(self.product, 'mobile_url' if is_mobile else 'pc_url')

    def send_sms(self, cellphone):
        body = f"""안녕하세요, {self.compare.customer_name} 고객님

{self.compare.account.name} 설계사를 통해 요청하신 [{self.product.get_product_display()}] 가입안내 입니다.

아래 두가지 방법 중 편하신 방법으로 가입을 도와드리겠습니다.

- 전화 02-2275-8027
상담원의 도움을 받아 가입을 진행하고 싶으신 경우
- 링크 {self.short_url}
인터넷으로 직접 가입하시고 싶으신 경우

***보험료는 동일합니다.**

문의사항이 있으신 경우 차다이렉트 고객센터로 문의 부탁드립니다.
고객센터 : 1544-7653
(평일 09시~18시 운영 /12시~1시는 점심시간 입니다)

감사합니다.
"""
        from car_cms.models import Message
        message = Message.objects.create(
            receiver=cellphone,
            msg=body, msg_type="LMS", title="차다이렉트 보험가입 링크"
        )
        message.send()


class ShortlinkLog(models.Model):
    class Meta:
        verbose_name = '단축 링크'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='유입일시')
    short_link = models.ForeignKey(
        Shortlink, null=False, blank=False, verbose_name='단축 링크', on_delete=models.PROTECT
    )
    device = models.CharField(
        choices=DeviceChoice.choices, max_length=10, null=False, blank=False, verbose_name='디바이스'
    )
    referer = models.TextField(null=True, blank=True, verbose_name='유입처')
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
