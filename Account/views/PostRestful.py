import django.db.utils
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
import Account.serializers
from Account.models import BusinessType, Unit, Permission, Role, Notice, User, Post, Comment
from Account.serializers import BusinessSerializer, UserOutSideSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Paper.helper import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from Account.policies import PermissionAccessPolicy
from rest_framework_tricks import filters
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action


# Post
class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    user = django_filters.NumberFilter(method='search_by_user', lookup_expr='exact')

    class Meta:
        model = Post
        fields = {
            'title': ['icontains']
        }

    @staticmethod
    def search_by_user(queryset, name, value):
        return queryset.filter()


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = Account.serializers.PostSerializer
    renderer_classes = [JSONResponseRenderer, ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = PostFilter

    def get_queryset(self):
        return Post.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = Account.serializers.PostSerializer(data=request.data)
            author = request.user
            if serializer.is_valid():
                serializer.save()
                instance = serializer.instance
                instance.author = author
                instance.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': serializer.errors,
                    'message': 'Validation error'
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Successfully created!'
            })
        except User.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'You have to select correct receiver'
            })

        except Exception as e:
            print('----', e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create Role'
            })

    @action(detail=True, url_path='comment', methods=['post'])
    def create_comment(self, request, pk=None):
        try:
            user = request.user
            comment = Comment()
            comment.content = request.data.get('content')
            comment.post = self.get_object()
            comment.user = user
            comment.save()
            return JsonResponse({
                'response_code': True,
                'data': Account.serializers.CommentSerializer(comment).data,
                'message': 'Successfully created comment'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Validation error'
            })


