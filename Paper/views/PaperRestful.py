import django.db.utils
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
import Paper.serializers
from Paper.models import Journal, Publisher, Country, ReviewType, Category, ProductType, Frequency, Article
from Paper.serializers import JournalSerializer, PublisherSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Paper.helper import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_tricks import filters
from Paper.policies import PublisherAccessPolicy
from Paper.helper import filter_params


# Journal API
class JournalFilter(django_filters.FilterSet):
    publisher = django_filters.ModelMultipleChoiceFilter(field_name='publisher', queryset=Publisher.objects.all())

    class Meta:
        model = Journal
        fields = {
            'name': ['icontains', ],
            'publisher': ['in']
        }


class JournalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = JournalSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = JournalFilter
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    queryset = Journal.objects.all()

    def get_base_data(self):
        return filter_params(self.request.data, [
            'name',
            'description',
            'issn',
            'impact_factor',
            'open_access',
            'flag',
            'eissn',
            'guide_url',
            'logo_url',
            'url',
            'start_year',
        ])

    def create(self, request, *args, **kwargs):
        try:
            base_data = self.get_base_data()
            serializer = JournalSerializer(data=base_data)
            if serializer.is_valid():
                serializer.save()
                countries = request.data.getlist('countries')
                products = request.data.getlist('products')
                categories = request.data.getlist('categories')
                journal = serializer.instance
                journal.assign_product(products)
                journal.assign_country(countries)
                journal.assign_category(categories)
                if request.data.get('review_type') and ReviewType.objects.filter(pk=int(request.data.get('review_type'))).exists():
                    journal.review_type = ReviewType.objects.get(pk=int(request.data.get('review_type')))
                if request.data.get('frequency') and Frequency.objects.filter(
                        pk=int(request.data.get('frequency'))).exists():
                    journal.frequency = Frequency.objects.get(pk=int(request.data.get('frequency')))
                if request.data.get('publisher') and Publisher.objects.filter(
                        pk=int(request.data.get('publisher'))).exists():
                    journal.publisher = Publisher.objects.get(pk=int(request.data.get('publisher')))
                journal.save()
            else:
                print(serializer.errors)
                return JsonResponse({
                    'response_code': False,
                    'data': serializer.errors,
                    'message': 'Duplicated name'
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Successfully created!'
            })
        except Exception as e:
            print('----', e)
            if journal:
                journal.delete()
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create journal'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = JournalSerializer(instance, data=self.get_base_data(), partial=True)
            if serializer.is_valid():
                if request.data.getlist('products') is not []:
                    instance.assign_product(request.data.getlist('products'))
                if request.data.getlist('countries') is not []:
                    instance.assign_country(request.data.getlist('countries'))
                if request.data.getlist('categories') is not []:
                    instance.assign_category(request.data.getlist('categories'))
                if request.data.get('review_type') and ReviewType.objects.filter(
                        pk=int(request.data.get('review_type'))).exists():
                    instance.review_type = ReviewType.objects.get(pk=int(request.data.get('review_type')))
                if request.data.get('frequency') and Frequency.objects.filter(
                        pk=int(request.data.get('frequency'))).exists():
                    instance.frequency = Frequency.objects.get(pk=int(request.data.get('frequency')))
                if request.data.get('publisher') and Publisher.objects.filter(
                        pk=int(request.data.get('publisher'))).exists():
                    instance.publisher = Publisher.objects.get(pk=int(request.data.get('publisher')))
                serializer.save()
                instance.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': serializer.errors
                })
            return JsonResponse({
                'response_code': False,
                'data': serializer.data,
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


# publisher API

class PublisherFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Publisher
        fields = {
            'id': ['exact'],
            'name': ['icontains']
        }


class PublisherViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PublisherAccessPolicy]
    serializer_class = PublisherSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = PublisherFilter
    queryset = Publisher.objects.all()

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
                'message': 'Can not remove this  instance'
            })


# country API
class CountryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Country
        fields = {
            'name': ['icontains']
        }


class CountryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.CountrySerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = CountryFilter
    queryset = Country.objects.all()

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
                'message': 'Can not remove this  instance'
            })


# review Type API
class ReviewTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = ReviewType
        fields = {
            'name': ['icontains']
        }


class ReviewTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.ReviewTypeSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = ReviewTypeFilter
    queryset = ReviewType.objects.all()

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
                'message': 'Can not remove this  instance'
            })


# Frequency API
class FrequencyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Frequency
        fields = {
            'name': ['icontains']
        }


class FrequencyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.FrequencySerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = FrequencyFilter
    queryset = Frequency.objects.all()

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
                'message': 'Can not remove this  instance'
            })


# Products API
class ProductTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = ProductType
        fields = {
            'name': ['icontains']
        }


class ProductTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.ProductTypeSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = ProductTypeFilter
    queryset = ProductType.objects.all()

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
                'message': 'Can not remove this  instance'
            })


# Category API
class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = {
            'name': ['icontains']
        }


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.CategorySerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = CategoryFilter
    queryset = Category.objects.all()

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
                'message': 'Can not remove this  instance'
            })


# Article API
class ArticleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    class Meta:
        model = Article
        fields = {
            'name': ['icontains']
        }


class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.ArticleSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = ArticleFilter
    queryset = Article.objects.all()

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
                'message': 'Can not remove this  instance'
            })


# Status API
class StatusFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Paper.models.Status
        fields = {
            'name': ['icontains']
        }


class StatusViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.StatusSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = StatusFilter
    queryset = Paper.models.Status.objects.all()

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
                'message': 'Can not remove this  instance'
            })


# Requirement API
class RequirementFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Paper.models.Requirement
        fields = {
            'name': ['icontains']
        }


class RequirementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Paper.serializers.RequirementSerializer
    pagination_class = StandardResultsSetPagination
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RequirementFilter
    queryset = Paper.models.Requirement.objects.all()

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
                'message': 'Can not remove this  instance'
            })