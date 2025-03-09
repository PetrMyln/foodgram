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
from recipes.models import (
    Ingredient,
    Tag, Recipes,
    RecipesIngredient,
    RecipeTag,
    ShoppingCart,
    FavoriteRecipe)
from users.serializers import Base64ImageField, UsersSerializer


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
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=128)
    measurement_unit = serializers.CharField(max_length=64)

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
    FIELDS = [
        'tags', 'author', 'ingredients', 'image', 'name', 'text', 'cooking_time'
    ]
    CHECK_FILED_TAGS = 'tags'

    id = serializers.IntegerField(required=False)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UsersSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(many=True)

    def check_ingredient(self, attrs):
        check_list_for_ingredient = []
        for c in attrs['ingredients']:
            if c['amount'] < 1:
                raise ValidationError(
                    message='Значение должно быть больше нуля',
                    code=400,
                )
            rule_for_ingredient = Ingredient.objects.filter(id=c['id']).exists()
            if not rule_for_ingredient:
                raise ValidationError(
                    message=f'Не существует ингредиент {c["id"]}',
                    code=400,
                )
            if c["id"] not in check_list_for_ingredient:
                check_list_for_ingredient.append(c['id'])
            else:
                raise ValidationError(
                    message=f'Вы указали два одинаковых ингредиента',
                    code=400,
                )
        return attrs

    def check_tags(self, attrs):
        rule_not_same_tags = len(
            attrs[self.CHECK_FILED_TAGS]) == len(
            set(attrs[self.CHECK_FILED_TAGS])
        )
        if not rule_not_same_tags:
            raise ValidationError(
                message=f'Повторяющие значения {self.CHECK_FILED_TAGS}',
                code=400,
            )
        return True

    def check_post_method(self, attrs):
        not_all_fields = len(self.FIELDS) != len(attrs.keys())
        empty_fields = all([bool(attrs['ingredients']), bool(attrs['tags'])])
        if not_all_fields:
            raise ValidationError(
                message='Поле не должно быть пустым',
                code=400
            )
        if not empty_fields:
            raise ValidationError(
                message='Поле не должно быть пустым',
                code=400,
            )
        self.check_tags(attrs)
        return self.check_ingredient(attrs)

    def check_patch_method(self, attrs):
        rule_empty_field_ingredient = 'ingredients' in attrs
        rule_empty_field_tags = 'tags' in attrs
        if not all([rule_empty_field_ingredient, rule_empty_field_tags]):
            raise ValidationError(
                message=f'Пустые поля ингредиент или таги',
                code=400,
            )
        empty_filds = all([bool(attrs['ingredients']), bool(attrs['tags'])])
        if not empty_filds:
            raise ValidationError(
                message=f'Пустые поля ингредиент или таги',
                code=400,
            )
        self.check_tags(attrs)
        return self.check_ingredient(attrs)

    def validate(self, attrs):
        if self.context["request"].method == 'POST':
            return self.check_post_method(attrs)
        return self.check_patch_method(attrs)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        recipe = Recipes.objects.create(**validated_data)
        ingred_list = []
        for ingredient_data in ingredients_data:
            rec_ig = RecipesIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient_data['id']),
                amount=ingredient_data['amount'],
            )
            ingred_list.append(rec_ig.pk)
        for tag in tags_data:
            RecipeTag.objects.create(
                recipe=recipe,
                tag=Tag.objects.get(pk=tag.pk),
            )

        recipe.tags.set(tags_data)
        recipe.ingredients.set(ingred_list)
        return recipe

    def get_is_favorited(self, obj):
        patch_meth_rule = self.context["request"].method == 'PATCH'
        if patch_meth_rule:
            return True
        user = self.context['request'].user
        recipe = obj
        FavoriteRecipe.objects.create(
            recipe=recipe,
            user=user,
            name=recipe.name,
            image=recipe.image,
            cooking_time=recipe.cooking_time
        )
        return FavoriteRecipe.objects.filter(user_id=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, obj):
        patch_meth_rule = self.context["request"].method == 'PATCH'
        if patch_meth_rule:
            return True
        user = self.context['request'].user
        recipe = obj
        ShoppingCart.objects.create(
            recipe=recipe,
            user=user,
            name=recipe.name,
            image=recipe.image,
            cooking_time=recipe.cooking_time
        )
        return ShoppingCart.objects.filter(user_id=user, recipe=recipe).exists()


class RecipesSerializer(RecipeMixinSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
    id = serializers.IntegerField(required=False)
    author = UsersSerializer(default=serializers.CurrentUserDefault())
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'name',
            'text',
            'cooking_time',
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
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']
