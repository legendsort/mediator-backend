from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets
from Account.service import MediatorService
from rest_framework_simplejwt.tokens import RefreshToken


class MediatorViewSet(viewsets.ViewSet):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='connect')
    def connect_mediator(self, request, pk=None):
        try:

            refresh = RefreshToken.for_user(self.request.user)
            service = MediatorService(token=str(refresh.access_token))
            response_code, response = service.connect()
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
