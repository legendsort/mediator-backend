from rest_framework import serializers
from Paper.models import Journal, ReviewType, Country, ProductType, Frequency, Category,\
    Publisher, Article, Submit, Order, Author, Status, Requirement, UploadFile, OrderStatusLog, Resource
from Contest.serializers import UploadSerializer
from Account.serializers import BusinessSerializer, UserDetailSerializer

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
            'description'
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
            'iso3',
            'nice_name',
            'num_code',
            'phone_code',
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


class PublisherSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publisher
        fields = [
            'id',
            'name',
        ]


class JournalSerializer(serializers.ModelSerializer):
    review_type = ReviewTypeSerializer(read_only=True)
    countries = CountrySerializer(many=True, required=False)
    frequency = FrequencySerializer(read_only=True)
    categories = CategorySerializer(many=True, required=False)
    products = ProductTypeSerializer(many=True, required=False)
    publisher = PublisherSerializer(read_only=True, required=False)

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


class JournalSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Journal
        fields = [
            'id',
            'name',

        ]


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = [
            'id',
            'name',
            'description',
        ]


class AuthorSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    country_id = serializers.SerializerMethodField(read_only=True)

    def get_country_id(self, obj):
        try:
            country = obj.country
            return country.id
        except Exception as e:
            print(e)
            return None

    class Meta:
        model = Author
        fields = [
            'first_name',
            'last_name',
            'position',
            'reason',
            'email',
            'appellation',
            'type',
            'country_id'
        ]


class UploadFileSerializer(serializers.ModelSerializer):
    requirement = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UploadFile
        fields = [
            'id',
            'requirement',
            'file',
            'name'
        ]


class StatusLogsSerializer(serializers.ModelSerializer):
    status = serializers.StringRelatedField(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = OrderStatusLog
        fields = [
            'id',
            'order',
            'message',
            'status',
            'created_at'
        ]


class SubmitSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    dealer = serializers.StringRelatedField(read_only=True)
    article = serializers.PrimaryKeyRelatedField(read_only=True)
    abstract = serializers.CharField(required=True)
    keywords = serializers.CharField(required=True)
    journal = serializers.PrimaryKeyRelatedField(read_only=True)
    authors = AuthorSerializer(source='get_authors',  read_only=True, many=True)
    upload_files = UploadFileSerializer(source='get_upload_files',  read_only=True, many=True)
    status = serializers.StringRelatedField(read_only=True)
    message = serializers.SerializerMethodField(read_only=True)
    status_logs = StatusLogsSerializer(source='get_status_logs', many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    @staticmethod
    def get_message(obj):
        try:
            order = obj.set_order()
            return OrderStatusLog.objects.filter(status=obj.status, order=order).first().message

        except Exception as e:
            return ''

    class Meta:
        model = Submit
        fields = [
            'id',
            'user',
            'article',
            'title',
            'abstract',
            'keywords',
            'major',
            'journal',
            'authors',
            'upload_files',
            'status',
            'dealer',
            'message',
            'created_at',
            'status_logs'
        ]


class SubmitListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    order_id = serializers.SerializerMethodField(read_only=True)
    dealer = serializers.StringRelatedField(read_only=True)
    article = serializers.StringRelatedField(read_only=True)
    journal = serializers.StringRelatedField(read_only=True)
    status = serializers.StringRelatedField(read_only=True)
    message = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_updated_at = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_message(obj):
        try:
            order = obj.set_order()
            return OrderStatusLog.objects.filter(status=obj.status, order=order).first().message
        except Exception as e:
            print('-->', e)
            return ''

    @staticmethod
    def get_order_id(obj):
        try:
            order = obj.set_order()
            return order.id
        except Exception as e:
            print('-->', e)
            return ''

    @staticmethod
    def get_last_updated_at(obj):
        try:
            order = obj.set_order()
            return OrderStatusLog.objects.filter(status=obj.status, order=order).first().created_at.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print('-->', e)
            return ''

    class Meta:
        model = Submit
        fields = [
            'id',
            'user',
            'order_id',
            'article',
            'title',
            'abstract',
            'journal',
            'status',
            'dealer',
            'message',
            'created_at',
            'last_updated_at'
        ]


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(read_only=True)
    type = serializers.StringRelatedField(read_only=True)
    status = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'type',
            'status',
        ]


class StatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = [
            'id',
            'name',
            'description',
        ]


class RequirementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Requirement
        fields = [
            'id',
            'name',
            'description',
            'file_type'
        ]

class ResourceUploadSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    upload_files = UploadSerializer(source='get_upload_files',  read_only=True, many=True, required=False)
    order_id = serializers.SerializerMethodField(read_only=True) 
    
    def get_order(self, obj):
        try:
            order = obj.get_order()
            return OrderSerializer(order).data

        except Exception as e:
            return None
    
    def get_order_id(self, obj):
        try:
            order = obj.get_order()
            return order.id

        except Exception as e:
            return None    
    def get_type_id(self, obj):
        try:
            order = obj.get_order()
            return order.type_id

        except Exception as e:
            return None

    class Meta:
        model = Resource
        fields = [
            'id',
            'title',
            'detail',
            'created_at',
            'is_upload',
            'is_allow',
            'upload_files',
            'order_id',
            'flag'
        ]        



class ResourceSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    order_type = serializers.SerializerMethodField(read_only=True)    
    status = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    order_id = serializers.SerializerMethodField(read_only=True) 
    message = serializers.SerializerMethodField(read_only=True)
    dealer = serializers.StringRelatedField(read_only=True)
    status_logs = StatusLogsSerializer(source='get_status_logs', many=True, read_only=True)

    def get_message(self, obj):
        try:
            order = obj.set_order()
            return OrderStatusLog.objects.filter(status=order.status, order=order).first().message

        except Exception as e:            
            return ''

    def get_order_type(self, obj):
        try:
            order = obj.get_order()
            if order.type:
                return order.type.name
            return None

        except Exception as e:
            return None

    def get_status(self, obj):
        try:
            order = obj.get_order()
            return order.status.name

        except Exception as e:
            return None  

    def get_username(self, obj):
        try:
            order = obj.get_order()
            return order.user.username

        except Exception as e:
            return None  
    def get_order_id(self, obj):
        try:
            order = obj.get_order()
            return order.id

        except Exception as e:
            return None                                                      

    class Meta:
        model = Resource
        fields = [
            'id',
            'title',
            'detail',
            'updated_at',
            'order_type',
            'status',
            'username',
            'order_id',
            'message',
            'dealer',
            'status_logs'
        ]        



class ResourceDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)    
    type = serializers.SerializerMethodField(read_only=True)
    upload_files = UploadSerializer(source='get_upload_files',  read_only=True, many=True)
    user = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    order_id = serializers.SerializerMethodField(read_only=True) 
    def get_order(self, obj):
        try:
            order = obj.get_order()
            return OrderSerializer(order).data

        except Exception as e:
            print(e)
            return None
    def get_order_id(self, obj):
        try:
            order = obj.get_order()
            return order.id

        except Exception as e:
            return None    
    def get_type(self, obj):
        try:
            order = obj.get_order()           
            return BusinessSerializer(order.type).data.get('name')

        except Exception as e:
            print(e)
            return None
    def get_user(self, obj):
        try:
            order = obj.get_order()           
            return UserDetailSerializer(order.user).data.get('username')

        except Exception as e:
            print(e)
            return None

    def get_status(self, obj):
        try:
            order = obj.get_order()           
            return StatusSerializer(order.status).data.get('name')

        except Exception as e:
            print(e)
            return None


    class Meta:
        model = Resource
        fields = [
            'id',
            'title',
            'detail',
            'created_at',            
            'type',
            'user',
            'status',
            'upload_files',
            'order_id',
            'flag'
        ] 

