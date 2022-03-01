class CarCMSCompareError(Exception):
    def get_error(self):
        code = self.code
        kwargs = self.kwargs
        if code == 0:
            return "올바르지 않은 요청입니다."
        elif code == 1:
            return "존재하지 않는 요청입니다."
        elif code == 2:
            return f"이미 {kwargs.get('user').__str__()}담당자가 배정되어 있습니다."
        elif code == 3:
            return f"담당자 재배정이 불가능한 상태 [{kwargs.get('status_display')}] 입니다."
        elif code == 4:
            return f"배정이 불가능한 건입니다."
        elif code == 5:
            return f"견적 등록이 불가능한 상태 [{kwargs.get('status_display')}] 입니다."
        elif code == 6:
            return "견적사가 등록되지 않았습니다."
        elif code == 7:
            return f"견적 거절이 불가능한 상태 [{kwargs.get('status_display')}] 입니다."
        elif code == 8:
            return f"계약 요청이 불가능한 상태 [{kwargs.get('status_display')}] 입니다."
        elif code == 9:
            return f"계약 등록이 불가능한 상태 [{kwargs.get('status_display')}] 입니다."
        elif code == 10:
            return f"존재하지 않는 견적 상세"
        elif code == 11:
            return f"출금 요청이 불가능한 상태 [{kwargs.get('status_display')}] 입니다."
        elif code == 12:
            return f"이미 출금 요청된 건입니다."
        elif code == 13:
            return f"출금 계좌가 등록되지 않았습니다."

    def __init__(self, code, **kwargs):
        self.code = int(code)
        self.kwargs = kwargs
        self.msg = self.get_error()

    def __str__(self):
        return self.msg
