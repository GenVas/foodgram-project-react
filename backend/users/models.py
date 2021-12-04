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
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from django.db import models


HELP_TEXT_FOR_USER_ACTIVE_FIELD = _(
    'Designates whether this user should be treated as active. '
    'Unselect this instead of deleting accounts.'
)


class UserRole:
    USER = "user"
    # MODERATOR = "moderator"
    ADMIN = "admin"


ROLE_CHOICES = (
    (UserRole.USER, _("User")),
    # (UserRole.MODERATOR, "модератор"),
    (UserRole.ADMIN, _("Administrator")),
)


class User(AbstractUser):

    username = models.CharField(
        verbose_name=_("Name"),
        max_length=150,
        blank=False,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name=_("Name"),
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name=_("Surname"),
        max_length=150,
        blank=False,
    )
    email = models.EmailField(
        verbose_name=_("Email address"),
        blank=False, unique=True,
        max_length=254,
    )
    role = models.CharField(
        verbose_name=_("Role"),
        max_length=60,
        choices=ROLE_CHOICES,
        null=False,
        default=UserRole.USER,
    )
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
        help_text=(HELP_TEXT_FOR_USER_ACTIVE_FIELD),
    )

    class Meta:
        ordering = ('username', )
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.username
