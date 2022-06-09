from django.urls import path, include
from rest_framework import routers, serializers, viewsets

import Paper.views
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
router.register(r'submit', Paper.views.SubmitViewSet, basename='submit')
router.register(r'status', Paper.views.StatusViewSet, basename='status')
router.register(r'requirement', Paper.views.RequirementViewSet, basename='requirement')
router.register(r'resource', Paper.views.ResourceViewSet, basename='resource')

urlpatterns = [
    path(r'', include(router.urls))
]