from django.urls import include, path
from rest_framework import routers

from users.views import (
    SignUpView,
    TokenView,
    ProfileView,
    MyView,
    MyAvatarView,
    SetPasswordView, SubscriptionListView, SubscribeView,

    # SubscribeView,
)



auth_patterns = [
    path('token/login/', TokenView.as_view(), name='login'),
    path('', include('djoser.urls.authtoken')),

]

users_patterns = [
    path('me/avatar/', MyAvatarView.as_view(), name='avatar-detail'),
    path('me/', MyView.as_view(), name='list'),
   path(
        'subscriptions/',
         SubscriptionListView.as_view(),
         name='subscriptions'
    ),
    path('set_password/', SetPasswordView.as_view(), name='signup'),
    path('', SignUpView.as_view(), name='signup'),

    path(
        '<int:id>/subscribe/',
        SubscribeView.as_view(), name='subscribe'),
    path('<int:id>/', ProfileView.as_view(({'get': 'retrieve'})), name='profile'),
]

urlpatterns = [
    path('users/', include(users_patterns)),
    path('auth/', include(auth_patterns)),
]
