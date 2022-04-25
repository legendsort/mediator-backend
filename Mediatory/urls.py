"""Mediatory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Account.views.MediatoryAPI import MediatorViewSet
from Bank.views import ScriptConfigViewSet
from rest_framework.routers import DefaultRouter
from Account.views import (
    DecoratedTokenObtainPairView,
    DecoratedTokenVerifyView,
    DecoratedTokenRefreshView,
    test,
    room
)

router = DefaultRouter(trailing_slash=False)
router.register(r'mediator', MediatorViewSet, basename='mediator')
router.register(r'config', ScriptConfigViewSet, basename = 'config')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('test', test),
    path('chat/<str:room_name>/', room, name='room'),
    path(r'api/token', DecoratedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(r'api/token/refresh', DecoratedTokenRefreshView.as_view(), name='token_refresh'),
    path(r'api/token/verify', DecoratedTokenVerifyView.as_view(), name='token_verify'),
    path('api/account/', include('Account.urls')),
    path('api/', include(router.urls)),
    path('api/bank/', include('Bank.urls')),
    path('api/wipo/', include('Wipo.urls')),
    path('api/paper/', include('Paper.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)
