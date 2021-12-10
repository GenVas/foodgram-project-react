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

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.request.query_params.get('is_favorited') in [
            '1', 'true', 'True'
        ]:
            queryset = queryset.filter(watching__user=self.request.user)
        if self.request.query_params.get('is_in_shopping_cart') in [
            '1', 'true', 'True'
        ]:
            queryset = queryset.filter(goods__user=self.request.user)
        return queryset  # noqa


class IngredientNameFilter(filters.FilterSet):
    "Filters ingredients againts name and measurement_unit"
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')
