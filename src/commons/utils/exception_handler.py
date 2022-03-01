from rest_framework.views import exception_handler


def custom_exception_handler(exec, context):
    response = exception_handler(exec, context)

    if response is not None:
        response.data['code'] = response.status_code
        response.data['data'] = None
        response.data['error'] = response
    return response
