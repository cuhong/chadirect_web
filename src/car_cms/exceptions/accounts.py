class CarCMSAccountError(Exception):
    def get_error(self):
        code = self.code
        kwargs = self.kwargs
        if code == 0:
            return f"존재하지 않는 계정입니다."
        elif code == 1:
            return f"비밀번호가 일치하지 않습니다."
        elif code == 2:
            return f"올바르지 않은 로그인 요청입니다."
        elif code == 3:
            return f"사용이 제한된 사용자입니다."
        elif code == 4:
            return f"사용이 제한된 회사 입니다."
        elif code == 5:
            return f"올바르지 않은 회원가입 요청입니다."
        elif code == 6:
            return f"존재하지 않는 회사 입니다."
        elif code == 7:
            return f"사용자명 {self.kwargs.get('username')}은 이미 사용중입니다."

    def __init__(self, code, data=None, **kwargs):
        self.code = int(code)
        self.kwargs = kwargs
        self.msg = self.get_error()
        self.data = data

    def __str__(self):
        return self.msg
