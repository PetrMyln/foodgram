from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib import admin

from recipes.views import (

    RedirectView,
)

api_patterns = [
    path('', include('users.urls')),
    path('', include('recipes.urls')),
]

short_link = [

    path('<str:link>', RedirectView.as_view(), name='redirect')

]


urlpatterns = [
    path('s/', include(short_link)),
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),

    ),
    #path('<str:link>', RedirectView.as_view(), name='redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
