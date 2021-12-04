# from enum import unique
import re
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from django.utils.translation import \
    ugettext_lazy as _  # TODO: переделать в перевод

from .validators import slug_regex_validator

# from users.models import User

User = get_user_model()

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils.datetime_safe import datetime


CART_STRING_METHOD = _("User: {} has {} items in their cart")
CART_ENTRY_STRING_METHOD = _("This entry contains {} {}(s).")
FAVORITES_STRING_METHOD = _("Favorites for username '{}'")
INGREDIENT_RECIPE_STR = _("recipe name: {}, "
                          "ingredient: {}, "
                          "quantity:{} ({})")
CART_STRING_METHOD = _("Cart for {}")


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
        blank=False, unique=True
    )
    color = ColorField(
        verbose_name=_("HEX index of color"),
        blank=False, unique=True
    )  # https://pypi.org/project/django-colorfield/
    slug = models.SlugField(
        max_length=200,
        verbose_name=_("slug"),
        validators=[slug_regex_validator]
    )

    class Meta:
        ordering = ['name']
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name=_("Unit"),
        blank=False
    )

    class Meta:
        ordering = ['name']
        verbose_name = _("Ingredient")
        verbose_name_plural = _("Ingredients")

    def __str__(self):
        return self.name


class Recipe(models.Model):
    # https://docs.djangoproject.com/en/3.2/ref/models/fields/#recursive-relationships
    author = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        verbose_name=_('Author of recipe'),
        related_name="recipes",
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        verbose_name=_("Ingredients"),
        related_name="recipes"
        # related_name="recipes",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_("Tags"),
        # related_name="recipes",
        # on_delete=models.DO_NOTHING,
        blank=True
    )
    # https://gist.github.com/yprez/7704036
    image = models.ImageField(
        blank=False,
        verbose_name=_("Image"),
        )  # TODO code to base64 (see link)
    name = models.CharField(
        max_length=200,
        verbose_name=_("Recipe name"),
        blank=False,
        db_index=True
    )
    text = models.TextField(
        verbose_name=_("Recipe description"),
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_("Cooking time"),
        blank=False,
        validators=[validators.MinValueValidator(limit_value=1)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Publication date")
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = _("Recipe")
        verbose_name_plural = _("Recipes")

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("Quantity"),
        blank=False,
        validators=[validators.MinValueValidator(limit_value=0)]
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = _("Measured ingredient")
        verbose_name_plural = _("Measured ingredients")

    # https://stackoverflow.com/questions/31264108/manytomanyfield-not-returning-str-object
    def __str__(self):
        return INGREDIENT_RECIPE_STR.format(
            self.recipe.name, self.ingredient,
            self.quantity, self.ingredient.measurement_unit)


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="buyer",
    )
    count = models.PositiveIntegerField(default=0)

    recipe = models.ManyToManyField(
        Recipe,
        related_name="good",
    )
    creation_date = models.DateTimeField(
        verbose_name=_('creation date'),
        auto_now=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(
        verbose_name=_("Activity flag for cart"),
        default=True
    )
    is_ordered = models.BooleanField(default=False)

    class Meta:
        verbose_name = ('Cart')
        verbose_name_plural = ('Carts')
        ordering = ('-creation_date',)

    def __str__(self):
        return CART_STRING_METHOD.format(self.user.username)


class Following(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name="following",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow'),
        ]
        ordering = ['author']
        verbose_name = "Following"
        verbose_name_plural = "Followings"

    def __str__(self):
        return self.author.username


class Favorites(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="collector",
    )

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="watching",
    )

    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"

    def __str__(self):
        return FAVORITES_STRING_METHOD.format(self.user.username)


# https://stackoverflow.com/questions/48716346/django-cart-and-item-model-getting-quantity-to-update
# @receiver(post_save, sender=Cart_entry)
# def update_cart(sender, instance, **kwargs):
#     line_cost = instance.quantity * instance.product.cost
#     instance.cart.count += instance.quantity
#     instance.cart.updated = datetime.now()



