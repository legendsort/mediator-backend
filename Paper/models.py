from django.db import models
from Account.models import TimeStampMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
# Create your models here.


class ReviewType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)


class Publisher(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)
    name_translate = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    description_translate = models.TextField(null=True)
    logo_url = models.URLField(null=True)
    site_address = models.URLField(null=True)

    def __str__(self):
        return self.name_translate


class Journal(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    logo_url = models.URLField(null=True)
    issn = models.CharField(max_length=255, null=True)
    review_type = models.ForeignKey(ReviewType, on_delete=models.DO_NOTHING, related_name='journal_review_method')
    publisher = models.ForeignKey(Publisher, on_delete=models.DO_NOTHING, related_name='journal_publisher')
    guide_url = models.URLField(null=True)

    class Meta:
        verbose_name = _("Journal")
        verbose_name_plural = _("Journals")

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)


class Requirement(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    file_type = models.CharField(max_length=192, null=True)


class Order(TimeStampMixin):
    type = models.ForeignKey('Account.BusinessType', on_delete=models.DO_NOTHING, related_name='order_type')
    user = models.ForeignKey('Account.User', on_delete=models.DO_NOTHING, related_name='order_user')
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, related_name='order_status', null=True)
    product = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    status_logs = models.ManyToManyField(
        Status,
        through='OrderStatusLog',
        through_fields=('order', 'status'),
        blank=True,
    )


class OrderStatusLog(TimeStampMixin):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)


class Submit(TimeStampMixin):
    order = GenericRelation(Order, related_query_name='order_submit')
    article = models.ForeignKey(Article, on_delete=models.DO_NOTHING, related_name='submit_article', null=True)
    title = models.CharField(max_length=255, null=True)
    abstract = models.TextField(null=True)
    keywords = models.TextField(null=True)
    upload_files = models.JSONField(null=True)
    major = models.TextField(null=True)
    journal = models.ForeignKey(Journal, on_delete=models.DO_NOTHING, related_name='submit_journal', null=True)


class Resource(TimeStampMixin):
    order = GenericRelation(Order, related_query_name='order_resource')
    is_download = models.BooleanField(default=True)
    file_lists = models.JSONField(null=True)


class Country(models.Model):
    iso = models.CharField(max_length=2)
    name = models.CharField(max_length=80)
    nice_name = models.CharField(max_length=80)
    iso3 = models.CharField(max_length=3, null=True)
    num_code = models.IntegerField(null=True)
    phone_code = models.SmallIntegerField()


class Author(TimeStampMixin):

    class Appellation(models.TextChoices):
        DOCTOR = 'Dr', _('Doctor')
        MR = 'Mr', _('Mr')
        MRS = 'Mrs', _('Mrs')
        MISS = 'Miss', _('Miss')
        PROFESSOR = 'Professor', _('professor')

    class AuthorType(models.TextChoices):
        AUTHOR = 'author', _('Author')
        REVIEWER = 'reviewer', _('Reviewer')

    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    position = models.CharField(max_length=255, null=True)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, null=True)
    reason = models.CharField(max_length=255, null=True)
    submit = models.ForeignKey(Submit, on_delete=models.DO_NOTHING, related_name='submit_author')
    type = models.CharField(max_length=12, choices=AuthorType.choices, default=AuthorType.AUTHOR, )
    appellation = models.CharField(max_length=12,
                                   choices=Appellation.choices,
                                   default=Appellation.MR,)

