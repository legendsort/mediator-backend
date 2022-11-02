import hashlib
import pathlib
from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination
from enum import Enum
from os.path import basename
from django.apps import apps
from djongo import models


from rest_framework.response import Response


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


def exchange_attachment_path(instance, filename):
    return f"upload/exchanges/{hashlib.md5(str(instance.title).encode('utf-8')).hexdigest()}/{hashlib.md5(str(filename).encode('utf-8')).hexdigest()}{pathlib.Path(filename).suffix}"


def upload_file_path(instance, filename):
    return f"upload/{'post' if isinstance(instance.source, apps.get_model('Account.Post')) else 'comment'}/{instance.source.id}/{hashlib.md5(str(filename).encode('utf-8')).hexdigest()}{pathlib.Path(filename).suffix}"


def submit_upload_path(instance, filename):
    return f"upload/submit-papers/{instance.submit.id}/{hashlib.md5(str(filename).encode('utf-8')).hexdigest()}{pathlib.Path(filename).suffix}"


def resource_upload_path(instance, filename):
    return f"upload/resource/{instance.resource.id}/{filename}"


def censor_file_path(instance, filename):
    return f"censorship/{basename(filename)}"


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('current_page', self.request.query_params.get('page', 1)),
            ('results', data),
        ]))

    def get_page_size(self, request):
        if self.page_size_query_param:
            page_size = min(int(request.query_params.get(self.page_size_query_param, self.page_size)),
                            self.max_page_size)
            if page_size > 0:
                return page_size
            elif page_size == 0:
                return None
            else:
                pass
        return self.page_size


class SubmissionStatus:
    NEW_SUBMISSION = 'New Submission'
    START_SUBMISSION = 'Start Submission'



