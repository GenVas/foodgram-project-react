from colorfield.fields import ColorField
from django.core import validators
from django.db import models

from .validators import slug_regex_validator


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="название",
        related_name="ingredients",
        blank=False, unique=True,

    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="единица измерения",
        related_name="ingredients",
        blank=False
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


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


class Recipe(models.Model):
    # https://docs.djangoproject.com/en/3.2/ref/models/fields/#recursive-relationships
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
        blank=False)
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

    class Meta:
        ordering = ['name']
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class Cart(models.Model):
    pass  # TODO


class Favorites(models.Model):
    pass  # TODO
