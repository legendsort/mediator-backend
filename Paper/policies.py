from rest_access_policy import AccessPolicy


class PublisherAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "condition": "has_permission:view_contest",
            "effect": "allow"
        }
    ]

    def has_permission(self, request, view) -> bool:
        user = request.user
        return user.has_perm('view_contest') or user.has_perm('manage_contest')
