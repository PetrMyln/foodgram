from django.urls import include, path
from rest_framework import routers

from users.views import SignUpView, TokenView, ProfileView,MyView,MyAvatarView

v1_router = routers.DefaultRouter()

v1_router.register('users', ProfileView, basename='profile')
#v1_router.register('users/me/avatar', MyAvatarView, basename='avatar')


auth_patterns = [
    path('token/login/', TokenView.as_view(), name='token'),
    path('', include('djoser.urls.authtoken')),

]


urlpatterns = [
    path('users/me/avatar/', MyAvatarView.as_view(), name='my-avatar-profile'),
    path('users/me/', MyView.as_view(), name='my-profile'),
    path('users/', SignUpView.as_view(), name='signup'),
    path('', include(v1_router.urls)),

    #path('users/me/', MyView.as_view(), name='myprofile'),

    #path('', include('djoser.urls')),
    #path('auth/token/login/', TokenView.as_view(), name='token'),
    #path('auth/', include('djoser.urls.authtoken')),

    path('auth/', include(auth_patterns)),
]