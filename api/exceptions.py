from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    detail = response.data.get('detail', response.data)
    response.data = {
        'status_code': response.status_code,
        'error': _get_error_label(response.status_code),
        'detail': detail,
    }
    return response


def _get_error_label(status_code):
    if status_code == 400:
        return 'bad_request'
    if status_code == 403:
        return 'forbidden'
    if status_code == 404:
        return 'not_found'
    if status_code == 401:
        return 'unauthorized'
    return 'error'
