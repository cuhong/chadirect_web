from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render
from inline_actions.admin import InlineActionsModelAdminMixin

from car_cms.admin.inline_mixin import CustomInlineActionsModelAdminMixin
from car_cms.models import Compare, CompareStatus, ComparePending, CompareAll

User = get_user_model()

@admin.register(CompareAll)
class CompareAllAdmin(CustomInlineActionsModelAdminMixin, admin.ModelAdmin):
    list_display = [
        'serial', 'account', 'manager', 'customer_name', 'customer_cellphone', 'insurer', 'premium', 'status'
    ]
    list_filter = ['manager', 'insurer', 'status']
    search_fields = ['serial__icontains', 'customer_name__icontains', 'customer_cellphone__icontains']
    #
    # def get_inline_actions(self, request, obj=None):
    #     actions = super(CompareAllAdmin, self).get_inline_actions(request, obj)
    #     if obj:
    #         if obj.status in [CompareStatus.CALCULATE_COMPLETE, CompareStatus.DENY, CompareStatus.CONTRACT,
    #                           CompareStatus.CONTRACT_FAIL, CompareStatus.CONTRACT_SUCCESS]:
    #             actions.append('show_estimate')
    #     return actions

    # def show_estimate(self, request, obj, parent_obj=None):
    #     # 1. has the form been submitted?
    #     if '_save' in request.POST:
    #         return None  # return back to list view
    #     # 2. has the back button been pressed?
    #     elif '_back' in request.POST:
    #         return None  # return back to list view
    #     # 3. simply display the form
    #     else:
    #         return render(
    #             request,
    #             'car_cms/admin/estimate_detail_admin.html',
    #             context={'compare': obj}
    #         )
    #
    # show_estimate.short_description = '비교견적서'


@admin.register(ComparePending)
class ComparePendingAdmin(CustomInlineActionsModelAdminMixin, admin.ModelAdmin):
    list_display = [
        'serial', 'account', 'manager', 'customer_name', 'customer_cellphone', 'driver_range', 'status'
    ]
    list_filter = ['status']
    search_fields = [
        'customer_name__icontains', 'customer_cellphone__icontains', 'account__name__icontains',
        'car_identification__icontains'
    ]
    autocomplete_fields = ['account']

    def get_queryset(self, request):
        qs = super(ComparePendingAdmin, self).get_queryset(request)
        return qs.filter(status=CompareStatus.REQUEST, manager=None)

    def get_inline_actions(self, request, obj=None):
        actions = super(ComparePendingAdmin, self).get_inline_actions(request, obj)
        if obj:
            if obj.status == 0 and obj.manager is None:
                actions.append('_set_manager')
        return actions

    def save_model(self, request, obj, form, change):
        super(ComparePendingAdmin, self).save_model(request, obj, form, change)
        obj.refresh_from_db()
        obj.set_manager(request.user)

    # def response_add(self, request, obj, post_url_continue=None):
    #     super(ComparePendingAdmin, self).response_add(request, obj, post_url_continue=post_url_continue)

    def get_fieldsets(self, request, obj=None):
        if obj:
            fieldsets = (
                ('기본정보', {
                    'fields': ('status', 'id', 'serial', 'registered_at', 'updated_at')
                }),
                ('견적요청', {
                    'fields': (
                        'account', 'manager', 'status', 'channel', 'customer_name', 'career', 'customer_cellphone',
                        'customer_type',
                        'customer_identification', 'ssn', 'car_name', 'car_type', 'car_identification', 'car_price',
                        'attach_1', 'attach_2', 'attach_3', 'driver_range', 'memo'
                    )
                }),
            )
        else:
            fieldsets = (
                ('견적요청', {
                    'fields': (
                        'account', 'customer_name', 'channel', 'career', 'customer_cellphone', 'customer_type',
                        'customer_identification', 'ssn', 'car_name', 'car_type', 'car_identification',
                        'attach_1', 'attach_2', 'attach_3', 'driver_range', 'memo'
                    )
                }),
            )
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        if obj:
            rf = [
                'id', 'registered_at', 'updated_at', 'serial', 'account', 'manager', 'status', 'channel',
                'customer_name', 'career',
                'customer_cellphone', 'customer_type', 'customer_identification', 'ssn', 'car_name', 'car_type',
                'car_identification', 'attach_1', 'attach_2', 'attach_3', 'driver_range', 'memo'
                                                                                          'request_msg', 'deny_msg',
                'contract_fail_msg'
            ]

        else:
            rf = []
        return rf

    def _set_manager(self, request, obj, parent_obj=None):
        # 1. has the form been submitted?
        if '_save' in request.POST:
            try:
                manager_id = request.POST.get('user')
                manager = User.objects.get(id=manager_id)
                obj.set_manager(manager=manager)
            except Exception as e:
                print(e)
                messages.error(request, '담당자 배정 실패')
            else:
                messages.success(request, '담당자가 배정되었습니다.')
            return None  # return back to list view
        # 2. has the back button been pressed?
        elif '_back' in request.POST:
            return None
        # 3. simply display the form
        else:
            pass
        chatuser_queryset = User.objects.filter(Q(is_admin=True) | Q(is_superuser=True)).filter(is_active=True)
        return render(
            request,
            'car_cms/admin/set_manager.html',
            context={'chatuser_queryset': chatuser_queryset}
        )

    _set_manager.short_description = '담당자 배정'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Compare)
class CompareAdmin(CustomInlineActionsModelAdminMixin, admin.ModelAdmin):
    list_display = [
        'serial', 'account', 'manager', 'customer_name', 'customer_cellphone', 'driver_range', 'status'
    ]
    list_filter = ['status']
    search_fields = [
        'customer_name__icontains', 'customer_cellphone__icontains', 'account__name__icontains',
        'car_identification__icontains'
    ]
    autocomplete_fields = ['account']
    change_form_template = 'car_cms/admin/change_form_compare.html'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            rf = [
                'id', 'registered_at', 'updated_at', 'serial', 'account', 'manager', 'status', 'customer_name', 'career',
                'customer_cellphone', 'customer_type', 'customer_identification', 'ssn', 'car_name', 'car_type',
                'car_identification', 'attach_1', 'attach_2', 'attach_3', 'driver_range', 'memo',
                'request_msg', 'deny_msg', 'contract_fail_msg'
            ]
            if obj.status != 1:
                estimate = [
                    'insured_name', 'birthdate', 'car_no', 'vin', 'car_name_fixed',
                    'start_at', 'driver_range_fixed', 'min_age',
                    'bi_2', 'self_injury', 'uninsured', 'li', 'self_damage', 'emergency', 'blackbox',
                    'estimate_insurer_1', 'estimate_premium_1', 'estimate_memo_1',
                    'estimate_insurer_2', 'estimate_premium_2', 'estimate_memo_2',
                    'estimate_insurer_3', 'estimate_premium_3', 'estimate_memo_3',
                    'estimate_insurer_4', 'estimate_premium_4', 'estimate_memo_4',
                    'estimate_insurer_5', 'estimate_premium_5', 'estimate_memo_5',
                    'estimate_insurer_6', 'estimate_premium_6', 'estimate_memo_6',
                    'estimate_insurer_7', 'estimate_premium_7', 'estimate_memo_7',
                    'estimate_insurer_8', 'estimate_premium_8', 'estimate_memo_8',
                    'estimate_insurer_9', 'estimate_premium_9', 'estimate_memo_9',
                    'estimate_insurer_10', 'estimate_premium_10', 'estimate_memo_10',
                    'estimate_insurer_11', 'estimate_premium_11', 'estimate_memo_11',
                    'estimate_insurer_12', 'estimate_premium_12', 'estimate_memo_12',
                ]
                rf += estimate
            if obj.status != 4:
                contract = [
                    'insurer', 'premium', 'fee', 'policy_no', 'policy_image', 'contract_memo',
                ]
                rf += contract
        else:
            rf = []
        return rf

    def get_fieldsets(self, request, obj=None):
        if obj:
            fieldsets = (
                ('기본정보', {
                    'fields': ('status', 'id', 'serial', 'registered_at', 'updated_at')
                }),
                ('견적요청', {
                    'fields': (
                        'account', 'manager', 'status', 'customer_name', 'career', 'customer_cellphone', 'customer_type',
                        'customer_identification', 'car_price', 'ssn', 'car_name', 'car_type', 'car_identification',
                        'attach_1', 'attach_2', 'attach_3', 'driver_range', 'memo'
                    )
                }),
                ('설계', {
                    'fields': (
                        'estimate_image',
                        ('insured_name', 'birthdate'), ('car_no', 'vin', 'car_name_fixed'),
                        ('start_at', 'driver_range_fixed', 'min_age'),
                        ('bi_2', 'self_injury', 'uninsured'), ('li', 'self_damage'), ('emergency', 'blackbox'),
                        ('estimate_insurer_1', 'estimate_premium_1', 'estimate_memo_1'),
                        ('estimate_insurer_2', 'estimate_premium_2', 'estimate_memo_2'),
                        ('estimate_insurer_3', 'estimate_premium_3', 'estimate_memo_3'),
                        ('estimate_insurer_4', 'estimate_premium_4', 'estimate_memo_4'),
                        ('estimate_insurer_5', 'estimate_premium_5', 'estimate_memo_5'),
                        ('estimate_insurer_6', 'estimate_premium_6', 'estimate_memo_6'),
                        ('estimate_insurer_7', 'estimate_premium_7', 'estimate_memo_7'),
                        ('estimate_insurer_8', 'estimate_premium_8', 'estimate_memo_8'),
                        ('estimate_insurer_9', 'estimate_premium_9', 'estimate_memo_9'),
                        ('estimate_insurer_10', 'estimate_premium_10', 'estimate_memo_10'),
                        ('estimate_insurer_11', 'estimate_premium_11', 'estimate_memo_11'),
                        ('estimate_insurer_12', 'estimate_premium_12', 'estimate_memo_12'),
                        'reject_reason'
                    )
                }),
                ('체결정보', {
                    'fields': (
                        ('insurer', 'premium', 'policy_no'), 'fee', 'policy_image',
                        'contract_memo', 'request_msg', 'deny_msg', 'contract_fail_msg'
                    )
                }),
            )
        else:
            fieldsets = (
                ('견적요청', {
                    'fields': (
                        'account', 'customer_name', 'customer_cellphone', 'customer_type',
                        'customer_identification', 'ssn', 'car_name', 'car_type', 'car_identification',
                        'attach_1', 'attach_2', 'attach_3', 'driver_range', 'memo'
                    )
                }),
            )
        return fieldsets

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if obj.manager:
            return obj.manager == request.user
        else:
            return False

    def get_queryset(self, request):
        qs = super(CompareAdmin, self).get_queryset(request).filter(manager=request.user)
        return qs

    def get_inline_actions(self, request, obj=None):
        actions = super(CompareAdmin, self).get_inline_actions(request, obj)
        if obj:
            if obj.status == CompareStatus.CALCULATE:
                actions.append('_complete_calculate')
                actions.append('_deny_calculate')
            if obj.status == CompareStatus.CALCULATE_COMPLETE:
                actions.append('_start_contract')
                actions.append('_deny_estimate')
            if obj.status == CompareStatus.CONTRACT:
                actions.append('_success_contract')
                actions.append('_fail_contract')
            # if obj.status in [CompareStatus.CALCULATE_COMPLETE, CompareStatus.DENY, CompareStatus.CONTRACT,
            #                   CompareStatus.CONTRACT_FAIL, CompareStatus.CONTRACT_SUCCESS]:
            #     actions.append('show_estimate')
        return actions
    #
    # def show_estimate(self, request, obj, parent_obj=None):
    #     # 1. has the form been submitted?
    #     if '_save' in request.POST:
    #         return None  # return back to list view
    #     # 2. has the back button been pressed?
    #     elif '_back' in request.POST:
    #         return None  # return back to list view
    #     # 3. simply display the form
    #     else:
    #         return render(
    #             request,
    #             'car_cms/admin/estimate_detail_admin.html',
    #             context={'compare': obj}
    #         )

    def _complete_calculate(self, request, obj, parent_obj=None):
        try:
            result = obj._complete_calculate()
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '견적완료 처리 되었습니다.')

    def _deny_calculate(self, request, obj, parent_obj=None):
        try:
            result = obj._deny_calculate()
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '견적산출 불가 처리 되었습니다.')

    def _deny_estimate(self, request, obj, parent_obj=None):
        try:
            obj.deny_estimate()
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '견적거절 처리 되었습니다.')

    def _start_contract(self, request, obj, parent_obj=None):
        try:
            obj.start_contract()
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '계약중 처리 되었습니다.')

    def _success_contract(self, request, obj, parent_obj=None):
        try:
            obj.success_contract()
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '체결 처리 되었습니다.')

    def _fail_contract(self, request, obj, parent_obj=None):
        try:
            obj.fail_contract()
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '체결 실패 처리 되었습니다.')

    _complete_calculate.short_description = '견적요청'
    _deny_estimate.short_description = '거절'
    _start_contract.short_description = '계약 진행'
    _success_contract.short_description = '체결'
    _fail_contract.short_description = '체결 실패'
    _deny_calculate.short_description = '견적산출 불가'
    # show_estimate.short_description = '비교견적서'
