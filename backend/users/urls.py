from django.urls import include, path
from rest_framework import routers
from django.urls import re_path
from djoser import views


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
path("token/logout/", views.TokenDestroyView.as_view(), name="logout"),

   # path('', include('djoser.urls.authtoken')),


    #path('token/login/', CustomTokenCreateView.as_view(), name='login'),
    #path('token/login/', CustomTokenCreateView.as_view(), name='login'),
    #path("token/logout/", views.TokenDestroyView.as_view(), name="logout"),
    # path("token/logout/", CustomTokenDestroyView.as_view(), name="logout"),
#path('', include('djoser.urls')),
    #path('', include('djoser.urls.authtoken')),
#re_path(r"^token/login/?$", views.TokenCreateView.as_view(), name="logout"),
    #path('token/login/', views.TokenObtainPairView.as_view(), name="jwt-create".as_view(), name='login'),
#path("token/logout/", CustomTokenDestroyView.as_view(), name="logout"),
    #path('', include('djoser.urls.jwt')),

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

    path(
        '<int:id>/subscribe/',
        SubscribeView.as_view(), name='subscribe'),
    path('<int:id>/', ProfileView.as_view(({'get': 'retrieve'})), name='profile'),
    path('', SignUpView.as_view(), name='signup'),
]

urlpatterns = [
    path('users/', include(users_patterns)),
    path('auth/', include(auth_patterns)),
]
