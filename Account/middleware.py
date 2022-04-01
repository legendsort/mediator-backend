from rest_framework_simplejwt import authentication
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
import jwt
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from django.conf import settings

JWT_SETTINGS = getattr(settings, "SIMPLE_JWT", None)


@database_sync_to_async
def get_user(user_id):
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token')
        if not token:
            scope['user'] = AnonymousUser()
            return await self.inner(scope, receive, send)
        try:
            valid_data = TokenBackend(algorithm=JWT_SETTINGS['ALGORITHM']).decode(token[0], verify=False)
            user = await get_user(valid_data['user_id'])
            if not user.is_active:
                user = AnonymousUser()
        except TokenBackendError as v:
            user = AnonymousUser()
        except Exception as e:
            print(e)
            user = AnonymousUser()
        scope['user'] = user
        return await self.inner(scope, receive, send)
    


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))


class MiddlewareForPermission:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, **kwargs):
        response = self.get_response()

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.user = authentication.JWTAuthentication().authenticate(request)
        if request.user:
            request.user = request.user[0]
