import django.db.utils
from django.http import JsonResponse
import json
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
import Paper.serializers
from Paper.models import Journal, Status, Resource, Exchange
from Paper.serializers import ExchangeListSerializer, ExchangeDetailSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Paper.helper import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_tricks import filters
from Paper.helper import filter_params
from Account.models import BusinessType
from django.apps import apps
from django.db.models import Q
from Paper.policies import PaperSearchPolicy
from Paper.services.PaperSearchService import PaperSearchService
import mimetypes
from django.http import HttpResponse
import os


class PaperSearchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, PaperSearchPolicy, ]

    def list(self, request):
        auth_user = self.request.user
        params = self.request.query_params
        searchService = PaperSearchService()
        res_data = searchService.search(params)
        return JsonResponse({
            'response_code': True,
            'data': res_data,
            'message': 'Searched'
        })

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass
