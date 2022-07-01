from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets
from Wipo.service import FTPService
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status

from django.apps import apps

class FTPViewSet(viewsets.ViewSet):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:

            refresh = RefreshToken.for_user(self.request.user)
            service = FTPService(token=str(refresh.access_token))
            response_code, response = service.list(path=request.query_params.get('path', '/'))
            return Response({
                'response_code': response_code,
                'message': response if not response_code else response['message'],
                'data': response['data'] if response_code else []
            })
        except Exception as e:
            print(e)
            return Response({
                'response_code': False,
                'message': 'Server has error',
                'data': []
            })

    @action(detail=False, methods=['post'], url_path='remove')
    def remove(self, request, pk=None):
        try:
            refresh = RefreshToken.for_user(self.request.user)
            service = FTPService(token=str(refresh.access_token))
            response_code, response = service.remove(path=request.data.get('path', None))
            print(request.data)
            return Response({
                'response_code': response_code,
                'message': response if not response_code else response['message'],
                'data': response['data'] if response_code else []
            })
        except Exception as e:
            print('remove exception', e)
            return Response({
                'response_code': False,
                'message': 'Server has error',
                'data': []
            })

    @action(detail=False, methods=['post'], url_path='rename')
    def rename(self, request, pk=None):
        try:
            refresh = RefreshToken.for_user(self.request.user)
            service = FTPService(token=str(refresh.access_token))
            response_code, response = service.rename(src_path=request.data.get('src_path', '/'),
                                                     dst_path=request.data.get('dst_path', '/'))
            return Response({
                'response_code': response_code,
                'message': response if not response_code else response['message'],
                'data': response['data'] if response_code else []
            })
        except Exception as e:
            print(e)
            return Response({
                'response_code': False,
                'message': 'Server has error',
                'data': []
            })

    @action(detail=False, methods=['post'], url_path='download')
    def download(self, request, pk=None):
        try:
            refresh = RefreshToken.for_user(self.request.user)
            service = FTPService(token=str(refresh.access_token))
            response_code, response = service.download(dst_path=request.data.get('dst_path', '/'),
                                                       src_path=request.data.get('src_path', '/'))
            return Response({
                'response_code': response_code,
                'message': response if not response_code else response['message'],
                'data': []
            })
        except Exception as e:
            print(e)
            return Response({
                'response_code': False,
                'message': 'Server has error',
                'data': []
            })

    @action(detail=False, methods=['post'], url_path='copy')
    def copy(self, request, pk=None):
        try:
            refresh = RefreshToken.for_user(self.request.user)
            service = FTPService(token=str(refresh.access_token))
            response_code, response = service.copy(dst_path=request.data.get('dst_path', '/'),
                                                       src_path=request.data.get('src_path', '/'))

            return Response({
                'response_code': response_code,
                'message': response if not response_code else response['message'],
                'data': []
            })
        except Exception as e:
            print(e)
            return Response({
                'response_code': False,
                'message': 'Server has error',
                'data': []
            })

    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request, pk=None):
        try:
            refresh = RefreshToken.for_user(self.request.user)
            service = FTPService(token=str(refresh.access_token))
            upload_files = []

            # for file in self.request.FILES.getlist('files'):
                # upload = Upload(user=self.request.user, file=file)
                # upload.save()
                # UpFile = apps.get_model('Contest.UploadFile')
                # m_file = UpFile()
                # m_file.file = file
                # m_file.name = str(file)
                # m_file.resource = self
                # m_file.save()
                # upload_files.append(UpFile)
            files= self.request.FILES['files'].file.getvalue() 
            # print(files)
            service.upload(files)
            return Response({
                'response_code': True,
                'message': 'message',
                'data': []
            })
        except Exception as e:
            print(e)
            return Response({
                'response_code': False,
                'message': 'Server has error',
                'data': []
            })


class FTPUploadView(APIView):

    def post(self, request, *args, **kwargs):
        for file in self.request.FILES.getlist('files'):
            print(file)
            return Response({
                'response_code': True,
                'message': 'message',
                'data': []
            })
