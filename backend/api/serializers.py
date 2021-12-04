from django.core.exceptions import ValidationError
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from backend.users.models import User
from backend.recipes.models import (
    Cart, Favorites, Following,
    Ingredient, IngredientRecipe, Recipe,
    Tag, )
from djoser.serializers import UserCreateSerializer
from djoser.constants import Messages
from django.utils.translation import gettext_lazy as _
# from rest_framework.views import exception_handler

POSITIVE_VALUE_REQUIRED = _('Value of ingredient must be positive')
UNABLE_TO_SIGN_FOR_YOURSELF = _('Unable to sign up for yourself')
ALREADY_SUBSCRIBED = _('You are already following this author')
RECIPE_IS_ALREADY_IN_FAVORITES = _('Recipe is already in favorites')


class CustomMessages(Messages):
    INVALID_CREDENTIALS_ERROR = _("Unable to log in with provided credentials.")
    INACTIVE_ACCOUNT_ERROR = _("User account is disabled.")
    INVALID_TOKEN_ERROR = _("Invalid token for given user.")
    INVALID_UID_ERROR = _("Invalid user id or user doesn't exist.")
    STALE_TOKEN_ERROR = _("Stale token for given user.")
    PASSWORD_MISMATCH_ERROR = _("The two password fields didn't match.")
    USERNAME_MISMATCH_ERROR = _("The two {0} fields didn't match.")
    INVALID_PASSWORD_ERROR = _("Invalid password.")
    EMAIL_NOT_FOUND = _("User with given email does not exist.")
    CANNOT_CREATE_USER_ERROR = _("Unable to create account.")


class CustomUserCreateSerializer(UserCreateSerializer):
    "Custom Serializer for adding new user"

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password'
        )
        read_only_fields = (
        'id',
        )


class UserSerializer(serializers.ModelSerializer):
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


class CustomUserSerializer(UserSerializer):
    "Custom Serializer for returning list of users"

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'password', 'first_name', 'last_name'
        )


class PasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for genres."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class SimpleRecipeSerializer(serializers.ModelSerializer):
    """ Service serializer for nested
        serialization - see SubscribersSerializer"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')





## Working with follow models: following and unfollowing users, dispalying
## list of subscriptions for authorized user

class SubscribersSerializer(serializers.ModelSerializer):
    """"This serializer is serving FollowingBaseSerializer below
    for dispalying fields in line with requested documentation"""
    recipes = SimpleRecipeSerializer(many=True, read_only=True)
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


class SimpleFollowSerializer(serializers.ModelSerializer):
    """Serrializer that allows to unfollow user with DELETE
    request from ManageFollowingsViewSet"""
    class Meta:
        model = Following
        fields = ["user", "author"]


class FollowingBaseSerializer(serializers.ModelSerializer):
    """Serrializer that allows to follow user with GET request
    from ManageFollowingsViewSet"""

    class Meta:
        model = Following
        fields = '__all__'

    def validate(self, attrs):
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


## Recipes: listing, crating and adding to favorites


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'name', 'measurement_unit', 'quantity']


class RecipeListSerializer(serializers.ModelSerializer):
    
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'is_favorited',
            # 'is_in_shopping_cart',
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

    # def get_is_in_shopping_cart(self, obj):
    #     request = self.context.get('request')
    #     if not request or request.user.is_anonymous:
    #         return False
    #     return PurchaseList.objects.filter(
    #         user=request.user,
    #         recipe=obj
    #     ).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    """Service cerializer for FavoriteSerializer to_representation method"""
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    """Service seriailizer for CreateRecipeSerializer field"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Serializer for creating, updating, and deleting recipes"""
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = AddIngredientToRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        for ingredient in ingredients:
            if ingredient['amount'] < 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть '
                    'отрицательным числом.'
                )
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            obj = get_object_or_404(Ingredient, id=ingredient['id'])
            amount = ingredient['amount']
            if IngredientRecipe.objects.filter(
                    recipe=recipe,
                    ingredient=obj
            ).exists():
                amount += F('amount')
            IngredientRecipe.objects.update_or_create(
                recipe=recipe,
                ingredient=obj,
                defaults={'amount': amount}
            )
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')

            for ingredient in ingredients:
                if ingredient['amount'] < 0:
                    raise serializers.ValidationError(
                        'Количество ингредиента не может быть '
                        'отрицательным числом.'
                    )
            instance.ingredients.clear()
            for ingredient in ingredients:
                obj = get_object_or_404(Ingredient,
                                        id=ingredient['id'])
                amount = ingredient['amount']
                if IngredientRecipe.objects.filter(
                        recipe=instance,
                        ingredient=obj
                ).exists():
                    amount += F('amount')
                IngredientRecipe.objects.update_or_create(
                    recipe=instance,
                    ingredient=obj,
                    defaults={'amount': amount}
                )
        if 'tags' in self.initial_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ManageFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for including or excluding recipes
    to/from favorites for authorized user"""
    class Meta:
        model = Favorites
        fields = '__all__'

    def validate(self, attrs):
        request = self.context['request']
        if (request.method == 'GET'
            and Favorites.objects.filter(
                user=request.user,
                recipe=attrs['recipe']).exists()):
            raise serializers.ValidationError(
                RECIPE_IS_ALREADY_IN_FAVORITES
            )
        return attrs

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
