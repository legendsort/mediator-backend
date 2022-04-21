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


class SubmissionAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve", "create", "update", "partial_update"],
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
            "action": ["accept", "send"],
            "principal": "*",
            "condition_expression": ["has_perms:mediate_paper or has_perms:manage_paper"],
            "effect": "allow"
        },
    ]

    def can_destroy(self, request, view, action, field: str) -> bool:
        user = request.user
        if user.has_perm('manage_paper'):
            return True
        elif user.has_perm('view_paper') and view.get_object().status.name == SubmissionStatus.NEW_SUBMISSION:
            return True
        else:
            return False


    def has_perms(self, request, view, action, field: str) -> bool:
        user = request.user
        print(self._get_invoked_action(view))
        return user.has_perm(field)
