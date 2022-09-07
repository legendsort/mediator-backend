import django.db.utils
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
import Account.serializers
from Account.models import Introduction
from Account.serializers import PostSerializer, CommentSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Paper.helper import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from Account.policies import IntroductionAccessPolicy
from rest_framework_tricks import filters
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action


# Introduction
class IntroductionFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name='type', lookup_expr='exact')

    class Meta:
        model = Introduction
        fields = {
            'title': ['icontains']
        }


# API for Introduce information
class LandingViewSet(viewsets.ModelViewSet):
    permission_classes = [IntroductionAccessPolicy]
    serializer_class = Account.serializers.IntroductionSerializer
    renderer_classes = [JSONResponseRenderer, ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = IntroductionFilter

    def get_queryset(self):
        return Introduction.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = Account.serializers.IntroductionSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': serializer.errors,
                    'message': 'Validation error'
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Successfully created!'
            })
        except Exception as e:
            print('----', e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create Role'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = Account.serializers.IntroductionSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                instance.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': serializer.errors
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Journal has been updated'
            })
            pass
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'server has error'
            })

    def destroy(self, request, *args, **kwargs):
        try:
            self.perform_destroy(self.get_object())
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': 'Successfully removed!'
            })
        except django.db.DatabaseError:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Can not remove this instance'
            })
