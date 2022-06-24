from django.db import models
from Account.models import TimeStampMixin, BusinessType
from Paper.helper import resource_upload_path
import Paper.models


# Create your models here.
class UploadFile(TimeStampMixin):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=resource_upload_path)
    resource = models.ForeignKey(Paper.models.Resource, on_delete=models.CASCADE, related_name='resource_upload_file', null=True)
    type = models.ForeignKey(BusinessType, on_delete=models.CASCADE, related_name='resource_business_type', null=True)
    
