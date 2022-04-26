import django.db.utils
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
import Paper.serializers
from Paper.models import Journal, ReviewType, Order, Status
from Paper.serializers import JournalSerializer, OrderSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Paper.helper import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_tricks import filters
from Paper.policies import PublisherAccessPolicy
from Paper.helper import filter_params


# Journal API
class OrderFilter(django_filters.FilterSet):
    status = django_filters.ModelMultipleChoiceFilter(field_name='status', queryset=Status.objects.all())

    class Meta:
        model = Order
        fields = {
            'status': ['in']
        }


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = OrderFilter
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]

    def get_queryset(self):
        orders = Order.objects.filter(order_submit=None)
        user = self.request.user
        if user.is_superuser:
            return orders
        elif user.has_perm('manage_order'):
            return orders
        elif user.has_perm('deal_order'):
            return orders.filter(user=user)
        else:
            return orders.filter(pk=None)

    def create(self, request, *args, **kwargs):
        try:
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': 'Successfully created!'
            })
        except Exception as e:
            print('----', e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create order'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': 'Duplicated name'
            })
            pass
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'server has error'
            })

    # remove journal element
    def destroy(self, request, *args, **kwargs):
        try:
            self.perform_destroy(self.get_object())
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': 'Successfully removed!'
            })
        except django.db.DatabaseError as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Can not remove this  instance'
            })

