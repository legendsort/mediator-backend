from rest_access_policy import AccessPolicy


class UserAccessPolicy(AccessPolicy):
    statements = [
        {
            'action': ['list', 'retrieve', 'create', ],
            'principal': '*',
            'effect': 'allow',
            'condition': 'manageable_user'
        },
        {
            "action": ["update"],
            "principal": "*",
            "effect": "allow",
            'condition': 'updatable_user'
        },
        {
            "action": ["get_self_info"],
            "principal": "*",
            "effect": "allow"
        },
    ]

    @staticmethod
    def manageable_user(request, view, action) -> bool:
        return request.user.has_perms(['manage_user']) or request.user.is_superuser

    @staticmethod
    def updatable_user(request, view, action) -> bool:
        update_user = view.get_object()
        return request.user.has_perms(['manage_user']) or request.user.is_superuser or update_user == request.user
