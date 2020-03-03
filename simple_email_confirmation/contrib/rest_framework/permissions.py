from rest_framework import permissions


class EmailViewSetPermission(permissions.IsAuthenticated):
    """
    The request is authenticated as a user, or is a request to the
    confirm endpoint.
    """

    def has_permission(self, request, view):
        if view.action == 'confirm':
            return True

        return super().has_permission(request, view)
