from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from Paper.views.OrderRestful import OrderViewSet
from Paper.views.ResourceRestful import ResourceViewSet, ResourceUploadViewSet
from Paper.views.PaperSubmitRestful import SubmitViewSet
from Contest.views import UploadViewSet
from Paper.views.PaperRestful import JournalViewSet, PublisherViewSet, CountryViewSet, CategoryViewSet, \
    ProductTypeViewSet, FrequencyViewSet, ReviewTypeViewSet, ArticleViewSet, StatusViewSet,RequirementViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter(trailing_slash=False)
router.register(r'journal', JournalViewSet, basename='journal')
router.register(r'publisher', PublisherViewSet, basename='publisher')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'product-type', ProductTypeViewSet, basename='product-type')
router.register(r'country', CountryViewSet, basename='country')
router.register(r'frequency', FrequencyViewSet, basename='publish')
router.register(r'review-type', ReviewTypeViewSet, basename='review-type')
router.register(r'article', ArticleViewSet, basename='article')
router.register(r'submit', SubmitViewSet, basename='submit')
router.register(r'status', StatusViewSet, basename='status')
router.register(r'requirement', RequirementViewSet, basename='requirement')
router.register(r'resource', ResourceViewSet, basename='resource')
router.register(r'resource-upload', ResourceUploadViewSet, basename='resource_upload')
router.register(r'upload', UploadViewSet, basename='upload')
router.register(r'order', OrderViewSet, basename='order')

urlpatterns = [
    path(r'', include(router.urls))
]