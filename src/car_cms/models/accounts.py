import base64
import binascii
import hashlib
import hmac
import os
import time
import urllib.parse

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import models
from django.urls import reverse
from django.utils import timezone

from car_cms.exceptions import CarCMSCompanyError
from car_cms.models.upload import name_card_upload_to
from commons.models import DateTimeMixin, UUIDPkMixin
from itechs.storages import ProtectedFileStorage


