import requests


class Kakao():
    def __init__(self):
        self.apikey = "cyzy7q5ryu47qha6c7ix5mp44pyaq61l"
        self.userid = "directin"
        self.token = None
        self.urlencode = None

    def auth(self):
        url = "https://kakaoapi.aligo.in/akv10/token/create/30/s/"
        body = dict(
            apikey=self.apikey,
            userid=self.userid
        )
        response = requests.post(url=url, data=body)
        if response.status_code != 200:
            raise Exception('인증실패')
        response_data = response.json()
        if response_data.get('code') != 0:
            raise Exception(response_data.get('message'))
        self.token = response_data.get('token')
        self.urlencode = response_data.get('urlencode')

    def send(self, tpl_code, receiver, subject, message, sender="15447653"):
        self.auth()
        url = "https://kakaoapi.aligo.in/akv10/alimtalk/send/"
        body = dict(
            apikey=self.apikey,
            userid=self.userid,
            token=self.token,
            senderkey="393e80bd336be1ed0e77d6d68539d1ab3d55988e",
            tpl_code=tpl_code,
            sender=sender,
            receiver_1=receiver,
            subject_1=subject,
            message_1=message,
            failover="Y",
            fsubject_1=subject,
            fmessage_1=message,
        )
        # response = requests.post(url, data=body)

kakao = Kakao()

kakao.auth()

tpl_code = "TG_9652"
message = """차다이렉트 for FC

안녕하세요 홍찬의 설계사님 차다이렉트입니다.

요청하신 자동차보험 견적이 견적완료처리 되었습니다.

자세한 ㅁ낭ㄹ

차다이렉트 앱에서 상세 내용을 확인하세요."""

url = "https://kakaoapi.aligo.in/akv10/alimtalk/send/"
body = dict(
    apikey=kakao.apikey,
    userid=kakao.userid,
    token=kakao.token,
    senderkey="393e80bd336be1ed0e77d6d68539d1ab3d55988e",
    tpl_code=tpl_code,
    sender="15447653",
    receiver_1="01024846313",
    subject_1="제목",
    message_1=message,
    failover="Y",
    fsubject_1="제목",
    fmessage_1=message,
)

response = requests.post(url, data=body)

print(response.json())

# message = """차다이렉트 for #{회원구분}
#
# 안녕하세요 #{회원명} #{회원구분}님 차다이렉트입니다.
#
# 요청하신 자동차보험 견적이 #{변경상태}처리 되었습니다.
#
# #{상태변경상세}
#
# 차다이렉트 앱에서 상세 내용을 확인하세요.
# """