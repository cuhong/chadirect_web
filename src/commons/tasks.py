from celery import shared_task


@shared_task
def add(x, y):
    return x + y


@shared_task
def task_post_jandi(body, url=None):
    import datetime
    import requests
    from django.conf import settings
    headers = {
        "Accept": "application/vnd.tosslab.jandi-v2+json",
        "Content-Type": "application/json"
    }
    body = f"[[바로가기]]({url}) {body}" if url else body
    data = {
        "body": body
    }
    res = requests.post(
        url=settings.JANDI_CP_INSURANCE_URL,
        headers=headers,
        json=data
    )