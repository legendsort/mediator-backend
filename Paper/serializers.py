from rest_framework import serializers
from Paper.models import Journal, ReviewType, Country, ProductType, Frequency, Category, Publisher


class FrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Frequency
        fields = [
            'id',
            'name',
            'description',
        ]


class ReviewTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReviewType
        fields = [
            'id',
            'name',
            'json',
        ]


class ProductTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductType
        fields = [
            'id',
            'name',
            'description',
        ]


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = [
            'id',
            'name',
            'iso',
            'nice_name',
            'num_code',
        ]


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
        ]


class PublisherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publisher
        fields = [
            'id',
            'name',
            'name_translate',
            'description',
            'description_translate',
            'logo_url',
            'site_address',
        ]


class JournalSerializer(serializers.ModelSerializer):
    review_type = ReviewTypeSerializer(read_only=True)
    countries = CountrySerializer(many=True)
    frequency = FrequencySerializer(many=True)
    categories = CategorySerializer(many=True)
    products = ProductTypeSerializer(many=True)
    publisher = PublisherSerializer(read_only=True)

    class Meta:
        model = Journal
        fields = [
            'id',
            'name',
            'description',
            'logo_url',
            'issn',
            'eissn',
            'review_type',
            'guide_url',
            'url',
            'start_year',
            'impact_factor',
            'open_access',
            'flag',
            'countries',
            'frequency',
            'categories',
            'products',
            'publisher'
        ]
