from rest_access_policy import AccessPolicy
from Paper.helper import SubmissionStatus


class PublisherAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "condition": "has_permission:view_contest",
            "effect": "allow"
        },
    ]

    def has_permission(self, request, view) -> bool:
        user = request.user
        return user.has_perm('view_contest') or user.has_perm('manage_contest')


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
            "action": ["accept", "send"],
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
