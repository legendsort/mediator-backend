from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from Wipo.views import FTPViewSet, FTPUploadView
from rest_framework.routers import DefaultRouter
router = DefaultRouter(trailing_slash=False)
router.register(r'ftp', FTPViewSet, basename='ftp')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'upload', FTPUploadView.as_view())
]