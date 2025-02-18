from django.urls import include, path
from rest_framework import routers

from users.views import UserViewSet, SignUpView, TokenView

v1_router = routers.DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')




auth_patterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='token'),
]

v1_patterns = [
    path('', include(v1_router.urls)),
    path('auth/', include((auth_patterns, 'auth'))),
]

urlpatterns = [
    path('', include(v1_patterns)),
]