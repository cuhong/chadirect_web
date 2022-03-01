from django.conf import settings
from popbill import AccountCheckService, PopbillException

BANK_CODE_CHOICES = (
    ("0002", "산업은행"), ("0011", "농협은행"), ("0027", "한국씨티은행"), ("0035", "제주은행"), ("0048", "신협"),
    ("0057", "JP모간체이스은행"), ("0064", "산림조합"), ("0088", "신한은행"), ("0003", "기업은행"),
    ("0012", "지역농축협"), ("0031", "대구은행"), ("0037", "전북은행"), ("0050", "저축은행"), ("0060", "BOA은행"),
    ("0067", "중국건설은행"), ("0089", "케이뱅크"), ("0004", "국민은행"), ("0020", "우리은행"), ("0032", "부산은행"),
    ("0039", "경남은행"), ("0054", "HSBC은행"), ("0061", "BNP파리바은행"), ("0071", "우체국"), ("0090", "카카오뱅크"),
    ("0007", "수협중앙회"), ("0023", "SC은행"), ("0034", "광주은행"), ("0045", "새마을금고연합회"),
    ("0055", "도이치은행"), ("0062", "중국공상은행"), ("0081", "하나은행"), ("0209", "유안타증권"),
    ("0240", "삼성증권"), ("0262", "하이투자증권"), ("0266", "SK증권"), ("0278", "신한금융투자"), ("0290", "부국증권"),
    ("0218", "KB증권"), ("0243", "한국투자증권"), ("0263", "현대차증권"), ("0267", "대신증권"), ("0279", "DB금융투자"),
    ("0291", "신영증권"), ("0227", "KTB투자증권"), ("0247", "NH투자증권"), ("0264", "키움증권"),
    ("0269", "한화투자증권"), ("0280", "유진투자증권"), ("0292", "케이프투자증권"), ("0238", "미래에셋대우"),
    ("0261", "교보증권"), ("0265", "이베스트투자증권"), ("0270", "하나금융투자"), ("0287", "메리츠종합금융증권"),
    ("0294", "펀드온라인코리아"),
)

class PopbillAccountCheck(object):
    def __init__(
            self,
            link_id=settings.POPBILL['link_id'],
            secret_key=settings.POPBILL['secret_key'],
            brn=settings.POPBILL['brn'],
            corp_id=settings.POPBILL['corp_id'],
            is_test=settings.POPBILL['is_test']
    ):
        self.link_id = link_id
        self.secret_key = secret_key
        self.brn = brn
        self.corp_id = corp_id
        self.is_test = is_test
        self.service = None

    def auth(self):
        import ssl
        try:
            _create_unverified_https_context = ssl._create_unverified_context
            ssl._create_default_https_context = _create_unverified_https_context
        except:
            pass
        self.service = AccountCheckService(self.link_id, self.secret_key)
        self.service.ISTest = self.is_test
        self.service.IPRestrictOnOff = False
        self.service.UseStaticIP = False
        return self.service

    def get_balance(self):
        if self.service is None:
            self.auth()
        balance = self.service.getPartnerBalance(self.brn)
        self.service = None
        return int(balance)

    def get_partner_url(self):
        if self.service is None:
            self.auth()
        url = self.service.getPartnerURL(self.brn, 'CHRG')
        self.service = None
        return url

    def check_account(self, bank_code, account_no):
        if self.service is None:
            self.auth()
        try:
            result = self.service.checkAccountInfo(self.brn, bank_code, account_no, self.corp_id)
        except PopbillException as e:
            data = {
                "result": False,
                "code": e.code,
                "msg": e.message
            }
        else:
            data = {
                "result": True if result.resultCode == "0000" else False,
                "code": result.resultCode,
                "msg": result.resultMessage,
                "account_name": None if result.accountName == '' else result.accountName
            }
        self.service = None
        return data