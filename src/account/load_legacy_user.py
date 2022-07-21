# import datetime
# import os.path
# import pickle
# import csv
#
# from django.conf import settings
# from pytz import timezone as tz
#
# from account.models import User
#
# KST = tz('Asia/Seoul')
#
# path = os.path.join(settings.BASE_DIR, 'account', 'legacy_user.csv')
#
# with open(path, 'r') as file:
#     reader = csv.DictReader(file)
#     data_list = [dict(line) for line in reader]
#
# success_list = []
# error_list = []
#
# for data in data_list:
#     try:
#         print(data.get('user__email'))
#         user__registered_at = datetime.datetime.strptime(data['user__registered_at'][:19], "%Y-%m-%d %H:%M:%S")
#         user__last_login = datetime.datetime.strptime(data['user__last_login'][:19], "%Y-%m-%d %H:%M:%S")
#         user = User.objects.get(email=data.get('user__email'))
#         print(user)
#         # print(user_queryset.exists())
#         # if user_queryset.exists() is False:
#         #     print('ne')
#         #     user = User.objects.create_user(
#         #         email=data.get('user__email'),
#         #         name=data.get('user__name'),
#         #         cellphone=None if data.get('cellphone') == '' else data.get('cellphone'),
#         #         password='',
#         #     )
#         # else:
#         #     print('e')
#         #     user = user_queryset.first()
#         user.name_card = None if data.get('name_card') == '' else data.get('name_card')
#         user.referer_code = None if data.get('name_card') == '' else data.get('name_card')
#         user.user_type = None if data.get('user_type') == '' else data.get('user_type')
#         user.cellphone=None if data.get('cellphone') == '' else data.get('cellphone')
#         user.is_admin = data.get('is_admin') == 'True'
#         user.registered_at = KST.localize(user__registered_at)
#         user.last_login = KST.localize(user__last_login)
#         user.password = data.get('user__password')
#         user.bank = None if data.get('bank') == '' else data.get('bank')
#         user.bank_account_no = None if data.get('bank_account_no') == '' else data.get('bank_account_no')
#         user.ssn = None if data.get('ssn') == '' else data.get('ssn')
#         user.real_name = None if data.get('real_name') == '' else data.get('real_name')
#         user.save()
#     except Exception as e:
#         print(e)
#         data['err'] = str(e)
#         error_list.append(data)
#     else:
#         data['user'] = user
#         success_list.append(data)