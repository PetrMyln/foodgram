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
from recipes.models import Ingredient, Tag, Recipes, RecipesIngredient, RecipeTag
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
    # name = serializers.CharField(required=False)
    # amount = serializers.IntegerField(read_only=True)
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.Serializer):
    # id = IngredientSerializer()
    id = serializers.IntegerField()
    # id = serializers.PrimaryKeyRelatedField(
    #    many=True,
    #      queryset=RecipesIngredient.objects.all()
    #   )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = 'id', 'amount',

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ing_data = representation.pop('id')
        ingredient = RecipesIngredient.objects.get(id=ing_data)
        representation["measurement_unit"] = ingredient.ingredient.measurement_unit
        representation["name"] = ingredient.ingredient.name
        representation['id'] = ingredient.ingredient.id
        return representation


class RecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(default=serializers.CurrentUserDefault())
    # author =serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipes
        fields = ['id', 'ingredients', 'tags', 'name', 'author', 'image', 'text', 'cooking_time']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        tags_data = representation.pop('tags', [])
        representation['tags'] = [
            {
                'id': tag.id,
                "name": tag.name,
                "slug": tag.slug
            } for tag in Tag.objects.filter(id__in=tags_data)
        ]
        return representation

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
