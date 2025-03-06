from rest_framework import permissions


class UserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user or request.user.is_superuser)

class AuthorOrModeratorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated or
                request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class Author(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class UserMePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print(self.__dict__)
        print()
        print(request.__dict__)
        return (request.user.is_authenticated or
                request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.user.is_admin)
