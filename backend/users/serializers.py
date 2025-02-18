from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from foodgram_backend.constant import LENGTH_TEXT, LENGTH_USERNAME
from foodgram_backend.validators import validate_username
from users.models import User


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
    password = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'email',
            'first_name',
            'last_name',
            'password',
        )


    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        rule_username = User.objects.filter(username=username).exists()
        rule_email = User.objects.filter(email=email).exists()
        if (rule_email and rule_username) or (not rule_email
                                              and not rule_username):
            return data
        ans_error = (email, username)[rule_username]
        raise serializers.ValidationError(
            f'Проверьте {ans_error} уже используется!')

    def create(self, validated_data):
        print(validated_data)
        user, _ = User.objects.get_or_create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password'),
        )
        return user




class TokenSerializer(serializers.Serializer):
    password = serializers.CharField()
    email = serializers.EmailField()


    def validate(self, data):
        #print(data.get('password'))
        user = get_object_or_404(
            User, email=data.get('email'))
        print(user.password)
        return user





class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'email',
            'role',
            'first_name',
            'last_name',
            #'password',
            #'avatar',
        )
        extra_kwargs = {'password': {'write_only': True}}

