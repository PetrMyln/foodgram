from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from foodgram_backend.constant import LENGTH_TEXT, LENGTH_USERNAME
from foodgram_backend.validators import validate_username
from users.models import User

from djoser.serializers import UserSerializer



