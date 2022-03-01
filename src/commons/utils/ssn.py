import datetime

from django.utils import timezone


class SsnParser(object):
    def __init__(self, ssn, strict=False):
        self.ssn = "".join([s for s in str(ssn) if s.isdigit()])
        self.prefix = None
        self.suffix = None
        self.birthdate = None
        self.gender = None
        self.strict = strict  # strict 검증(거소번호 무시하고 검증)할지 여부.
        self.validate()

    class ValidationError(Exception):
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return f"주민등록번호 검증 오류 : {self.msg}"

    def _validate_checksum(self):
        total = sum(
            [x * y for x, y in zip([int(s) for s in self.ssn], [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5])]
        )
        validation_no = (11 - total % 11) % 10
        is_valid = str(validation_no) == self.ssn[12]
        if is_valid is False:
            raise self.ValidationError('주민번호 검증번호 불일치')

    def validate(self):
        """
        20120601 이후 외국인 거소신고번호 폐지,.
        """
        # 자릿수 검증
        if len(self.ssn) != 13:
            raise self.ValidationError('주민등록번호는 13자리 숫자입니다.')
        self.gender = 0 if int(self.ssn[6]) % 2 == 1 else 1  # 남성 0 여성 1
        self.prefix = self.ssn[:6]
        self.suffix = self.ssn[6:]
        # 생년월일 검증
        try:
            now = timezone.now().date()
            _birthdate = datetime.datetime.strptime(self.prefix, "%y%m%d").date()
            birthdate = _birthdate.replace(year=_birthdate.year - 100) if _birthdate > now else _birthdate
        except:
            raise self.ValidationError('생년월일을 확인하세요.')
        else:
            self.birthdate = birthdate
        # 형식 검증
        if self.strict is True:
            self._validate_checksum()
        elif self.ssn[12] not in ['7', '8', '9']:
            self._validate_checksum()


    @property
    def masked_ssn(self):
        return f"{self.prefix}{self.suffix[0]}******"
