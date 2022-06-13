from rest_access_policy import AccessPolicy


class UserAccessPolicy(AccessPolicy):
    statements = [
        {
            'action': ['list', 'retrieve', 'create', 'destroy', 'reset_password',],
            'principal': '*',
            'effect': 'allow',
            'condition': 'manageable_user'
        },
        {
            "action": ["check_password", 'change_password', ],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["update",  'update_profile'],
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
        return request.user.has_perms(['manage_users']) or request.user.is_superuser

    @staticmethod
    def updatable_user(request, view, action) -> bool:
        update_user = view.get_object()
        return request.user.has_perms(['manage_users']) or request.user.is_superuser or update_user == request.user


class PermissionAccessPolicy(AccessPolicy):
    statements = [
        {
            'action': ['list', 'retrieve', 'create', 'destroy'],
            'principal': '*',
            'effect': 'allow',
            'condition': 'is_administrator'
        },
        {
            "action": ["update"],
            "principal": "*",
            "effect": "allow",
            'condition': 'is_administrator'
        },
    ]

    @staticmethod
    def is_administrator(request, view, action) -> bool:
        return request.user.is_superuser


class UnitAccessPolicy(AccessPolicy):
    statements = [
        {
            'action': ['list', 'retrieve', 'create', 'destroy'],
            'principal': '*',
            'effect': 'allow',
            'condition': 'is_administrator'
        },
        {
            "action": ["update"],
            "principal": "*",
            "effect": "allow",
            'condition': 'is_administrator'
        },
    ]

    @staticmethod
    def is_administrator(request, view, action) -> bool:
        return request.user.is_superuser
