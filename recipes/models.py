from enum import unique
from colorfield.fields import ColorField
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _  # TODO: переделать в перевод
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.datetime_safe import datetime


from .validators import slug_regex_validator
from users.models import User

CART_STRING_METHOD = _("User: {} has {} items in their cart")


class Measurment_unit(models.Model):
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="единица измерения",
        related_name="units",
        blank=False,
        unique=True
    )

    class Meta:
        ordering = ['measurement_unit']
        verbose_name = "единица измерения"
        verbose_name_plural = "единицы измерения"

    def __str__(self):
        return self.measurement_unit


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="название",
        related_name="ingredients",
        blank=False, unique=True,
    )
    measurement_unit = models.ForeignKey(
        Measurment_unit,
        verbose_name="единица измерения",
        related_name="ingredients",
        blank=False
    )
    quantity = models.DecimalField(
        verbose_name="количество",
        related_name="ingredients",
        blank=False,
        validators=validators.MinValueValidator(limit_value=0)
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        unique_together = ["name", "measurement_unit"]

    def __str__(self):
        return self.name


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


class Recipe(models.Model):
    # https://docs.djangoproject.com/en/3.2/ref/models/fields/#recursive-relationships
    author = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        verbose_name='автор рецепта',
        related_name="recipes",
        blank=False)
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ингрединеты',
        related_name="recipes",
        on_delete=models.PROTECT, blank=False)
    tags = models.ForeignKey(
        Tag,
        verbose_name='тэги',
        related_name="recipes",
        on_delete=models.SET_NULL,
        blank=True)
    # https://gist.github.com/yprez/7704036
    image = models.ImageField(
        blank=False,
        verbose_name="фотография рецепта",
        )  # TODO code to base64 (see link)
    name = models.CharField(
        max_length=200,
        verbose_name="название рецепта",
        blank=False,
        db_index=True)
    text = models.TextField(
        verbose_name="описание рецепта",
        label="опишите подробно этапы, особенности приготовления",
        blank=False)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="время приготовления",
        label="Время приготовления в минутах",
        blank=False,
        validator=validators.MinValueValidator(limit_value=1)
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )

    class Meta:
        ordering = [-'pub_date']
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        unique_together = ["author", "name", "ingredients", "text"]

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="buyer",
    )
    count = models.PositiveIntegerField(default=0)
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="good",
    )
    creation_date = models.DateTimeField(verbose_name=_('creation date'))
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow'),
        ]

        verbose_name = ('корзина')
        verbose_name_plural = ('корзины')
        ordering = ('-creation_date',)
    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        CART_STRING_METHOD.format(self.user, self.count)


class Cart_entry(models.Model):
    recipe = models.ForeignKey(Recipe, null=True, on_delete='CASCADE')
    cart = models.ForeignKey(Cart, null=True, on_delete='CASCADE')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return "This entry contains {} {}(s).".format(self.quantity, self.recipe.name)

class Favorites(models.Model):
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


https://stackoverflow.com/questions/48716346/django-cart-and-item-model-getting-quantity-to-update 
# @receiver(post_save, sender=Cart_entry)
# def update_cart(sender, instance, **kwargs):
#     line_cost = instance.quantity * instance.product.cost
#     instance.cart.count += instance.quantity
#     instance.cart.updated = datetime.now()



# TODO: Создать менеджера (models.Manager) для обработка корзины в список из ингредиентов 
