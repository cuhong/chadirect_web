from django.conf import settings
from django.core.files.storage import DefaultStorage
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    querystring_auth = False
    default_acl = 'public-read'
    location = f"{settings.STAGE}/media"


class StaticStorage(S3Boto3Storage):
    querystring_auth = False
    default_acl = 'public-read'
    location = f"{settings.STAGE}/static"


class ProtectedFileStorage(S3Boto3Storage):
    querystring_expire = 15
    querystring_auth = True
    default_acl = 'private'
    location = f"{settings.STAGE}/protected"
