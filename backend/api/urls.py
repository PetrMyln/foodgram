from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    TagsView,
    RecipesView,
    IngredientsView,

)
from api.views import (
    UserViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagsView, basename='tags')
router.register('ingredients', IngredientsView, basename='recipes')
router.register('recipes', RecipesView, basename='ingredients')

auth_patterns = [
    path('', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('', include(router.urls)),
]
