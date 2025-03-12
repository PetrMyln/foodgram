from rest_framework import permissions


class UserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        rule_auth = request.user.is_authenticated
        rule_kwargs = request.parser_context['kwargs'].get('id', None)

        if not rule_auth and rule_kwargs is None:
            return False
        return (
            request.method in permissions.SAFE_METHODS
            or rule_auth
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
