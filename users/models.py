# When you define a foreign key or many-to-many
# relations to the user model, you should specify the custom model
# using the AUTH_USER_MODEL setting. For example:
# from django.conf import settings
# from django.db import models

# class Article(models.Model):
#     author = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#     )

from django.contrib.auth.models import AbstractUser
from django.db import models

# from django.contrib.auth.validators import UnicodeUsernameValidator


class UserRole:
    USER = "user"
    # MODERATOR = "moderator"
    ADMIN = "admin"


ROLE_CHOICES = (
    (UserRole.USER, "пользователь"),
    # (UserRole.MODERATOR, "модератор"),
    (UserRole.ADMIN, "администратор"),
)


class User(AbstractUser):

    first_name = models.CharField(
        verbose_name="имя",
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name="фамилия",
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        verbose_name="адрес электронной почты",
        blank=True, unique=True,
        max_length=254,
    )

    role = models.CharField(
        verbose_name="роль",
        max_length=60,
        choices=ROLE_CHOICES,
        null=False,
        default=UserRole.USER,
    )

    is_active = models.BooleanField(
        ('active'),
        default=True,
        help_text=(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.username
