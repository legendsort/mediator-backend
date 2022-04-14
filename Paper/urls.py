from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from Paper.views.PaperRestful import JournalViewSet, PublisherViewSet, CountryViewSet, CategoryViewSet, \
    ProductTypeViewSet, FrequencyViewSet, ReviewTypeViewSet, ArticleViewSet
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

urlpatterns = [
    path(r'', include(router.urls))
]