from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from foodgram_backend.constant import (
    LENGTH_ROLE,
    LENGTH_SHOW_NAME,
    LENGTH_TEXT,
    LENGTH_USERNAME,
    PATH_TO_AVATAR,
)


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
        default=''
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:LENGTH_SHOW_NAME]

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.Role.ADMIN.value


class Follow(models.Model):
    user = models.ForeignKey(
        User, related_name='following',
        on_delete=models.CASCADE
    )
    follower = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'follower'),)
        ordering = ['-created_at']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.follower.username} подписан {self.user.username}"

    def clean(self):
        if self.user == self.follower:
            raise ValidationError("Нельзя подписаться на самого себя.")
        super().clean()
