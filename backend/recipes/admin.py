from django.contrib import admin
from django.utils.translation import gettext as _
from . import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class RecipeIngredientInLine(admin.TabularInline):
    model = models.Recipe.ingredients.through
    extra = 1


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cooking_time',
        'author',
        'pub_date')
    inlines = (RecipeIngredientInLine,)


@admin.register(models.Cart)
class Cart(admin.ModelAdmin):
    list_display = ('user', 'updated')


admin.site.register(models.IngredientRecipe)
admin.site.register(models.Favorites)
admin.site.register(models.Following)
admin.site.register(models.Ingredient)
