from carcompare.models import *

data = {
    "name": "홍찬의",
    "ssn_prefix": "860906",
    "ssn_suffix": "1020710",
    "phone_company": "01",
    "phone1": "010",
    "phone2": "2484",
    "phone3": "6313"
}


self = Compare.object.create_compare(
    name=data.get('name'),
    ssn_prefix=data.get('ssn_prefix'),
    ssn_suffix=data.get('ssn_suffix'),
    phone_company=data.get('phone_company'),
    phone1=data.get('phone1'),
    phone2=data.get('phone2'),
    phone3=data.get('phone3'),
)

response = self.check_auth_no('003611')