from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .validators import SlugRegexValidator

User = get_user_model()


CART_STRING_METHOD = _('User: {} has {} items in their cart')
FAVORITES_STRING_METHOD = _("Favorites for username '{}'")
INGREDIENT_RECIPE_STR = _('recipe name: {}, '
                          'ingredient: {}, '
                          'amount:{} ({})')
TAGGED_RECIPE_STR = _('recipe name: {}, tag: {}, ')
CART_STRING_METHOD = _('Cart for {}')


class Tag(models.Model):
    '''Model for Tags'''
    name = models.CharField(
        max_length=200,
        verbose_name=_('Name'),
        blank=False, unique=True
    )
    color = ColorField(
        verbose_name=_('HEX index of color'),
        blank=False, unique=True
    )  # https://pypi.org/project/django-colorfield/
    slug = models.SlugField(
        max_length=200,
        verbose_name=_('slug'),
        validators=[SlugRegexValidator]
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Model for Ingredients'''
    name = models.CharField(
        max_length=200,
        verbose_name=_('Name'),
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name=_('Unit'),
        blank=False
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Model for Recipes'''
    author = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        verbose_name=_('Author of recipe'),
        related_name='recipes',
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name=_('Ingredients'),
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('Tags'),
        blank=True,
        related_name='recipes'
    )
    # https://gist.github.com/yprez/7704036
    image = models.ImageField(
        blank=False,
        verbose_name=_('Image'),
        )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Recipe name'),
        blank=False,
        db_index=True
    )
    text = models.TextField(
        verbose_name=_('Recipe description'),
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_('Cooking time'),
        blank=False,
        validators=[validators.MinValueValidator(limit_value=1)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Publication date')
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = _('Recipe')
        verbose_name_plural = _('Recipes')

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    '''Model for creating certain amounts (portions) of ingredients'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='portioned'
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name=_('amount'),
        blank=False,
        validators=[validators.MinValueValidator(limit_value=0)]
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = _('Measured ingredient')
        verbose_name_plural = _('Measured ingredients')

    def __str__(self):
        return INGREDIENT_RECIPE_STR.format(
            self.recipe.name, self.ingredient,
            self.amount, self.ingredient.measurement_unit)


class Cart(models.Model):
    '''Model for Carts (purchase lists)'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_holder',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='goods',
    )

    updated = models.DateTimeField(
        verbose_name=_('updated'), auto_now=True)
    active = models.BooleanField(
        verbose_name=_('Activity flag for cart'),
        default=True
    )

    class Meta:
        verbose_name = ('Cart')
        verbose_name_plural = ('Carts')
        ordering = ('-updated',)

    def __str__(self):
        return CART_STRING_METHOD.format(self.user.username)


class Following(models.Model):
    '''Model for followings (subscriptions)'''
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow'),
        ]
        ordering = ['author']
        verbose_name = 'Following'
        verbose_name_plural = 'Followings'

    def __str__(self):
        return self.author.username


class Favorites(models.Model):
    '''Model for Favorites'''
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='collector',
    )

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='watching',
    )

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return FAVORITES_STRING_METHOD.format(self.user.username)
