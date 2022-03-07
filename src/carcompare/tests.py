from carcompare.models import *

# data = {
#     "name": "홍찬의",
#     "ssn_prefix": "860906",
#     "ssn_suffix": "1020710",
#     "phone_company": "01",
#     "phone1": "010",
#     "phone2": "2484",
#     "phone3": "6313"
# }
#
#
# self = Compare.object.create_compare(
#     name=data.get('name'),
#     ssn_prefix=data.get('ssn_prefix'),
#     ssn_suffix=data.get('ssn_suffix'),
#     phone_company=data.get('phone_company'),
#     phone1=data.get('phone1'),
#     phone2=data.get('phone2'),
#     phone3=data.get('phone3'),
# )

# response = self.check_auth_no('003611')
#
compare_id = "c96c6505-52e0-40b8-9918-6c10c10794e4"

compare = Compare.object.get(id=compare_id)

auth_no = "588019"
car_no = "18더2227"

temp_data = {
    'session_id': str(compare.session_id), 'auth_number': auth_no, 'car_no': car_no, 'start_date': '2022-03-08',
    'manufacturer': '현대',
    'car_name': '쏘나타', 'car_register_year': '2011', 'detail_car_name': 'YF쏘나타2.0',
    'detail_option': '5인승 Y20 럭셔리,오토,에어컨,P/S,ABS,AIR-D,IM(가솔린)', 'treaty_range': '피보험자1인', 'driver_year': '1981',
    'driver_month': '02', 'driver_day': '13', 'driver2_year': '1981', 'driver2_month': '02', 'driver2_day': '13',
    'coverage_bil': '가입', 'coverage_pdl': '2억원', 'coverage_mp_list': '자동차상해', 'coverage_mp': '1억원/3천만원',
    'coverage_umbi': '가입(2억원)', 'coverage_cac': '가입', 'treaty_ers': '가입', 'treaty_charge': '50만원', 'discount_bb': 'YES',
    'discount_bb_year': '2022', 'discount_bb_month': '01', 'discount_bb_price': '10', 'discount_mileage': 'NO',
    'discount_dist': '', 'discount_child': 'NO', 'fetus': '', 'discount_child_year': '12만원 이상',
    'discount_child_month': '',
    'discount_child_day': '', 'discount_pubtrans': 'NO', 'discount_pubtrans_cost': '', 'discount_safedriving': 'NO',
    'discount_safedriving_score': '', 'discount_safedriving_h': 'NO', 'discount_safedriving_score_h': '',
    'discount_email': 'NO', 'discount_poverty': 'NO', 'discount_premileage': 'NO', 'discount_premileage_average': '',
    'discount_premileage_immediate': '', 'discount_and': 'NO', 'discount_adas': 'NO', 'discount_fca': 'NO'
}

response = requests.post(
    url="https://its-api.net/api/result-list/",
    # url="https://its-api.net/api/recall-result/",
    data=temp_data,
    headers={
        "content-type": "application/x-www-form-urlencoded",
    }
)

status_code = response.status_code

print(status_code)
print(response.content)

result_list = {
    'message': 'Success',
    'data': [
        {'insu_name': '흥국화재해상보험', 'expect_cost': '609,330', 'applied_expect_cost': '609,330',
         'dc_list': [{'dcName': '블랙박스 할인'}]},
        {'insu_name': '메리츠화재해상보험', 'expect_cost': '672,390', 'applied_expect_cost': '672,390',
         'dc_list': [{'dcName': '블랙박스 할인'}]},
        {'insu_name': '삼성화재해상보험', 'expect_cost': '681,620', 'applied_expect_cost': '681,620', 'dc_list': []},
        {'insu_name': '하나손해보험', 'expect_cost': '709,320', 'applied_expect_cost': '709,320',
         'dc_list': [{'dcName': '블랙박스 할인'}]},
        {'insu_name': '현대해상화재보험', 'expect_cost': '711,820', 'applied_expect_cost': '711,820',
         'dc_list': [{'dcName': '블랙박스 할인'}]},
        {'insu_name': 'MG손해보험', 'expect_cost': '718,720', 'applied_expect_cost': '718,720',
         'dc_list': [{'dcName': '블랙박스 할인'}]},
        {'insu_name': 'DB손해보험', 'expect_cost': '719,680', 'applied_expect_cost': '719,680', 'dc_list': []},
        {'insu_name': '한화손해보험', 'expect_cost': '795,920', 'applied_expect_cost': '795,920',
         'dc_list': [{'dcName': '블랙박스 할인'}]},
        {'insu_name': '롯데손해보험', 'expect_cost': '824,560', 'applied_expect_cost': '824,560', 'dc_list': []},
        {'insu_name': 'AXA손해보험', 'expect_cost': '866,630', 'applied_expect_cost': '866,630',
         'dc_list': [{'dcName': '블랙박스 할인'}]},
        {'insu_name': '캐롯손해보험', 'expect_cost': '914,640', 'applied_expect_cost': '914,640', 'dc_list': []}
    ], 'sms': {}, 'data2': []
}
