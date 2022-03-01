import uuid

from django.utils import timezone


def name_card_upload_to(instance, filename):
    now = timezone.localdate().strftime('%Y/%m/%d')
    file_path = f"file/car_cms/name_card/{now}/{str(instance.id)}/{filename}"
    return file_path


def compare_attach_upload_to(instance, filename):
    now = timezone.localdate().strftime('%Y/%m/%d')
    uid = str(uuid.uuid4())
    only_filename = ".".join(filename.split(".")[:-1])
    extension = filename.split(".")[-1]
    new_filename = f"{only_filename}_{uid}.{extension}"
    file_path = f"file/car_cms/compare/{now}/{str(instance.id)}/{new_filename}"
    return file_path


def compare_estimate_upload_to(instance, filename):
    now = timezone.localdate().strftime('%Y/%m/%d')
    uid = str(uuid.uuid4())
    only_filename = ".".join(filename.split(".")[:-1])
    extension = filename.split(".")[-1]
    new_filename = f"{only_filename}_{uid}.{extension}"
    file_path = f"file/car_cms/compare/{now}/{str(instance.id)}/{new_filename}"
    return file_path