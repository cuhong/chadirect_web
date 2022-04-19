import requests
from django.test import TestCase

from payment.models import DanalAuth

self = DanalAuth.objects.create()

self.auth_cp()

print(self.return_url)

form_data = dict(
    TXTYPE="ITEMSEND",
    CPID="B010007424",
    CPPWD="E9ESKD0YOa",
    SERVICE="UAS",
    AUTHTYPE="36",
    TARGETURL=self.return_url,
    CPTITLE=self.return_url,
    ORDERID=str(self.id),
    AGELIMIT="15",
)

url = "https://uas.teledit.com/uas/"

response = requests.post(url, data=form_data)

response_data = {data_list.split("=")[0]: data_list.split("=")[1] for data_list in response.text.split("&")}