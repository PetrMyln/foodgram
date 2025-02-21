from django.urls import include, path
from rest_framework import routers

from users.views import (
    SignUpView,
    TokenView,
    ProfileView,
    MyView,
    MyAvatarView,
    SetPasswordView,
)

v1_router = routers.DefaultRouter()

v1_router.register('users', ProfileView, basename='profile')
#v1_router.register('users/me/avatar', MyAvatarView, basename='avatar')


auth_patterns = [
    path('token/login/', TokenView.as_view(), name='login'),
    path('', include('djoser.urls.authtoken')),

]


users_patterns = [
    path('me/avatar/', MyAvatarView.as_view(), name='avatar-detail'),
    path('me/', MyView.as_view(), name='profile-detail'),
    path('set_password/', SetPasswordView.as_view(), name='signup'),
    path('', SignUpView.as_view(), name='signup'),
    #path('users/(?P<id>\d+)', ProfileView.as_view(), name='profile'),
    #path('', include(v1_router.urls)),

    #path('users/me/', MyView.as_view(), name='myprofile'),

    #path('', include('djoser.urls')),
    #path('auth/token/login/', TokenView.as_view(), name='token'),
    #path('auth/', include('djoser.urls.authtoken')),


]


urlpatterns = [
    path('users/', include(users_patterns)),
    path('auth/', include(auth_patterns)),
]