from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from Bank.views import DataViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter(trailing_slash=False)
router.register(r'data', DataViewSet, basename='data')

urlpatterns = [
    path(r'', include(router.urls))
]