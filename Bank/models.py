from django.db import models


# Create your models here.
class DataType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=1024)

    def __str__(self):
        return self.name


class Data(models.Model):
    type = models.ForeignKey(DataType, on_delete=models.DO_NOTHING, related_name='bank_data_type')
    json = models.JSONField(null=True)
    real_data_created_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
