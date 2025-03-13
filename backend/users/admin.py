from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from recipes.models import Recipes
from users.models import User, Follow


class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'follow_count',
        'recipe_count',
    )
    search_fields = ('username', 'email', 'first_name')
    add_fieldsets = BaseUserAdmin.add_fieldsets
    fieldsets = BaseUserAdmin.fieldsets

    @admin.display(description='Количество в подписчиков')
    def follow_count(self, obj):
        return Follow.objects.filter(user=obj).count()

    @admin.display(description='Количество в рецептов')
    def recipe_count(self, obj):
        return Recipes.objects.filter(author=obj).count()


class FollowAdmin(BaseUserAdmin):
    list_display = ['id', 'user', 'follower']
    filter_horizontal = []
    ordering = ['id']
    list_filter = ['id']


admin.site.register(Follow, FollowAdmin)
admin.site.register(User, UserAdmin)
