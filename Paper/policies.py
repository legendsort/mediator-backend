from rest_access_policy import AccessPolicy
from Paper.helper import SubmissionStatus


class PublisherAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "condition": ["has_permissions"],
            "effect": "allow"
        },
    ]

    @staticmethod
    def has_permissions(request, view, action) -> bool:
        user = request.user
        return user.has_perm('view_paper') or user.has_perm('manage_paper') or user.is_superuser


class JournalAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["destroy", "update", "partial_update", "create"],
            "principal": "*",
            "condition": "has_permissions:manage_paper",
            "effect": "allow"
        },
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "effect": "allow"
        },
    ]

    @staticmethod
    def has_permissions(request, view, actions, params=None) -> bool:
        user = request.user
        print(params)
        return user.has_perm(params)


class SubmissionAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve", "create", "update", "partial_update", "fetch_status"],
            "principal": "*",
            "condition_expression": ["has_perms:mediate_paper or has_perms:manage_paper or has_perms:view_paper"],
            "effect": "allow"
        },
        {
            "action": ["update_status"],
            "principal": "*",
            "condition_expression": ["has_perms:mediate_paper or has_perms:manage_paper or has_perms:view_paper"],
            "effect": "allow"
        },
        {
            "action": ["destroy"],
            "principal": "*",
            "condition": ["can_destroy"],
            "effect": "allow"
        },
        {
            "action": ["transfer"],
            "principal": "*",
            "condition": ["can_transfer"],
            "effect": "allow"
        },
        {
            "action": ["accept", "send", "download"],
            "principal": "*",
            "condition_expression": ["has_perms:mediate_paper or has_perms:manage_paper"],
            "effect": "allow"
        },
    ]

    @staticmethod
    def can_destroy(request, view, action, field: str = None) -> bool:
        user = request.user
        if user.has_perm('manage_paper'):
            return True
        elif user.has_perm('view_paper') and view.get_object().status.name == SubmissionStatus.NEW_SUBMISSION:
            return True
        else:
            return False

    @staticmethod
    def can_transfer(request, view, action, field: str = None) -> bool:
        user = request.user
        if user.has_perm('manage_paper'):
            return True
        elif user.has_perm('mediate_paper'):
            submission = view.get_object()
            return submission.user == user
        else:
            return False

    @staticmethod
    def has_perms(request, view, action, field: str) -> bool:
        user = request.user
        return user.has_perm(field)


class RequestAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["destroy", "update", "partial_update", "create"],
            "principal": "*",
            "condition": "has_permissions:view_request",
            "effect": "allow"
        },
        {
            "action": ["accept", "reject", "pub_check"],
            "principal": "*",
            "condition": "has_permissions:manage_request",
            "effect": "allow"
        },
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "effect": "allow",
            "condition": ["can_view_request"],
        },
    ]

    @staticmethod
    def can_view_request(request, view, actions):
        user = request.user
        return user.has_perm('view_request') or user.has_perm('manage_request')

    @staticmethod
    def has_permissions(request, view, actions, params=None) -> bool:
        user = request.user
        return user.has_perm(params)


class PaperSearchPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve", "create", "update", "partial_update", "fetch_status"],
            "principal": "*",
            "condition_expression": ["has_perms:mediate_paper or has_perms:manage_paper or has_perms:view_paper"],
            "effect": "allow"
        },
        {
            "action": ["update_status"],
            "principal": "*",
            "condition_expression": ["has_perms:mediate_paper or has_perms:manage_paper or has_perms:view_paper"],
            "effect": "allow"
        },
        {
            "action": ["destroy"],
            "principal": "*",
            "condition": ["can_destroy"],
            "effect": "allow"
        },
        {
            "action": ["transfer"],
            "principal": "*",
            "condition": ["can_transfer"],
            "effect": "allow"
        },
        {
            "action": ["accept", "send", "download"],
            "principal": "*",
            "condition_expression": ["has_perms:mediate_paper or has_perms:manage_paper"],
            "effect": "allow"
        },
    ]

    @staticmethod
    def can_destroy(request, view, action, field: str = None) -> bool:
        user = request.user
        if user.has_perm('manage_paper'):
            return True
        elif user.has_perm('view_paper') and view.get_object().status.name == SubmissionStatus.NEW_SUBMISSION:
            return True
        else:
            return False

    @staticmethod
    def can_transfer(request, view, action, field: str = None) -> bool:
        user = request.user
        if user.has_perm('manage_paper'):
            return True
        elif user.has_perm('mediate_paper'):
            submission = view.get_object()
            return submission.user == user
        else:
            return False

    @staticmethod
    def has_perms(request, view, action, field: str) -> bool:
        user = request.user
        return user.has_perm(field)

