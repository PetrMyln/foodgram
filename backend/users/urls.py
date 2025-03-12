from django.urls import include, path

from users.views import (
    MyAvatarView,
    SubscriptionListView,
    SubscribeView,
)


auth_patterns = [
    path('', include('djoser.urls.authtoken')),
]

users_patterns = [
    path('me/avatar/', MyAvatarView.as_view(), name='avatar-detail'),
    path(
        'subscriptions/',
        SubscriptionListView.as_view(),
        name='subscriptions'
    ),
    path(
        '<int:id>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe'
    ),
]



urlpatterns = [

    path('users/', include(users_patterns)),
    path('', include('djoser.urls')),
    path('auth/', include(auth_patterns)),
]
