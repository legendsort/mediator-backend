from rest_framework.renderers import JSONRenderer
from rest_framework.utils import json


class JSONResponseRenderer(JSONRenderer):
    media_type = 'application/json'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None, ):
        status_code = renderer_context['response'].status_code if renderer_context else 500
        response_dict = {
            'response_code': True if status_code < 400 else False,
            'data': data,
            'message': 'Successfully fetched!' if status_code < 400 else 'Server has error!',
        }
        data = response_dict
        return json.dumps(data)
