from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from Account.views import UserViewSet, BusinessTypeViewSet, UnitViewSet, PermissionViewSet, RoleViewSet, NoticeViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter(trailing_slash=False)
router.register(r'user', UserViewSet, basename='user')
router.register(r'business', BusinessTypeViewSet, basename='business')
router.register(r'unit', UnitViewSet, basename='unit')
router.register(r'role', RoleViewSet, basename='role')
router.register(r'permission', PermissionViewSet, basename='permission')
router.register(r'notice', NoticeViewSet, basename='notice')

urlpatterns = [
    path(r'', include(router.urls))
]