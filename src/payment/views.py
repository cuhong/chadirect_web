from django import forms
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from payment.exceptions import DanalAuthError
from payment.models import DanalAuth, DanalAuthStatusChoice


class DanalAuthSuccessView(View):
    def get(self, request, danal_auth_id):
        try:
            danal = DanalAuth.objects.get(id=danal_auth_id)
        except Exception as e:
            danal = None
        context = {"danal": danal}
        return render(request, 'new_design/payment/danal_auth/success.html', context=context)


class DanalAuthErrorView(View):
    def get(self, request, danal_auth_id):
        try:
            danal = DanalAuth.objects.get(id=danal_auth_id)
        except Exception as e:
            danal = None
        context = {"danal": danal, "error_msg": "인증 실패"}
        return render(request, 'new_design/payment/danal_auth/error.html', context=context)


class DanalAuthView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DanalAuthView, self).dispatch(request, *args, **kwargs)

    def get(self, request, danal_auth_id):
        try:
            with transaction.atomic():
                danal = DanalAuth.objects.select_for_update().get(id=danal_auth_id)
                if danal.status == DanalAuthStatusChoice.COMPLETE:
                    context = {"error_msg": "이미 인증 되었습니다.", "danal": danal}
                    return render(request, 'new_design/payment/danal_auth/error.html', context=context)
                tid = danal.auth_cp(
                    agree_1=True if request.GET.get('agree1') == "true" else False,
                    agree_2=True if request.GET.get('agree2') == "true" else False,
                    agree_3=True if request.GET.get('agree3') == "true" else False
                )
                context = {"danal": danal}
                return render(request, 'new_design/payment/danal_auth/ready.html', context=context)
        except DanalAuth.DoesNotExist:
            context = {"error_msg": f"존재하지 않는 인증 키: {str(danal_auth_id)}", "danal": None}
            return render(request, 'new_design/payment/danal_auth/error.html', context=context)
        except DanalAuthError as e:
            context = {"error_msg": e.msg, "danal": danal}
            return render(request, 'new_design/payment/danal_auth/error.html', context=context)
        except Exception as e:
            context = {"error_msg": f"기타 오류 : {str(e)}", "danal": None}
            return render(request, 'new_design/payment/danal_auth/error.html', context=context)

    def post(self, request, danal_auth_id):
        sample_response = {
            'TID': '202204192115259989747011',
            'dndata': 'oLS2a4yMw55AQUTUyc91hdou5Zqp1%2B4pxBQ5g3TNyHmG%2BQbXH%2BL%2F3sxEPTWts%2FSFBb1htvvueZZjQErD%2Byol6FKcIUm5PDTsRQkpS4NacQCL5aItVkSbjPYRfLHJd2saleJcpIO5VeZMPm6sY73659tWs3vY6VCqKQi%2FX%2FlPc3df3Qt0xQM3WJ2S1PmJNRjhA8VryLeWlu%2F0MuGRfZa%2B5jOZHRX7Wy3Q1Yz%2FNqbYp1ALnWB3vwOatr1zozcZck02',
            'BackURL': '',
            'IsMobileW': 'N',
            'IsCharSet': 'EUC-KR',
            'IsDstAddr': '01024846313',
            'IsCarrier': '',
            'IsExceptCarrier': '',
        }
        try:
            with transaction.atomic():
                danal = DanalAuth.objects.select_for_update().get(id=danal_auth_id)
                if danal.status == DanalAuthStatusChoice.COMPLETE:
                    context = {"error_msg": "이미 인증 되었습니다.", "danal": danal}
                    return render(request, 'new_design/payment/danal_auth/error.html', context=context)
                tid = request.POST.get('TID')
                if danal.tid != tid:
                    context = {"error_msg": "인증 대사가 일치하지 않습니다.", "danal": danal}
                    return render(request, 'new_design/payment/danal_auth/error.html', context=context)
                danal.confirm_auth()
                if danal.success_url:
                    return HttpResponseRedirect(danal.success_url)
                else:
                    context = {"danal": danal}
                    return render(request, 'new_design/payment/danal_auth/success.html', context=context)
        except DanalAuth.DoesNotExist:
            context = {"error_msg": f"존재하지 않는 인증 키: {str(danal_auth_id)}", "danal": None}
            return render(request, 'new_design/payment/danal_auth/error.html', context=context)
        except DanalAuthError as e:
            context = {"error_msg": e.msg, "danal": danal}
            return render(request, 'new_design/payment/danal_auth/error.html', context=context)
        except Exception as e:
            context = {"error_msg": f"기타 오류 : {str(e)}", "danal": None}
            return render(request, 'new_design/payment/danal_auth/error.html', context=context)