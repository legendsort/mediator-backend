from rest_access_policy import AccessPolicy


class UserAccessPolicy(AccessPolicy):
    statements = [
        {
            'action': ['list', 'retrieve', 'create', 'destroy', 'reset_password', 'create_user', 'update_user'],
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
        {
            "action": ['fetch_transfers'],
            "principal": "*",
            "effect": "allow",
            'condition': 'can_transfer'
        }
    ]

    @staticmethod
    def can_transfer(request, view, action) -> bool:
        return request.user.has_perms(['manage_paper']) or request.user.is_superuser or request.user.has_perms(['mediate_paper'])

    @staticmethod
    def manageable_user(request, view, action) -> bool:
        if action == 'list' or action == 'retrieve' or action == 'create_user' or action == 'update_user':
            return request.user.has_perms(['manage_users']) or request.user.is_superuser or request.user.has_perms(['manage_unit'])
        else:
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


class PostAccessPolicy(AccessPolicy):
    statements = [
        {
            'action': ['list', 'retrieve', 'create',  'create_comment', 'comment_list'],
            'principal': '*',
            'effect': 'allow',
        },
        {
            "action": ['destroy', "update", "partial_update"],
            "principal": "*",
            "effect": "allow",
            'condition': 'is_administrator'
        },
    ]

    @staticmethod
    def is_administrator(request, view, action) -> bool:
        return request.user.is_superuser or request.user.has_perm('administrator')


class IntroductionAccessPolicy(AccessPolicy):
    statements = [
        {
            'action': ['list', 'retrieve'],
            'principal': '*',
            'effect': 'allow',
        },
        {
            "action": ['destroy', "update", "partial_update", "create"],
            "principal": "*",
            "effect": "allow",
            'condition': 'is_administrator'
        },
    ]

    @staticmethod
    def is_administrator(request, view, action) -> bool:
        return request.user.is_superuser or request.user.has_perm('administrator')
