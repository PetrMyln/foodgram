import base64

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from foodgram_backend.constant import LENGTH_TEXT, LENGTH_USERNAME
from foodgram_backend.validators import validate_username
from recipes.models import Recipes
from users.models import User, Follow


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            form, imgstr = data.split(';base64,')
            ext = form.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
        return super().to_internal_value(data)


class AuthSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=LENGTH_TEXT
    )
    id = serializers.IntegerField
    username = serializers.CharField(
        required=True,
        max_length=LENGTH_USERNAME,
        validators=(
            validate_username,
            UnicodeUsernameValidator()
        )
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate(self, data):

        username = data.get('username')
        email = data.get('email')
        rule_username = User.objects.filter(username=username).exists()
        rule_email = User.objects.filter(email=email).exists()

        if len(data.get('first_name')) > LENGTH_USERNAME:
            raise serializers.ValidationError(
                f"Имя не должен превышать {LENGTH_USERNAME} символов"
            )
        if len(data.get('last_name')) > LENGTH_USERNAME:
            raise serializers.ValidationError(
                f"Фамилия не должна превышать {LENGTH_USERNAME} символов"
            )
        if rule_email is True and rule_username is True:
            raise serializers.ValidationError(
                {'Ошибка':
                     f'Проверьте {email} и '
                     f'{username} уже используются!'})
        if rule_email:
            raise serializers.ValidationError(
                {'Ошибка': f'Проверьте '
                           f'{email} уже используется!'})
        if rule_username:
            raise serializers.ValidationError(
                {f'Ошибка': f'Проверьте '
                            f'{username} уже используется!'})
        return data

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=make_password(validated_data.get('password')),
        )
        return user


class UsersSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',

        )

    def get_is_subscribed(self, obj):
        user = obj.pk
        rule = (
                self.context.get('subscriber') is None
                and self.context.get('request') is None
        )
        if rule:
            return False
        if self.context.get('subscriber'):
            follower = self.context['subscriber']
            return Follow.objects.filter(user_id=user, follower_id=follower).exists()
        if self.context.get('request') is not None:
            follower = self.context['request'].user.pk
        return Follow.objects.filter(user_id=user, follower_id=follower).exists()


class RecipeForSubcriber(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')







class SubscribeSerializer(UsersSerializer):
    recipes = RecipeForSubcriber(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()


    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )



    def to_representation(self, instance):
        representation = super().to_representation(instance)
        rule = 'post' in self.context.keys()
        if rule:
            if self.context['post'] is None:
                return representation
            cnt_recipes = int(self.context['post'][1])
            representation['recipes'] = representation['recipes'][:cnt_recipes]
            return representation
        recipe_limit = list(self.context.get('request').query_params.items())
        if recipe_limit and recipe_limit[0][0]=='recipes_limit':
            cnt_recipes = int(recipe_limit[0][1])
            representation['recipes'] = representation['recipes'][:cnt_recipes]
            return representation
        return representation


class FollowSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(
        read_only=True,
        source='user')
    follower = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Follow
        fields = ('username', 'follower', 'created_at')
