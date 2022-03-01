from django.conf import settings
from django.core.files.storage import DefaultStorage
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorageRemote(S3Boto3Storage):
    querystring_auth = False
    default_acl = 'public-read'
    location = f"{settings.STAGE}/media"


class StaticStorageRemote(S3Boto3Storage):
    querystring_auth = False
    default_acl = 'public-read'
    location = f"{settings.STAGE}/static"


class ProtectedFileStorageRemote(S3Boto3Storage):
    querystring_expire = 15
    querystring_auth = True
    default_acl = 'private'
    location = f"{settings.STAGE}/protected"


class MediaStorageLocal(DefaultStorage):
    location = f"{settings.STAGE}/media"


class StaticStorageLocal(DefaultStorage):
    location = f"{settings.STAGE}/static"


class ProtectedFileStorageLocal(DefaultStorage):
    location = f"{settings.STAGE}/protected"


def MediaStorage():
    if settings.STAGE == 'local':
        return MediaStorageLocal()
    return MediaStorageRemote()


def StaticStorage():
    if settings.STAGE == 'local':
        return StaticStorageLocal()
    return StaticStorageRemote()


def ProtectedFileStorage():
    if settings.STAGE == 'local':
        return ProtectedFileStorageLocal()
    return ProtectedFileStorageRemote()
