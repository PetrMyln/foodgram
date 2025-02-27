from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from users.models import User, Follow

from users.models import User



class UserAdmin(BaseUserAdmin):

    list_display = ('username', 'email',)
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    add_fieldsets = BaseUserAdmin.add_fieldsets
    fieldsets = BaseUserAdmin.fieldsets

class FollowAdmin(BaseUserAdmin):
    list_display = ['id', 'user', 'follower']
    filter_horizontal = []
    ordering = ['id']
    list_filter = ['id']


admin.site.register(Follow, FollowAdmin)
admin.site.register(User, UserAdmin)