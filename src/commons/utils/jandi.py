from commons.tasks import task_post_jandi


def post_jandi(body, url=None):
    try:
        task_post_jandi.delay(body, url=url)
    except:
        pass
