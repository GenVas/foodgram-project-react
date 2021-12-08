from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

HELP_TEXT_FOR_USER_ACTIVE_FIELD = _(
    'Designates whether this user should be treated as active. '
    'Unselect this instead of deleting accounts.'
)


class UserRole:
    '''Class descibes possible roles of a user'''
    USER = "user"
    ADMIN = "admin"


ROLE_CHOICES = (
    (UserRole.USER, _("User")),
    (UserRole.ADMIN, _("Administrator")),
)


class User(AbstractUser):
    '''Custom Abstract user class'''

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
