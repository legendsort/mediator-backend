from rest_framework import serializers
from Bank.models import Data, DataType


class DataTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataType
        fields = [
            'name',
        ]


class DataSerializer(serializers.ModelSerializer):
    type = serializers.StringRelatedField()

    class Meta:
        model = Data
        fields = [
            'id',
            'json',
            'type',
            'real_data_created_at'
        ]
