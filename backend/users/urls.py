from django.urls import include, path
from rest_framework import routers
from django.urls import re_path
from djoser import views

from users.views import (
    MyAvatarView,
    SubscriptionListView,
    SubscribeView,
)

auth_patterns = [
    path('', include('djoser.urls.authtoken')),
]

users_patterns = [
    path('users/me/avatar/', MyAvatarView.as_view(), name='avatar-detail'),
    path('', include('djoser.urls')),

]
avatar_subscrie_patterns = [
    path('me/avatar/', MyAvatarView.as_view(), name='avatar-detail'),
    path(
        'subscriptions/',
        SubscriptionListView.as_view(),
        name='subscriptions'
    ),
    path(
        '<int:id>/subscribe/',
        SubscribeView.as_view(), name='subscribe'),
]

urlpatterns = [
    path('users/', include(avatar_subscrie_patterns)),
    path('', include(users_patterns)),
    path('auth/', include(auth_patterns)),
]
