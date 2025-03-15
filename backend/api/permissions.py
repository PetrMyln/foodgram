from rest_framework import permissions


class UserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Ревью. Тут я тоже сплоховал.
        # этот костыль который вы просили заменить
        # проверяет есть ли в  ендпойнте user/ id или иное (me/ /avatar/).
        # тесту нужна 401 ошибка а у меня только 500
        # У меня переопределены в сетингах пермишены для djoser
        rule_auth = request.user.is_authenticated
        rule_kwargs = request.parser_context['kwargs'].get('id', None)
        if not rule_auth and rule_kwargs is None:
            return False
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class AuthorOrModeratorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
