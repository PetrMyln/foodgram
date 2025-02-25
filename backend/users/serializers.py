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
from users.models import User, Follow


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
        return super().to_internal_value(data)


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=LENGTH_TEXT
    )
    id = serializers.IntegerField(required=False)
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
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'email',
            'first_name',
            'last_name',
        )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        rule_username = User.objects.filter(username=username).exists()
        rule_email = User.objects.filter(email=email).exists()
        if rule_email is True and rule_username is True:
            raise serializers.ValidationError(
                {'Ошибка': f'Проверьте {email} и {username} уже используются!'})
        if rule_email:
            raise serializers.ValidationError(
                {'Ошибка': f'Проверьте {email} уже используется!'})
        if rule_username:
            raise serializers.ValidationError(
                {f'Ошибка': f'Проверьте {username} уже используется!'})
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


class TokenSerializer(serializers.Serializer):
    password = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data):
        user = get_object_or_404(
            User, email=data.get('email'),
        )
        rule_password_user = check_password(data.get('password'), user.password)
        if rule_password_user:
            return user
        return Response(status=status.HTTP_403_FORBIDDEN)


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',

        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = obj.pk
        if self.context.get('subscriber'):
            follower = self.context['subscriber']
        if self.context.get('request') is not None:
            follower = self.context['request'].user.pk
        return Follow.objects.filter(user_id=user, follower_id=follower).exists()



class SetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'new_password',
            'current_password',
        )

class FollowSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(
        read_only=True,
        source='user')
    follower = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Follow
        fields = ('username', 'follower', 'created_at')



