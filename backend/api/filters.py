import django_filters as filters
from recipes.models import Ingredient, Recipe
from users.models import User


class RecipeFilter(filters.FilterSet):
    "Filters recipes againts tags and author"
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class IngredientNameFilter(filters.FilterSet):
    "Filters ingredients againts name and measurement_unit"
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


def filter_recipe_queryset(request, queryset):
    """Modified method works with query parameters"""

    if request.query_params.get('is_favorited') in [
        '1', 'true', 'True'
    ]:
        queryset = queryset.filter(watching__user=request.user)
    if request.query_params.get('is_in_shopping_cart') in [
        '1', 'true', 'True'
    ]:
        queryset = queryset.filter(goods__user=request.user)
    return queryset  # noqa
