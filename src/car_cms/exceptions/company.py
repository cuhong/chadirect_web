class CarCMSCompanyError(Exception):
    def get_error(self):
        code = self.code
        kwargs = self.kwargs
        if code == 0:
            return f"사용자 [{kwargs.get('name')}]{kwargs.get('username')}는 비활성화된 계정입니다."
        elif code == 1:
            return f"사용자 [{kwargs.get('name')}]{kwargs.get('username')}는 이미 관리자 권한이 부여되어 있습니다."
        elif code == 2:
            return f"사용자 [{kwargs.get('name')}]{kwargs.get('username')}는 관리자 권한이 없습니다."
        elif code == 3:
            return f"사용자 [{kwargs.get('name')}]{kwargs.get('username')}는 이미 상담자 권한이 부여되어 있습니다."
        elif code == 4:
            return f"사용자 [{kwargs.get('name')}]{kwargs.get('username')}는 상담사 권한이 없습니다."

    def __init__(self, code, **kwargs):
        self.code = int(code)
        self.kwargs = kwargs

    def __str__(self):
        return self.get_error()
