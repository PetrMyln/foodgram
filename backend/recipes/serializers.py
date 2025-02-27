import base64

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from foodgram_backend.constant import LENGTH_TEXT, LENGTH_USERNAME
from foodgram_backend.validators import validate_username, ValidationError
from recipes.models import Ingredient, Tag, Recipes, RecipesIngredient, RecipeTag, ShoppingCart, FavoriteRecipe
from users.serializers import Base64ImageField, UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeTagSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = RecipeTag
        fields = 'tag',


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = 'id', 'name', 'measurement_unit', 'amount',

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ing_data = representation.get('id')
        ingredient = RecipesIngredient.objects.get(id=ing_data)
        representation["name"] = ingredient.ingredient.name
        representation["measurement_unit"] = ingredient.ingredient.measurement_unit
        representation.move_to_end('amount')
        return representation


class RecipeMixinSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UserSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientSerializer(many=True)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        ingred_list = []
        for ingredient_data in ingredients_data:
            rec_ig = RecipesIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient_data['id']),
                amount=ingredient_data['amount'],
            )
            ingred_list.append(rec_ig)
        recipe.tags.set(tags_data)
        recipe.ingredients.set(ingred_list)
        return recipe


class RecipesSerializer(RecipeMixinSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UserSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipes
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',

        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        tags_data = representation.get('tags', [])
        representation['tags'] = [
            {
                'id': tag.id,
                "name": tag.name,
                "slug": tag.slug
            } for tag in Tag.objects.filter(id__in=tags_data)
        ]
        return representation

    def get_is_favorited(self, obj):
        user = self.context['request'].user.pk
        recipe = obj.pk
        return FavoriteRecipe.objects.filter(user_id=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user.pk
        recipe = obj.pk
        return ShoppingCart.objects.filter(user_id=user, recipe=recipe).exists()


class RecipesPostSerializer(RecipeMixinSerializer):
    author = UserSerializer(default=serializers.CurrentUserDefault(), write_only=True)

    class Meta:
        model = Recipes
        fields = [
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
        ]

    def update(self, instance, validated_data):
        instance.author = self.context['request'].user
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.ingredients.all().delete()
        ingred_list = []
        for ingredient_data in ingredients_data:
            obj = RecipesIngredient.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(pk=ingredient_data['id']),
                amount=ingredient_data['amount'],
            )
            ingred_list.append(obj)
        instance.ingredients.set(ingred_list)
        instance.tags.set(tags_data)
        return instance


class ShoppingSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    # name = serializers.SerializerMethodField()
    # image = Base64ImageField(required=False, allow_null=True)
    # image = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']
