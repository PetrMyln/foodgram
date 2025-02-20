from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from foodgram_backend.constant import (
    LENGTH_ROLE,
    LENGTH_SHOW_NAME,
    LENGTH_TEXT,
    LENGTH_USERNAME,
    PATH_TO_AVATAR,
)

#from backend.foodgram_backend.constant import PATH_TO_AVATAR


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        max_length=LENGTH_USERNAME,
        unique=True,
        verbose_name='Username аккаунта',
        validators=(UnicodeUsernameValidator(),)
    )
    email = models.EmailField(
        max_length=LENGTH_TEXT,
        unique=True,
        verbose_name='Электронная почта',
        help_text='Укажите электронную почту'
    )
    role = models.CharField(
        max_length=LENGTH_ROLE,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль',
        help_text='Выберите роль пользователя'
    )
    avatar = models.ImageField(
        upload_to=PATH_TO_AVATAR,
        verbose_name='Аватар',
        null=True,
        default=None
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:LENGTH_SHOW_NAME]

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.Role.ADMIN.value


