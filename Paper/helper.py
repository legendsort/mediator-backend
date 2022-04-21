import hashlib
import pathlib
from rest_framework.pagination import PageNumberPagination


def filter_params(params, items):
    result = {}
    for item in items:
        if params.get(item):
            result[item] = params.get(item)
    return result


def publisher_logo_path(instance, filename):
    return f"upload/publisher/{hashlib.md5(str(filename).encode('utf-8')).hexdigest()}{pathlib.Path(filename).suffix}"


def journal_resource_path(instance, filename):
    return f"upload/journals/{instance.name}/{hashlib.md5(str(filename).encode('utf-8')).hexdigest()}{pathlib.Path(filename).suffix}"


def submit_upload_path(instance, filename):
    return f"upload/submit-papers/{instance.submit.id}/{hashlib.md5(str(filename).encode('utf-8')).hexdigest()}{pathlib.Path(filename).suffix}"


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
