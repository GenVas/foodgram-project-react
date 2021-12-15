from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import models

EMPTY = _('Empty')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    empty_value_display = EMPTY
    search_fields = ('name', 'slug',)
    ordering = ('color',)


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    empty_value_display = EMPTY
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('measurement_unit',)


@admin.register(models.IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
    empty_value_display = EMPTY
    list_filter = ('ingredient',)
    ordering = ('ingredient',)
    search_fields = ('ingredient',)


class RecipeIngredientInLine(admin.TabularInline):
    model = models.Recipe.ingredients.through
    extra = 1


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'cooking_time',
        'author',
        'pub_date',
        )
    inlines = (RecipeIngredientInLine,)


@admin.register(models.Following)
class FollowingAdminrt(admin.ModelAdmin):
    list_display = ('user', 'author')
    empty_value_display = EMPTY
    list_filter = ('author',)
    ordering = ('user',)
    search_fields = ('user',)


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    empty_value_display = EMPTY
    list_filter = ('recipe',)
    ordering = ('user',)
    search_fields = ('user',)


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated')
