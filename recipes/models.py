# from enum import unique
from colorfield.fields import ColorField
from django.core import validators
from django.db import models
from django.utils.translation import \
    ugettext_lazy as _  # TODO: переделать в перевод

# from users.models import User

from django.contrib.auth import get_user_model

User = get_user_model()

from .validators import slug_regex_validator

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils.datetime_safe import datetime


CART_STRING_METHOD = _("User: {} has {} items in their cart")
CART_ENTRY_STRING_METHOD = _("This entry contains {} {}(s).")


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="название",
        blank=False, unique=True
    )
    color = ColorField(
        verbose_name="HEX индекс цвета",
        blank=False, unique=True
    )  # https://pypi.org/project/django-colorfield/
    slug = models.SlugField(
        max_length=200,
        verbose_name='название-метка (слаг)',
        validators=[slug_regex_validator]
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="название",
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="единица измерения",
        blank=False
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    # https://docs.djangoproject.com/en/3.2/ref/models/fields/#recursive-relationships
    author = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        verbose_name='автор рецепта',
        # related_name="recipes",
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        verbose_name='ингрединеты',
        # related_name="recipes",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='тэги',
        # related_name="recipes",
        # on_delete=models.DO_NOTHING,
        blank=True
    )
    # https://gist.github.com/yprez/7704036
    image = models.ImageField(
        blank=False,
        verbose_name="фотография рецепта",
        )  # TODO code to base64 (see link)
    name = models.CharField(
        max_length=200,
        verbose_name="название рецепта",
        blank=False,
        db_index=True
    )
    text = models.TextField(
        verbose_name="описание рецепта",
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="время приготовления",
        blank=False,
        validators=[validators.MinValueValidator(limit_value=1)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="количество",
        blank=False,
        validators=[validators.MinValueValidator(limit_value=0)]
    )


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="buyer",
    )
    count = models.PositiveIntegerField(default=0)

    recipe = models.ManyToManyField(
        Recipe,
        # on_delete=models.CASCADE,
        related_name="good",
    )
    creation_date = models.DateTimeField(
        verbose_name=_('creation date'),
        auto_now=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(
        verbose_name="флаг активности корзины",
        default=True
    )
    is_ordered = models.BooleanField(default=False)

    class Meta:
        verbose_name = ('Корзина')
        verbose_name_plural = ('Корзины')
        ordering = ('-creation_date',)



# class Cart_entry(models.Model):
#     recipe = models.ForeignKey(Recipe, null=True, on_delete=models.CASCADE)
#     cart = models.ForeignKey(Cart, null=True, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()

#     def __str__(self):
#         return CART_ENTRY_STRING_METHOD.format(self.quantity, self.recipe.name)


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
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return self.author


class Favorites(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="collector",
    )

    recipe = models.ForeignKey(
        Recipe, on_delete=models.DO_NOTHING,
        related_name="watching",
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return self.recipe
# https://stackoverflow.com/questions/48716346/django-cart-and-item-model-getting-quantity-to-update
# @receiver(post_save, sender=Cart_entry)
# def update_cart(sender, instance, **kwargs):
#     line_cost = instance.quantity * instance.product.cost
#     instance.cart.count += instance.quantity
#     instance.cart.updated = datetime.now()


# TODO: Создать менеджера (models.Manager)
# для обработка корзины в список из ингредиентов

# pip install django-SHOP
# from shop.models.cart import CartManager, CartItemManager
