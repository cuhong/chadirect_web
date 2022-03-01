import datetime

from django.utils import timezone


# set_null은 빈 값이 들어올 경우 nuull로 반환하겠다는 의미, False 일 경우 이달의 시작일과 종료일을 반환한다,
def parse_get_date(request, set_null=False):
    start_date = None if request.GET.get('startDate', '') == '' else datetime.datetime.strptime(
        request.GET.get('startDate'), "%Y-%m-%d"
    ).date()
    end_date = None if request.GET.get('endDate', '') == '' else datetime.datetime.strptime(
        request.GET.get('endDate'), "%Y-%m-%d"
    ).date()
    now = timezone.localdate()
    if all([set_null is False, start_date is None]):
        start_date = now.replace(day=1)
    if all([set_null is False, end_date is None]):
        end_date = now
    return start_date, end_date

