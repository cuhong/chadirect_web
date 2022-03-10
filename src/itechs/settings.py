import importlib
import os
from boto3 import Session
from pathlib import Path
import sentry_sdk
from django.core.exceptions import ImproperlyConfigured
from sentry_sdk.integrations.django import DjangoIntegration


def get_env():
    module_name = "itechs.env"
    found = importlib.util.find_spec(module_name)
    if found is False:
        raise ImproperlyConfigured('환경설정 파일이 없습니다.')
    return importlib.import_module(module_name)


env = get_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.SECRET_KEY

DEBUG = env.DEBUG

STAGE = env.STAGE  # local, dev, prod

sentry_sdk.init(
    dsn="https://ea0284cee721405fabde33cf0dbf86de@o193266.ingest.sentry.io/5669492",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    environment=STAGE
)

ALLOWED_HOSTS = env.ALLOWED_HOSTS

CLOUDWATCH_AWS_ID = env.CLOUDWATCH_AWS_ID
CLOUDWATCH_AWS_KEY = env.CLOUDWATCH_AWS_KEY
CLOUDWATCH_AWS_DEFAULT_REGION = 'ap-northeast-2' # Be sure to update with your AWS region
logger_boto3_session = Session(
    aws_access_key_id=CLOUDWATCH_AWS_ID,
    aws_secret_access_key=CLOUDWATCH_AWS_KEY,
    region_name=CLOUDWATCH_AWS_DEFAULT_REGION,
)
LOGGING = {
    'version': 1,
    'diable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt': '%Y/%m/%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'watchtower': {
            'level': 'DEBUG',
            'class': 'watchtower.CloudWatchLogHandler',
            'boto3_session': logger_boto3_session,
            'log_group': 'chadirect',
            'stream_name': STAGE,
            # 'maxBytes': 1024 * 1024 * 10,  # 로그 파일 당 10M 까지
            # 'backupCount': 100,  # 로그 파일을 최대 10개까지 유지
            # 'class': 'logging.FileHandler',
            # 'filename': 'logs/logfile.log',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'default': {
            'level': 'DEBUG',  # 로거의 기본 레벨. 이 레벨이 우선시 된다.
            'handlers': ['watchtower']
        },
    },
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_json_widget',
    'rest_framework',
    'mathfilters',
    'bootstrap_pagination',
    # 'rest_framework_api_key',
    'encrypted_fields',
    'imagekit',
    'inline_actions',
    'django_filters',
    'ckeditor',
    'import_export',
    'simple_history',
    'daterangefilter',
    'sequences.apps.SequencesConfig',
    'commons.apps.CommonsConfig',
    'account.apps.AccountConfig',
    'car_cms.apps.CarCmsConfig',
    'chadirect.apps.ChadirectConfig',
    'carcompare.apps.CarcompareConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ]
    }
}

ROOT_URLCONF = 'itechs.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'itechs.wsgi.application'

DATABASES = env.DATABASES
# CACHES = env.CACHES

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DATE_FORMAT": "%Y-%m-%d"
}

# API Key Authentication
API_KEY_CUSTOM_HEADER = "HTTP_X_ITECHS_API_KEY"

# User Model
AUTH_USER_MODEL = 'account.User'

SESSION_COOKIE_AGE = 999999999999999
# Static and Media
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'templates', 'static')
]

if STAGE == 'local':
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    # Storage
    DEFAULT_FILE_STORAGE = 'itechs.storages.MediaStorage'
    STATICFILES_STORAGE = 'itechs.storages.StaticStorage'
    AWS_ACCESS_KEY_ID = env.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = env.AWS_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME = env.AWS_STORAGE_BUCKET_NAME
    AWS_DEFAULT_ACL = env.AWS_DEFAULT_ACL
    AWS_S3_FILE_OVERWRITE = True
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_S3_REGION_NAME = 'ap-northeast-2'
    AWS_S3_SIGNATURE_VERSION = 's3v4'

# Encrypted Field
FIELD_ENCRYPTION_KEYS = env.FIELD_ENCRYPTION_KEYS
FIELD_ENCRYPTION_HASH_KEYS = env.FIELD_ENCRYPTION_HASH_KEYS

#
USE_X_FORWARDED_HOST = True

# 암호화 키
AES_KEY = env.AES_KEY

LOGIN_URL = '/dashboard/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'


SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD = True

if STAGE == 'prod':
    BASE_URL = 'https://mobilityn.net/'
elif STAGE == 'dev':
    BASE_URL = 'https://dev.mobilityn.net/'
elif STAGE == 'local':
    BASE_URL = 'http://127.0.0.1:8000/'

SLACK_WEBHOOK_URL = env.SLACK_WEBHOOK_URL

CELERY_TIMEZONE = "Asia/Seoul"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = env.CELERY_BROKER_URL

NAVER_ACCESS_KEY = "xX3Zs5ANDz9EBuZpPsve"
NAVER_SECRET_KEY = "sXzoSJxfzeS9DZqNNsgt1kbDkEkIraPGXHOgdSOt"