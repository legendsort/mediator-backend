import hashlib
import pathlib


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
