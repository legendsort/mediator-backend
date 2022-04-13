from django.contrib import admin
from Paper.models import ReviewType
# Register your models here.


@admin.register(ReviewType)
class ReviewTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'json', 'description')
