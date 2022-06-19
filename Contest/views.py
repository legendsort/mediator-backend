from django.shortcuts import render
import django.db.utils
from django.http import JsonResponse
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from Contest.models import UploadFile
from Contest.serializers import UploadSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Paper.helper import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_tricks import filters


# Upload API
class UploadFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = UploadFile
        fields = {
            'name': ['icontains']
        }


class UploadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = UploadSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = UploadFilter
    queryset = UploadFile.objects.all()
 