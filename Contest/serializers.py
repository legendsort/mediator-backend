from rest_framework import serializers
from Contest.models import UploadFile
class UploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadFile
        fields = [
            'id',
            'name'
            'file',
        ]

