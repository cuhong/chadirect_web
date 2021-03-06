from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from inline_actions.admin import InlineActionsModelAdminMixin

from car_cms.admin.inline_mixin import CustomInlineActionsModelAdminMixin
from car_cms.models import Compare, CompareStatus, ComparePending, CompareAll
from payment.models import DanalAuthStatusChoice

User = get_user_model()


@admin.register(CompareAll)
class CompareAllAdmin(CustomInlineActionsModelAdminMixin, admin.ModelAdmin):
    list_display = [
        'serial', 'account', 'customer_name', 'customer_cellphone', 'insurer', 'premium', 'status'
    ]
    list_filter = ['insurer', 'status']
    search_fields = ['serial__icontains', 'customer_name__icontains', 'customer_cellphone__icontains']

    def get_queryset(self, request):
        return super(CompareAllAdmin, self).get_queryset(request).exclude(
            danal_auth__status=DanalAuthStatusChoice.READY)


@admin.register(ComparePending)
class ComparePendingAdmin(CustomInlineActionsModelAdminMixin, admin.ModelAdmin):
    list_display = [
        'serial', 'account', 'customer_name', 'customer_cellphone', 'driver_range', 'status', '_auth_status'
    ]
    list_filter = ['status']
    search_fields = [
        'customer_name__icontains', 'customer_cellphone__icontains', 'account__name__icontains',
        'car_identification__icontains'
    ]
    autocomplete_fields = ['account']

    def get_queryset(self, request):
        qs = super(ComparePendingAdmin, self).get_queryset(request).exclude(danal_auth=None).filter(
            danal_auth__status=DanalAuthStatusChoice.READY
        )
        return qs

    def get_inline_actions(self, request, obj=None):
        actions = super(ComparePendingAdmin, self).get_inline_actions(request, obj)
        if obj:
            if obj.danal_auth.status != DanalAuthStatusChoice.COMPLETE:
                actions.append('_send_auth_sms')
        return actions

    def save_model(self, request, obj, form, change):
        super(ComparePendingAdmin, self).save_model(request, obj, form, change)
        obj.refresh_from_db()
        obj.start_calculation()

    # def response_add(self, request, obj, post_url_continue=None):
    #     super(ComparePendingAdmin, self).response_add(request, obj, post_url_continue=post_url_continue)

    def get_fieldsets(self, request, obj=None):
        if obj:
            fieldsets = (
                ('????????????', {
                    'fields': ('status', 'id', 'serial', 'registered_at', 'updated_at')
                }),
                ('????????????', {
                    'fields': (
                        'account', 'status', 'channel', 'customer_name', 'career', 'customer_cellphone',
                        'customer_type',
                        'customer_identification', 'ssn', 'min_age', 'min_age_birthdate', 'car_name', 'car_type',
                        'car_identification', 'car_price',
                        'attach_1', 'attach_2', 'attach_3', 'driver_range', 'memo'
                    )
                }),
            )
        else:
            fieldsets = (
                ('????????????', {
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
                'id', 'registered_at', 'updated_at', 'serial', 'account', 'status', 'channel',
                'customer_name', 'career', 'status',
                'customer_cellphone', 'customer_type', 'customer_identification', 'ssn', 'car_name', 'car_type',
                'car_identification', 'attach_1', 'attach_2', 'attach_3', 'driver_range', 'memo'
                                                                                          'request_msg', 'deny_msg',
                'contract_fail_msg'
            ]

        else:
            rf = []
        return rf

    def _send_auth_sms(self, request, obj, parent_obj=None):
        try:
            obj.send_auth_message()
        except Exception as e:
            messages.error(request, f'????????? ?????? : {str(e)}')
        else:
            messages.success(request, '???????????? ???????????????.')

    _send_auth_sms.short_description = '???????????? ?????????'

    def _auth_status(self, obj):
        if obj.danal_auth is None:
            html = "<span>?????????</san>"
        else:
            # READY = 'ready', '??????'
            # COMPLETE = 'complete', '??????'
            if obj.danal_auth.status == DanalAuthStatusChoice.READY:
                html = "<span style='color:red'>????????????</san>"
            else:
                html = "<span style='color:blue'>????????????</san>"
        return mark_safe(html)

    _auth_status.short_description = '??????'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Compare)
class CompareAdmin(CustomInlineActionsModelAdminMixin, admin.ModelAdmin):
    list_display = [
        'serial', 'account', 'customer_name', 'customer_cellphone', 'driver_range', '_status_display',
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
                'id', 'registered_at', 'updated_at', 'serial', 'account', 'display', 'customer_name',
                'career', 'status',
                'customer_cellphone', 'customer_type', 'customer_identification', 'ssn', 'car_name', 'car_type',
                'car_identification', 'attach_1', 'attach_2', 'attach_3', 'driver_range', 'memo',
                'request_msg', 'deny_msg', 'contract_fail_msg'
            ]
            if obj.status != 1:
                estimate = [
                    'insured_name', 'birthdate', 'car_no', 'vin', 'car_name_fixed',
                    'start_at', 'driver_range_fixed', 'min_age', 'min_age_birthdate',
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
                ('????????????', {
                    'fields': ('status', 'id', 'serial', 'registered_at', 'updated_at')
                }),
                ('????????????', {
                    'fields': (
                        'account', 'status', 'customer_name', 'career', 'customer_cellphone',
                        'customer_type',
                        'customer_identification', 'car_price', 'ssn', 'car_name', 'car_type', 'car_identification',
                        'attach_1', 'attach_2', 'attach_3', 'driver_range', 'memo'
                    )
                }),
                ('??????', {
                    'fields': (
                        ('estimate_image', 'estimate_image_comment'),
                        ('estimate_image_2', 'estimate_image_2_comment'),
                        ('estimate_image_3', 'estimate_image_3_comment'),
                        ('insured_name', 'birthdate'), ('car_no', 'vin', 'car_name_fixed'),
                        ('start_at', 'driver_range_fixed', 'min_age', 'min_age_birthdate',),
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
                ('????????????', {
                    'fields': (
                        ('insurer', 'premium', 'policy_no'), 'fee', 'policy_image',
                        'contract_memo', 'request_msg', 'deny_msg', 'contract_fail_msg'
                    )
                }),
            )
        else:
            fieldsets = (
                ('????????????', {
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


    def get_inline_actions(self, request, obj=None):
        actions = super(CompareAdmin, self).get_inline_actions(request, obj)
        if obj:
            if obj.status == CompareStatus.REQUEST:
                actions.append('_start_calculation')
            if obj.status == CompareStatus.CALCULATE:
                actions.append('_complete_calculate')
                actions.append('_deny_calculate')
            if obj.status == CompareStatus.CALCULATE_COMPLETE:
                actions.append('_start_contract')
                actions.append('_deny_estimate')
            if obj.status == CompareStatus.CONTRACT:
                actions.append('_success_contract')
                actions.append('_fail_contract')
            if obj.status == CompareStatus.CONTRACT_SUCCESS:
                actions.append('_revoke_success_contract')
            # if obj.status in [CompareStatus.CALCULATE_COMPLETE, CompareStatus.DENY, CompareStatus.CONTRACT,
            #                   CompareStatus.CONTRACT_FAIL, CompareStatus.CONTRACT_SUCCESS]:
            #     actions.append('show_estimate')
        return actions

    def _start_calculation(self, request, obj, parent_obj=None):
        try:
            obj.start_calculation(request.user)
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '?????? ??????????????? ?????? ???????????????.')
            url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
            return HttpResponseRedirect(url)

    def _complete_calculate(self, request, obj, parent_obj=None):
        result = obj._complete_calculate(request.user)
        # try:
        #     result = obj._complete_calculate()
        # except Exception as e:
        #     messages.error(request, str(e))
        # else:
        #     messages.success(request, '???????????? ?????? ???????????????.')

    def _deny_calculate(self, request, obj, parent_obj=None):
        try:
            result = obj._deny_calculate(request.user)
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '???????????? ?????? ?????? ???????????????.')

    def _deny_estimate(self, request, obj, parent_obj=None):
        try:
            obj.deny_estimate(request.user)
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '???????????? ?????? ???????????????.')

    def _start_contract(self, request, obj, parent_obj=None):
        try:
            obj.start_contract(request.user)
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '????????? ?????? ???????????????.')

    def _success_contract(self, request, obj, parent_obj=None):
        try:
            obj.success_contract(user=request.user)
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '?????? ?????? ???????????????.')

    def _fail_contract(self, request, obj, parent_obj=None):
        try:
            obj.fail_contract(request.user)
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '?????? ?????? ?????? ???????????????.')

    def _revoke_success_contract(self, request, obj, parent_obj=None):
        try:
            result = obj.revoke_success_contract()
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.success(request, '?????? ?????? ?????? ???????????????.')

    def _status_display(self, obj):
        if obj.status == 4:
            font_size = "14px"
            color = "red"
            weight = "bold"
        elif obj.status == 0:
            font_size = "16px"
            color = "blue"
            weight = "bold"
        else:
            font_size = "14px"
            color = "black"
            weight = "normal"
        html = f"<span style='color: {color}; font-weight: {weight}; font-size: {font_size}'>{obj.get_status_display()}</span>"
        return mark_safe(html)

    _start_calculation.short_description = '????????????'
    _status_display.short_description = '??????'
    _complete_calculate.short_description = '????????????'
    _deny_estimate.short_description = '??????'
    _start_contract.short_description = '?????? ??????'
    _success_contract.short_description = '??????'
    _fail_contract.short_description = '?????? ??????'
    _deny_calculate.short_description = '???????????? ??????'
    _revoke_success_contract.short_description = '?????? ??????'
    # show_estimate.short_description = '???????????????'
