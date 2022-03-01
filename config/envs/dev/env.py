# dev

from pathlib import Path

ENV_DIR = Path(__file__).resolve().parent

SECRET_KEY = "ae8@ivgmcy&&ojb$tmhy%j_#w3ug6h3_!u@pk$m%@jl7h3z&fo"

STAGE = 'dev'

DEBUG = True

ALLOWED_HOSTS = ['dev.itechs.io']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'itechs_core_dev',
        'USER': 'itechs',
        'PASSWORD': 'dkdlxldptm1!',
        'HOST': 'itechs-core.cz11mooapt6e.ap-northeast-2.rds.amazonaws.com',
        'PORT': 5432,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

AWS_STORAGE_BUCKET_NAME = 'itechs-core'
AWS_DEFAULT_ACL = 'public-read'
AWS_ACCESS_KEY_ID = 'AKIAZGI6WZDTLWRP3EPO'
AWS_SECRET_ACCESS_KEY = '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'

AWS_TEXTRACT_ACCESS_KEY_ID = 'AKIAZGI6WZDTLJJZWHVI'
AWS_TEXTRACT_SECRET_ACCESS_KEY = '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'

FIELD_ENCRYPTION_KEYS = [
    "f620f4692aa443e4ca9e3934f3a905f12641564b809e23fa9435bc04064df788"
]

FIELD_ENCRYPTION_HASH_KEYS = 'fbf14d6a7130108be6ef369cd99df9873092c2b7212eb22acea809c466adbb0a'

AES_KEY = b'@\xe4\x0e\x0c\x13z]V5E\x80\xbcu\x1dNy'

OCR_KEY = "dURDTGZmeWF4TG5VRk94aElmc29kdm1yaWpXbUtYa28="
OCR_ENDPOINT = "https://498a2295378e453698c0bd48d013a9c0.apigw.ntruss.com/custom/v1/4922/cbbff0c4d64df80abf1e9827efebb170b715922d8ada552b3cec4a95706d7952/general"

POPBILL = {
    "link_id": "itechs",
    "secret_key": "j7Umkoolg9NcPl9iXlZWhSpSthkf8y8wh5imEqP2cA8=",
    "brn": "7438600950",
    "corp_id": "itechs",
    "is_test": True
}

CLOUDWATCH_AWS_ID = "AKIAZGI6WZDTCBQDBHO6"
CLOUDWATCH_AWS_KEY = "HNlrLYZaWmRE82qowE0fxMYXB73XGFH6z4vfw6Bq"

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

CELERY_BROKER_URL = 'redis://itechs-redis.cjhpy0.0001.apn2.cache.amazonaws.com:6379/0'

JANDI_CP_INSURANCE_URL = "https://wh.jandi.com/connect-api/webhook/23279605/a5f69df1544841f1a152453c927df16b"

NAVER_ACCESS_KEY = "xX3Zs5ANDz9EBuZpPsve"
NAVER_SECRET_KEY = "sXzoSJxfzeS9DZqNNsgt1kbDkEkIraPGXHOgdSOt"