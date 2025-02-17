from django.urls import include, path
from rest_framework import routers

v1_router = routers.DefaultRouter()

v1_patterns = [
    path('', include(v1_router.urls)),

]



urlpatterns = [
    path('v1/', include(v1_patterns)),
]