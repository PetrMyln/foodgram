from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    TagsView,
    GetLinkView,
    ShoppingCartView,
    FavoriteRecipeView,
    RecipesView,
    IngredientsView,
    DownloadShoppingCartView,
)
from api.views import (
    MyAvatarView,
    SubscriptionListView,
    SubscribeView,
)

router = DefaultRouter()
router.register('tags', TagsView, basename='tags')
router.register('ingredients', IngredientsView, basename='recipes')
router.register('recipes', RecipesView, basename='ingredients')




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

recipes_patterns = [
    path('download_shopping_cart/',
         DownloadShoppingCartView.as_view(),
         name='cart',
         ),
    path('<int:pk>/favorite/',
         FavoriteRecipeView.as_view(), name='favorite-recipe'),
    path('<int:pk>/shopping_cart/',
         ShoppingCartView.as_view(), name='cart-view'),
    path(
        '<int:pk>/get-link/',
        GetLinkView.as_view(),
        name='get-short-link'
    ),
]

urlpatterns = [
    path('users/', include(users_patterns)),
    path('', include('djoser.urls')),
    path('auth/', include(auth_patterns)),
    path('recipes/', include(recipes_patterns)),
    path('', include(router.urls)),
]
