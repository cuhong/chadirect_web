import csv
from account.models import *

org_id = 11
organization = Organization.objects.get(id=org_id)

path = "/home/ubuntu/chadirect_web/src/account/list.csv"

data_list = []
c = 0
exist_user_list = []
nonexist_user_list = []

with open(path, 'r', encoding='utf-8-sig') as file:
    lines = csv.DictReader(file)
    for line in lines:
        data = dict(line)
        data['contact'] = data.pop('cellphone')
        user_queryset = User.objects.filter(name=data['name'], cellphone=data['contact'])
        if user_queryset.exists():
            user = user_queryset.first()
            user.organization = organization
            user.dept_1 = data['dept_1']
            user.dept_2 = data['dept_2']
            user.role = data['role']
            user.save()
            data['user'] = user
            exist_user_list.append(data)
            c += 1
        else:
            user_temp_queryset = User.objects.values_list('cellphone', flat=True).filter(name=data['name'])
            print(user_temp_queryset.count())
            data['이름이 같은 사람 가입 휴대전화번호'] = "|".join(list(user_temp_queryset))
            print(data)
            nonexist_user_list.append(data)
        # oeq = OrganizationEmployee.objects.filter(**data)
        # if oeq.exists():
        #     data['organization'] = oeq.first()
        #     c += 1
        # else:
        #     data['organization'] = None
        # data_list.append(data)


print(c)
with open("/home/ubuntu/chadirect_web/src/account/list_result.csv", 'w', encoding='utf-8-sig') as file:
    writer = csv.DictWriter(file, fieldnames=nonexist_user_list[0].keys())
    writer.writeheader()
    writer.writerows(nonexist_user_list)