from django.contrib import admin

from carcompare.models import Compare, LegacyContract, CarNo, CompareDetail, CompareDetailEstimate
from import_export.admin import ExportMixin


class ContractInlineAdmin(admin.TabularInline):
    model = LegacyContract
    readonly_fields = ['company_name', 'car_no', 'car_name', 'due_date']
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Compare)
class CompareAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['serial', 'name', 'ssn_prefix', 'phone', 'status', 'is_session_active']
    list_filter = ['status', 'is_session_active']
    search_fields = ['name__icontains', 'ssn_prefix__icontains', 'car_name__icontains']
    inlines = [ContractInlineAdmin]
    readonly_fields = ['serial', 'registered_at']
    fieldsets = (
        ('요청 정보', {
            'fields': (('serial', 'user'), ('registered_at', 'session_id'))
        }),
        ('고객 정보', {
            'fields': (
                'name', 'ssn_prefix', ('phone_company', 'phone1', 'phone2', 'phone3'),
            )
        }),
        ('상태 정보', {
            'fields': (('status', 'is_session_active'), 'error')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def phone(self, obj):
        return f"{obj.phone1}-{obj.phone2}-{obj.phone3}"

    phone.short_description = '휴대전화'


class CompareDetailEstimateInline(admin.TabularInline):
    model = CompareDetailEstimate
    readonly_fields = ['insurer', 'expect_cost', 'expect_cost_mileage_applied', 'dc_list']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


@admin.register(CompareDetail)
class CompareDetailAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'car_no', 'manufacturer', 'car_name', 'is_success']
    list_filter = ['is_success']
    inlines = [CompareDetailEstimateInline]
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    fieldsets = (
        ('기본 정보', {
            'fields': ('compare', 'is_success', 'error')
        }),
        ('계약 정보', {
            'fields': ('start_date',  'image')
        }),
        ('차량 정보', {
            'fields': (
                'car_no', ('manufacturer', 'car_name'), 'car_register_year', ('detail_car_name', 'detail_option'),
            )
        }),
        ('운전자 정보', {
            'fields': (
                'treaty_range',
                ('driver_year', 'driver_month', 'driver_day'),
                ('driver2_year', 'driver2_month', 'driver2_day'),
            )
        }),
        ('담보 정보', {
            'fields': (
                'coverage_bil',
                'coverage_pdl',
                'coverage_mp_list',
                'coverage_mp',
                'coverage_umbi',
                'coverage_cac',
            )
        }),
        ('특약 정보', {
            'fields': (
                'treaty_ers',
                'treaty_charge',
                ('discount_bb', 'discount_bb_year', 'discount_bb_month', 'discount_bb_price'),
            )
        }),
    )


@admin.register(CarNo)
class CarNoAdmin(admin.ModelAdmin):
    pass


"""
curl 'https://its-api.net/api/result-list/' \
  -H 'authority: its-api.net' \
  -H 'pragma: no-cache' \
  -H 'cache-control: no-cache' \
  -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'content-type: application/x-www-form-urlencoded' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'origin: https://its-api.net' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-dest: empty' \
  -H 'referer: https://its-api.net/' \
  -H 'accept-language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cookie: AWSALB=YEPU0YkhuHaMO62AwiSX46aUAVCzrj4DMGPDIimZzNYyLthl9UhbGMw4F09CF/6NCdeWUrlWRHG8G9T20sklst5w0i4MQOMFhkJKO07cXucZBOKc/gylFGxiuir9; AWSALBCORS=YEPU0YkhuHaMO62AwiSX46aUAVCzrj4DMGPDIimZzNYyLthl9UhbGMw4F09CF/6NCdeWUrlWRHG8G9T20sklst5w0i4MQOMFhkJKO07cXucZBOKc/gylFGxiuir9' \
  --data-raw 'session_id=22b800e0-c2f2-4d98-88f2-ea73362ac894&double=N&auth_number=136558&start_date=2022-03-08&car_no=18더2277&manufacturer=삼성&car_name=QM5&car_register_year=2016&detail_car_name=QM5 2.0 가솔린(2WD)&detail_option=5인승 LE,오토,에어컨,ABS,AIR-D,IM(가솔린)&coverage_pdl=2억원&coverage_bil=가입&coverage_mp=2억원/2천만원&coverage_cac=가입&coverage_umbi=가입(2억원)&treaty_range=부부한정&treaty_charge=200만원&driver_year=1991&driver_month=01&driver_day=01&driver2_year=1991&driver2_month=01&driver2_day=01&treaty_ers=가입&coverage_mp_list=자동차상해&fetus=NO&discount_mileage=YES&discount_bb=YES&discount_poverty=NO&discount_email=YES&discount_premileage=YES&discount_safedriving=YES&discount_safedriving_h=NO&discount_pubtrans=YES&discount_and=NO&discount_adas=NO&discount_fca=NO&discount_child=YES&discount_dist=10,000km&discount_bb_year=2015&discount_bb_month=05&discount_bb_price=10&discount_child_year=2013&discount_child_month=05&discount_child_day=11&discount_pubtrans_cost=12만원 이상&discount_safedriving_score=100&discount_safedriving_h_score=100&discount_premileage_average=24&discount_premileage_immediate=24' \
  --compressed
"""
