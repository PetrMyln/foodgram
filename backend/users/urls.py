from django.urls import include, path
from rest_framework import routers

from users.views import (
    SignUpView,
    TokenView,
    ProfileView,
    MyView,
    MyAvatarView,
    SetPassword,
)

#v1_router = routers.DefaultRouter()

#v1_router.register('', ProfileView, basename='profile')

auth_patterns = [
    path('token/login/', TokenView.as_view(), name='login'),
    path('', include('djoser.urls.authtoken')),

]

users_patterns = [
    path('me/avatar/', MyAvatarView.as_view(), name='avatar-detail'),
    path('me/', MyView.as_view(), name='profile-detail'),
    path('set_password/', SetPassword.as_view(), name='signup'),
    path('', SignUpView.as_view(), name='signup'),
    path('<int:id>/', ProfileView.as_view(({'get': 'retrieve'})), name='profile'),
]

urlpatterns = [
    path('users/', include(users_patterns)),
    path('auth/', include(auth_patterns)),
]
