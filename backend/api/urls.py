from django.urls import include, path
from rest_framework import routers

from recipes.views import (
    IngredientsView,
    IngredientsDetailView, TagsView, TagsDetailView,
    RecipesListCreateView,
    RecipesDetailUpdaateDeleteView,
    GetLinkView, ShoppingCartView,
    FavoriteRecipeView,
    IndexListView
)

from users.views import (
    SignUpView,
    TokenView,
    ProfileView,
    MyView,
    MyAvatarView,
    SetPasswordView, SubscriptionListView, SubscribeView,

    # SubscribeView,
)

ingredients_patterns = [
    path('', IngredientsView.as_view(), name='ingredients-list'),
    path('<int:pk>/', IngredientsDetailView.as_view(), name='ingredients-detail'),
]
tags_patterns = [
    path('', TagsView.as_view(), name='tags-list'),
    path('<int:pk>/', TagsDetailView.as_view(), name='tags-detail'),
]
recipes_patterns = [
    path('', RecipesListCreateView.as_view(), name='recipes-list'),
    path('<int:pk>/favorite/',
         FavoriteRecipeView.as_view(), name='favorite-recipe'),
    path('<int:pk>/shopping_cart/',
         ShoppingCartView.as_view(), name='add-recipe-to-cart'),
    path('<int:pk>/get-link/', GetLinkView.as_view(), name='get-short-link'),
    path('<int:pk>/',
         RecipesDetailUpdaateDeleteView.as_view(), name='recipes-detail'),
]
auth_patterns = [
    path('token/login/', TokenView.as_view(), name='login'),
    path('', include('djoser.urls.authtoken')),
    #path('', SignUpView.as_view(), name='signup'),
]
users_patterns = [
    path('me/avatar/', MyAvatarView.as_view(), name='avatar-detail'),
    path('me/', MyView.as_view(), name='list'),
    path(
        'subscriptions/',
        SubscriptionListView.as_view(),
        name='subscriptions'
    ),
    path('set_password/', SetPasswordView.as_view(), name='set-password'),
    path('', SignUpView.as_view(), name='signup'),

    path(
        '<int:id>/subscribe/',
        SubscribeView.as_view(), name='subscribe'),
    path('<int:id>/', ProfileView.as_view(({'get': 'retrieve'})), name='profile'),
]

urlpatterns = [
    path('users/', include(users_patterns)),
    path('auth/', include(auth_patterns)),
    path('ingredients/', include(ingredients_patterns)),
    path('tags/', include(tags_patterns)),
    path('recipes/', include(recipes_patterns)),
    path('',IndexListView.as_view(), name='index')
]
