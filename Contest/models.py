from django.db import models
from Account.models import TimeStampMixin, BusinessType
from Paper.helper import resource_upload_path
from Paper.models import Resource


# Create your models here.
class UploadFile(TimeStampMixin):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=resource_upload_path)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='resource_upload_file', null=True)
    type = models.ForeignKey(BusinessType, on_delete=models.CASCADE, related_name='resource_business_type')
