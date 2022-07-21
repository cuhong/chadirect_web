from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from link.models import Shortlink


def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    except:
        return None


class ShortLinkView(View):
    def get(self, request, short_code):
        # is_mobile = request.device.get('is_mobile')
        # ip = get_client_ip(request)
        # referer = request.META.get('HTTP_REFERER')
        try:
            short_link_instance = Shortlink.objects.select_related('product').get(short_code=short_code)
            target_url = short_link_instance.create_history(True, None, None)
            return HttpResponseRedirect(target_url)
        except Shortlink.DoesNotExist:
            return HttpResponse(f'{short_code}은 존재하지 않는 단축코드 입니다.', status=404)
        except Exception as e:
            return HttpResponse(f'서버 오류', status=500)
