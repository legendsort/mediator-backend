from rest_access_policy import AccessPolicy


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
            "condition": "has_perms:view_paper",
            "effect": "allow"
        },
        {
            "action": ["update_status", "destroy"],
            "principal": "*",
            "condition": ["has_perms:manage_paper"],
            "effect": "allow"
        },
        {
            "action": ["accept", "send"],
            "principal": "*",
            "condition_expression": ["has_perms:mediate_paper or has_perms:manage_paper"],
            "effect": "allow"
        },
    ]

    def has_perms(self, request, view, action, field: str) -> bool:
        user = request.user
        print(self._get_invoked_action(view))
        return user.has_perm(field)
