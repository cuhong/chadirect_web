import requests
from django.db import models

class Message(models.Model):
    class Meta:
        verbose_name = '메시지'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    MSG_TYPE_CHOICES = (('SMS', '단문'), ('LMS', '장문'), ('MMS', '그림문자'), ('KKO', '알림톡'))
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일시')
    sender = models.CharField(max_length=30, null=False, blank=False, verbose_name='발신번호', default='15447653')
    receiver = models.CharField(max_length=30, null=False, blank=False, verbose_name='수신번호')
    msg = models.TextField(null=False, blank=False, verbose_name='본문')
    msg_type = models.CharField(max_length=3, choices=MSG_TYPE_CHOICES, null=False, blank=False, verbose_name='구분')
    title = models.CharField(max_length=500, null=True, blank=True, verbose_name='제목(LMS)')
    return_data = models.JSONField(null=True, blank=True, verbose_name='전송상세')
    result = models.BooleanField(default=None, null=True, blank=True, verbose_name='결과')
    # # 카카오톡 only 필드
    # tpl_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='템플릿코드')
    # receiver_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='수신자 이름')
    # button = models.JSONField(null=True, blank=True, verbose_name='버튼 정보')

    def __str__(self):
        return self.title

    def send(self):
        url = "https://apis.aligo.in/send/"
        data = {
            "key": "cyzy7q5ryu47qha6c7ix5mp44pyaq61l",
            "user_id": "directin",
            "sender": self.sender,
            "receiver": self.receiver,
            "msg": self.msg,
            "msg_type": self.msg_type,
            "title": self.title,
            "testmode_yn": "n"
        }
        response = requests.post(url, data)
        if response.status_code != 200:
            self.result = False

        return_data = response.json()
        self.return_data = return_data
        self.result = return_data['result_code'] == "1"
        self.save()
        return self

        # test = 'y' if self.testmode_yn is True else 'n'
        # if self.msg_type == 'KKO':
        #     url = "https://kakaoapi.aligo.in/akv10/alimtalk/send/"
        #     auth_instance = KakaoAuth.get_solo()
        #     token = auth_instance.get_token()
        #     data = {
        #         "apikey": settings.ALIGO_SMS_KEY,
        #         "userid": settings.ALIGO_SMS_ID,
        #         "token": token,
        #         "senderkey": settings.ALIGO_KAKAO_KEY,
        #         "tpl_code": self.tpl_code,
        #         "sender": self.sender,
        #         "receiver_1": self.receiver,
        #         "recvname_1": self.receiver_name,
        #         "subject_1": self.title[:44],
        #         "message_1": self.msg,
        #         "failover": "Y",
        #         "fsubject_1": self.title,
        #         "fmessage_1": self.msg,
        #         "testmode_yn": test
        #     }
        #     if self.button is not None:
        #         data['button_1'] = json.dumps(self.button)
        # else:
        #     url = "https://apis.aligo.in/send/"
        #     data = {
        #         "key": settings.ALIGO_SMS_KEY,
        #         "user_id": settings.ALIGO_SMS_ID,
        #         "sender": self.sender,
        #         "receiver": self.receiver,
        #         "msg": self.msg,
        #         "msg_type": self.msg_type,
        #         "title": self.title,
        #         "testmode_yn": test
        #     }
        # response = requests.post(url, data)
        # if response.status_code != 200:
        #     self.result = False
        # return_data = response.json()
        # self.return_data = return_data
        # if self.msg_type == 'KKO':
        #     self.result = return_data['code'] == 0
        # else:
        #     self.result = return_data['result_code'] == "1"
        # self.save()
        # return self