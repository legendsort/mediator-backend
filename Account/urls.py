from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from Account.views import UserViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter(trailing_slash=False)
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    path(r'', include(router.urls))
]