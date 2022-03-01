import hmac

import requests
from django.test import TestCase

# Create your tests here.
import time
import hashlib
import base64

access_key = "xX3Zs5ANDz9EBuZpPsve"
secret_key = "sXzoSJxfzeS9DZqNNsgt1kbDkEkIraPGXHOgdSOt"

sender = "no-reply@directin.co.kr"

now = int(round(time.time() * 1000))

signiture_message = f"POST /api/v1/mails\n{str(now)}\n{access_key}"
signature_hmac = hmac.new(bytes(secret_key, 'utf-8'), msg=bytes(signiture_message, 'utf-8'), digestmod=hashlib.sha256)
signature = base64.b64encode(signature_hmac.digest()).decode()

headers = {
    "content-type": "application/json",
    "x-ncp-apigw-timestamp": str(now),
    "x-ncp-iam-access-key": access_key,
    "x-ncp-apigw-signature-v2": signature,
}


body = {
    "senderAddress": "no_reply@directin.co.kr",
    "senderName": "차다이렉트",
    "title": "${customer_name}님 반갑습니다. ",
    "body": "안녕하세요",
    "recipients": [
        {"address": "hongcoilhouse@gmail.com", "name": None, "type": "R"},
    ],
    "individual": True,
    "advertising": False
}

res = requests.post("https://mail.apigw.ntruss.com/api/v1/mails", json=body, headers=headers)

print(res.json())
