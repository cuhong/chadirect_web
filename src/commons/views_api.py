from django.db.models import Q
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import BaseHasAPIKey

from account.models import APIKey, Affiliate
from commons.serializers import AESSerializer
from commons.utils.aes_cipher import AESCipher


class AffiliateHasAPIKey(BaseHasAPIKey):
    model = APIKey

    def has_permission(self, request, view):
        key = self.get_key(request)
        if not key:
            return False
        try:
            api_key = APIKey.objects.get_from_key(key)
            affiliate = Affiliate.objects.get(
                Q(api_key=api_key) &
                Q(active=True)
            )
        except Affiliate.DoesNotExist:
            return False
        else:
            is_valid_key = self.model.objects.is_valid(key)
            return is_valid_key


class AESTestViewView(APIView):
    permission_classes = [AffiliateHasAPIKey]

    def get(self, request):
        key_string = AESCipher.generate_key()
        response_data = {
            "result": True, "data": {
                "key": key_string
            }
        }
        return Response(response_data)

    def post(self, request):
        serializer = AESSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            key = data.get('key')
            iv = data.get('iv', None) if data.get('iv', None) else key[:16]
            cipher = AESCipher(key, iv=iv)
            data_string = data.get('data')
            if data.get('action') == 0:
                # 암호화
                result_string = cipher.encrypt_to_string(data_string)
            else:
                # 복호화
                result_string = cipher.decrypt_to_string(data_string)
            response_data = {
                "result": True, "data": {
                    "key": key,
                    "iv": iv,
                    "request_string": data_string,
                    "result_string": result_string
                }
            }
        except ValidationError as e:
            response_data = {
                "result": False, "errors": serializer.errors, "msg": "잘못된 요청"
            }
        except Exception as e:
            response_data = {
                "result": False, "errors": None, "msg": str(e)
            }
        return Response(response_data)
