from django.urls import include, path
from rest_framework import routers

from users.views import UserViewSet, SignUpView, TokenView

v1_router = routers.DefaultRouter()
v1_router.register('users',UserViewSet, basename='users')
#v1_router.register('users', SignUpView.as_view(), basename='signup')



auth_patterns = [
    path('', SignUpView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='token'),
]

v1_patterns = [
    path('', SignUpView.as_view(), name='signup'),
    #path('', include(v1_router.urls)),
    #path('token/', TokenView.as_view(), name='token'),
]

urlpatterns = [
    path('', include(v1_patterns)),
    path('users/', SignUpView.as_view(), name='signup')
]