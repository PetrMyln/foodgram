from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib import admin




api_patterns = [
    path('', include('users.urls')),
   # path('', include('api.urls')),
]

urlpatterns = [

    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),

    ),
]
