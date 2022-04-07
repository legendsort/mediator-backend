from rest_access_policy import AccessPolicy


class UserAccessPolicy(AccessPolicy):
    statements = [
        {
            'action': ['list', 'retrieve', ],
            'principle': '*',
            'effect': 'allow'
        }
    ]

    def manageable_user(self, request, view, action) -> bool:
        self.statements
        return True
