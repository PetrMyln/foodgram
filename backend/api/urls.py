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
]


urlpatterns = [
    path('users/', include(users_patterns)),
    path('auth/', include(auth_patterns)),
]