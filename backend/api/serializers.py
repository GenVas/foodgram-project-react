from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from djoser.serializers import TokenCreateSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Cart, Favorites, Following, Ingredient,
                            IngredientRecipe, Recipe, Tag)
from rest_framework import serializers
from users.models import User

from . import service_functions

POSITIVE_VALUE_REQUIRED = _('Value of ingredient must be positive')
UNABLE_TO_SIGN_FOR_YOURSELF = _('Unable to sign up for yourself')
ALREADY_SUBSCRIBED = _('You are already following this author')
RECIPE_IS_ALREADY_IN_FAVORITES = _('Recipe is already in favorites')
RECIPE_UNIQUE_CONSTRAINT_MESSAGE = _(
    'Author can not have multiple recipes '
    'with the same name and text desciption.'
    )
RECIPE_IS_ALREADY_IN_THE_SHOPPING_CART = _(
    'Recipe is already in your shopping cart'
)
ONLY_AUTHOR_CAN_DELETE_RECIPE = _(
    'Only author can delete the recipe'
)
NEGATIVE_VALUE_NOT_ALLOWED = _(
    r"Negative value for '{}' is not allowed"
)
TAG_ID_ALREADY_ASSIGNED = _(
    'Tag with ID {} was already assigned to this recipe with ID {}'
)
NO_INGREDIENT_IN_DATABASE = _(
    "There is no ingredient with ID '{}' in the database"
)


class CustomTokenCreateSerializer(TokenCreateSerializer):
    ''''Custom djoser Serializer for creating Token'''
    pass


class CustomUserCreateSerializer(UserCreateSerializer):
    'Custom djoser Serializer for adding new user'

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password'
        )
        read_only_fields = (
            'id',
        )


class UserSerializer(serializers.ModelSerializer):
    '''Nested serializer for RecipeListSerializer'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Following.objects.filter(user=request.user, author=obj).exists()


class PasswordSerializer(serializers.Serializer):
    '''Serializer for password change endpoint'''
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):
    '''Serializer for genres'''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''Serializer for ingerdients'''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class SimpleRecipeSerializer(serializers.ModelSerializer):
    ''' Nested serializer for SubscribersSerializer'''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


# Working with follow models: following and unfollowing users, dispalying
# list of subscriptions for authorized user


class SubscribersSerializer(serializers.ModelSerializer):
    ''''Nested serializer for FollowingBaseSerializer.
    It also serves ListMyFollowingsViewSet'''
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Following.objects.filter(user=obj, author=request.user).exists()

    def get_recipes(self, obj):
        '''Method field allows to set
        length of subset with query pamaneter through nested serializer'''
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()[
            :int(limit)
        ] if limit else obj.recipes.all()

        return SimpleRecipeSerializer(
            recipes, many=True, read_only=True,
        ).data


class SimpleFollowSerializer(serializers.ModelSerializer):
    '''Nested Serrializer that allows to unfollow user with DELETE
    through  ManageFollowingsViewSet'''
    class Meta:
        model = Following
        fields = ['user', 'author']


class FollowingBaseSerializer(serializers.ModelSerializer):
    '''Serrializer that allows to follow user with GET through
    ManageFollowingsViewSet'''

    class Meta:
        model = Following
        fields = '__all__'

    def validate(self, attrs):
        '''Repeats unqique contraint of the Following model'''
        request = self.context['request']
        if request.method == 'GET':
            if request.user == attrs['author']:
                raise serializers.ValidationError(
                    UNABLE_TO_SIGN_FOR_YOURSELF
                )
            if Following.objects.filter(
                    user=request.user,
                    author=attrs['author']
            ).exists():
                raise serializers.ValidationError(ALREADY_SUBSCRIBED)
        return attrs

    def to_representation(self, instance):
        return SubscribersSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class IngredientRecipeSerializer(serializers.ModelSerializer):
    '''Nested serializer for RecipeListSerializer that allows to configure
    ingredient fields'''
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeListSerializer(serializers.ModelSerializer):
    '''Serializer serves RecipeViewSet'''
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        ]

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorites.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Cart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    '''Service cerializer for FavoriteSerializer to_representation method'''
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    '''Service seriailizer for CreateRecipeSerializer field,
    allows to add one or more ingredients to a recipe'''
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    '''Serializer for creating, updating, and deleting recipes'''
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = AddIngredientToRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        ]
        read_only_fields = ['author']

    def validate(self, data):
        '''Repeats unqique constraint and assures that new recipe
        doesnt duplicate a record'''
        request = self.context['request']
        if request.method == 'POST' and Recipe.objects.filter(
                    author=request.user,
                    name=data['name'],
                    text=data['text']).exists():
            raise serializers.ValidationError(
                        RECIPE_UNIQUE_CONSTRAINT_MESSAGE
            )

        if (
            request.method == 'DELETE' and request.user != data[
                'recipe'].author):
            raise serializers.ValidationError(ONLY_AUTHOR_CAN_DELETE_RECIPE)
        return data

    def validate_tags(self, data):
        if self.context["request"].method in ['POST', 'PUT']:
            tags_ids = self.initial_data['tags']
            recipe_id = self.instance.id
            for tag in tags_ids:
                if Recipe.objects.filter(
                    id=self.instance.id,
                    tags__id=tag
                ).exists():
                    raise serializers.ValidationError(
                        TAG_ID_ALREADY_ASSIGNED.format(tag, recipe_id)
                    )
        return data

    def validate_ingredients(self, data):
        if self.context["request"].method in ['POST', 'PUT']:
            for ingredient in self.initial_data['ingredients']:
                try:
                    Ingredient.objects.get(id=ingredient['id'])
                except ObjectDoesNotExist:
                    raise serializers.ValidationError(
                        NO_INGREDIENT_IN_DATABASE.format(ingredient['id'])
                    )
                if ingredient['amount'] <= 0:
                    raise serializers.ValidationError(
                        NEGATIVE_VALUE_NOT_ALLOWED.format('ingredient')
                    )

        return data

    def create(self, validated_data):
        '''Method allows to create recipe amount
        of ingredients in one request'''
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        service_functions.calculate_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        '''Method allows to update recipe amount
        of ingredients in one request'''
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            service_functions.calculate_ingredients(ingredients, instance)
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        # updates other standard fields
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ManageFavoriteSerializer(serializers.ModelSerializer):
    '''Serializer for including or excluding recipes
    to/from favorites for authorized user'''
    class Meta:
        model = Favorites
        fields = '__all__'

    def validate(self, data):
        request = self.context['request']
        if (request.method == 'GET'
            and Favorites.objects.filter(
                user=request.user,
                recipe__id=data['recipe'].id).exists()):
            raise serializers.ValidationError(
                RECIPE_IS_ALREADY_IN_FAVORITES
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ManageCartSerializer(serializers.ModelSerializer):
    '''Serializer adds recipe to the shopping cart with GET request
    and deletes with DELETE request through ManageCartView'''
    class Meta:
        model = Cart
        fields = '__all__'

    def validate(self, data):
        request = self.context['request']
        if (request.method == 'GET'
            and Cart.objects.filter(
                user=request.user,
                recipe__id=data['recipe'].id).exists()):
            raise serializers.ValidationError(
                RECIPE_IS_ALREADY_IN_THE_SHOPPING_CART
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
