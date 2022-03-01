import datetime

from django.utils import timezone


class CellphoneParser(object):
    def __init__(self, cellphone):
        self.cellphone = "".join([s for s in str(cellphone) if s.isdigit()])
        self.clean()
        self.validate()

    class ValidationError(Exception):
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return f"휴대전화번호 검증 오류 : {self.msg}"

    def clean(self):
        if self.cellphone[:3] == "821":
            self.cellphone = "0" + self.cellphone[2:]

    def validate(self):
        # 자릿수 검증
        if len(self.cellphone) not in [11, 10]:
            raise self.ValidationError('휴대전화번호는 10 혹은 11자리 숫자 입니다.')
        if self.cellphone[:3] not in ["010", "011", "017", "018", "019"]:
            raise self.ValidationError(f"통신사 식별번호({self.cellphone[:3]}) 불명")
