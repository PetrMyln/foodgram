from django.core.exceptions import ValidationError

from foodgram_backend.constant import USERNAME_RESTRICTION


def validate_username(value):
    if not isinstance(value, str):
        raise ValidationError(
            'username должен иметь тип str'
        )
    if value == USERNAME_RESTRICTION:
        raise ValidationError(
            f'username не может быть "{value}"'
        )
    return value
