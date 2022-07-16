import json
from rest_framework.decorators import action
import django.db.utils
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
import Paper.serializers
from Paper.models import Journal, Publisher, Country, ReviewType, Submit, UploadFile, Requirement,\
    Order, Frequency, Article, Status
from Paper.serializers import JournalSerializer, PublisherSerializer, SubmitListSerializer, SubmitSerializer
import django_filters
from Paper.render import JSONResponseRenderer
from Bank.views import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_tricks import filters
from Paper.policies import PublisherAccessPolicy, SubmissionAccessPolicy
from Paper.helper import filter_params, SubmissionStatus
from Paper.services import SubmissionService
from Account.models import User, BusinessType


# Submit API
class SubmitFilter(django_filters.FilterSet):

    class Meta:
        model = Submit
        fields = {
            'id': ['exact', ]
        }


class SubmitViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, SubmissionAccessPolicy]
    serializer_class = Paper.serializers.SubmitSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = SubmitFilter
    renderer_classes = [JSONResponseRenderer, ]
    filter_backends = [DjangoFilterBackend, ]

    def get_base_data(self):
        return filter_params(self.request.data, [
            'title',
            'article_id',
        ])

    # Query set for submission
    def get_queryset(self):
        user = self.request.user
        if user.has_perm('administrator') or user.has_perm('manage_paper'):
            return Submit.objects.all()
        elif user.has_perm('view_paper'):
            return Submit.objects.filter(user=user)
        elif user.has_perm('mediate_paper'):
            return Submit.objects.filter(Q(dealer=user) | Q(dealer=None))
        elif user.has_perm('manage_unit_paper'):
            return Submit.objects.filter(user__unit=user.unit)
        else:
            return Submit.objects.filter(pk=None)

    def get_serializer_class(self):
        if self.action == 'list':
            return SubmitListSerializer
        else:
            return SubmitSerializer

    # new submit paper request
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                request_data = request.data
                journal_id = request_data.get('journal_id')
                article_id = request_data.get('article_id')
                authors = request.data.get('authors')
                upload_files = request.data.getlist('files')
                upload_files_key = request.data.getlist('files_requirement')
                if not journal_id or not Journal.objects.filter(pk=journal_id).exists():
                    raise ValidationError('journal_id')
                if not article_id or not Article.objects.filter(pk=article_id).exists():
                    raise ValidationError('article_id')
                if not authors or type(authors) is not str:
                    raise ValidationError('authors')
                if not upload_files:
                    raise ValidationError('upload_files')
                serializer.save()
                instance = serializer.instance
                instance.article = Article.objects.get(pk=article_id)
                instance.journal = Journal.objects.get(pk=journal_id)
                authors = json.loads(authors)
                result = instance.set_authors(authors)
                if len(result):
                    instance.delete()
                    return JsonResponse({
                        'response_code': False,
                        'data': result,
                        'message': 'Your submit has some errors. Please check details'
                    })
                instance.set_upload_files(upload_files, upload_files_key)
                instance.user = request.user
                instance.status = Status.objects.get(name='New Submission')
                instance.save()
                instance.set_order()
                instance.update_status(Status.objects.get(name='New Submission'))

            else:
                print(serializer.errors)
                return JsonResponse({
                    'response_code': False,
                    'data': serializer.errors,
                    'message': 'Your submit has some errors. Please check details'
                })
            return JsonResponse({
                'response_code': True,
                'data': serializer.data,
                'message': 'Successfully created!'
            })
        except ValidationError as e:
            return JsonResponse({
                'response_code': False,
                'data': str(e.message),
                'message': f"Your submit has some errors. Please check details {str(e.message)}"
            })
        except Exception as e:
            print('----', e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Failed create journal'
            })

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.status == Status.objects.get(name='New Submission') and not instance.dealer:
                request_data = request.data
                instance.title = request_data.get('title', instance.title)
                instance.keywords = request_data.get('keywords', instance.keywords)
                instance.abstract = request_data.get('abstract', instance.abstract)
                instance.major = request_data.get('major', instance.major)
                journal_id = request_data.get('journal_id')
                article_id = request_data.get('article_id')
                authors = request.data.get('authors')
                upload_files = request.data.getlist('files')
                upload_files_key = request.data.getlist('files_requirement')
                if journal_id and Journal.objects.filter(pk=journal_id).exists():
                    instance.journal = Journal.objects.get(pk=journal_id)
                if article_id and Article.objects.filter(pk=article_id).exists():
                    instance.article = Article.objects.get(pk=article_id)
                if authors or type(authors) is str:
                    authors = json.loads(authors)
                if upload_files and upload_files_key:
                    instance.set_upload_files(upload_files, upload_files_key)
                instance.user = request.user
                instance.save()
                instance.set_order()
                instance.update_status(Status.objects.get(name='New Submission'))
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': 'Cannot update this submission'
                })

            return JsonResponse({
                'response_code': True,
                'data':  self.serializer_class(instance).data,
                'message': 'Submission has been updated'
            })
        except django.http.response.Http404:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Not Found'
            })
        except Exception as e:
            print(type(e))
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'server has error'
            })

    # remove journal element
    def destroy(self, request, *args, **kwargs):
        try:
            self.perform_destroy(self.get_object())
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': 'Successfully removed!'
            })
        except django.db.DatabaseError as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Can not remove this publisher'
            })

    # update submit status
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        instance = self.get_object()
        try:
            message = request.data.get('message')
            status_id = request.data.get('status_id')
            instance.update_status(Status.objects.get(pk=status_id), message=message)
            instance.save()
            return JsonResponse({
                'response_code': True,
                'data': self.get_serializer(instance).data,
                'message': 'Submission has been updated'
            })
        except Status.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Please submit correct status"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })

    # accept submit for mediate
    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        instance = self.get_object()
        try:
            user = request.user
            instance.dealer = user
            instance.update_status(Status.objects.get(name=SubmissionStatus.START_SUBMISSION),
                                   message=f"Submission has been started by {user.username}")
            instance.save()
            return JsonResponse({
                'response_code': True,
                'data': self.get_serializer(instance).data,
                'message': 'Submission has been accepted'
            })
        except Status.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': f"Submission has no {SubmissionStatus.START_SUBMISSION} status"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })

    # translate dealer
    @action(detail=True, methods=['post'], url_path='transfer')
    def transfer(self, request, pk=None):
        instance = self.get_object()
        try:
            to_user = User.objects.get(pk=request.data.get('user_id'))
            if to_user.has_perm('mediate_paper') or to_user.has_perm('manage_paper'):
                instance.dealer = to_user
                instance.save()
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': f"User {to_user.username} has no permission "
                })
            return JsonResponse({
                'response_code': True,
                'data': [],
                'message': f"Submission {instance.id} has been transfer dealer to {to_user.username}"
            })
        except User.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Please select correct user"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has errors"
            })

    # send information of submit
    @action(detail=True, methods=['post'], url_path='send')
    def send(self, request, pk=None):
        instance = self.get_object()
        try:
            submission_service = SubmissionService(instance)
            res_data = submission_service.send()
            if res_data:
                return JsonResponse(res_data)
            else:
                return JsonResponse({
                    'response_code': False,
                    'data': [],
                    'message': 'Resource send has been failed'
                })
        except Exception as e:
            print('send error', e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': 'Server has errors'
            })

    @action(detail=True, methods=['get'], url_path='fetch-status-logs')
    def fetch_status(self, request, pk=None):
        instance = self.get_object()
        try:
            return JsonResponse({
                'response_code': True,
                'data': self.get_serializer(instance).data['status_logs'],
                'message': 'Submission has been updated'
            })
        except Status.DoesNotExist:
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Please submit correct status"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'response_code': False,
                'data': [],
                'message': "Server has error"
            })

