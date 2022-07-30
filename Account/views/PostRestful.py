import django.db.utils
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
import Account.serializers
from Account.models import BusinessType, Unit, Permission, Role, Notice, User, Post, Comment
from Account.serializers import PostSerializer, CommentSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Paper.helper import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from Account.policies import PostAccessPolicy
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
    permission_classes = [IsAuthenticated, PostAccessPolicy]
    serializer_class = Account.serializers.PostSerializer
    renderer_classes = [JSONResponseRenderer, ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PostFilter
    ordering = ['-created_at', 'id']

    def get_queryset(self):
        author = self.request.user
        if author.has_perm('administrator') or author.is_superuser:
            return Post.objects.all()
        else:
            return Post.objects.filter(Q(author=author) | Q(open_access=True))

    def create(self, request, *args, **kwargs):
        try:
            serializer = Account.serializers.PostSerializer(data=request.data, context={'request': request})
            author = request.user
            upload_files = request.data.getlist('attachments')
            if serializer.is_valid():
                serializer.save()
                instance = serializer.instance
                instance.author = author
                if author.has_perm('administrator') or author.is_superuser:
                    instance.open_access = True if request.data.get('open_access') else False
                instance.save()
                instance.assign_upload_files(upload_files)
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
            upload_files = request.data.getlist('attachments')
            comment.assign_upload_files(upload_files)
            return JsonResponse({
                'response_code': True,
                'data': Account.serializers.CommentSerializer(comment, context={'request': request}).data,
                'message': 'Successfully created comment'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'You have no permission this post'
            })

    @action(detail=True, url_path='comment-list', methods=['GET'])
    def comment_list(self, request, pk=None):
        try:
            comments = Comment.objects.filter(post=self.get_object()).order_by('-created_at')
            paginator = StandardResultsSetPagination()
            paginator.page_size = 5
            result_page = paginator.paginate_queryset(comments, request)
            serializer = CommentSerializer(result_page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Fetch Comment error'
            })

    def destroy(self, request, *args, **kwargs):
        try:
            self.perform_destroy(self.get_object())
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': 'Successfully removed!'
            })
        except django.db.DatabaseError:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Can not remove this instance'
            })
