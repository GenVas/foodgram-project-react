from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from recipes.models import Ingredient, IngredientRecipe
from rest_framework import serializers, status
from rest_framework.response import Response

ENTRY_DUPLICATION_MESSAGE = _(
    "{} with ID '{}' duplicates provided list of IDs"
)
NEGATIVE_VALUE_NOT_ALLOWED = _(
    'Negative values are not allowed'
)


def calculate_ingredients(ingredients, recipe):
    '''Method adds ingredients to the recipe'''
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


def custom_get_method(request, get_serializer, key, value):
    data = {'user': request.user.id,
            key: value}
    context = {'request': request}
    serializer = get_serializer(data=data, context=context)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        serializer.data,
        status.HTTP_201_CREATED
    )


def custom_delete_author_method(
            request, class_name,
            get_serializer,
            key, value, message
            ):
    try:
        follower = class_name.objects.get(
            user=request.user.id, author=value)
    except class_name.DoesNotExist as exception:
        return Response(
            {"errors": f'{exception}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    data = {
        'user': request.user.id,
        key: value
    }
    context = {'request': request}
    serializer = get_serializer(data=data, context=context)
    serializer.is_valid(raise_exception=True)
    follower.delete()
    return Response(
        message.format(value),
        status.HTTP_204_NO_CONTENT
    )


def custom_delete_recipe_method(
            request, class_name,
            get_serializer,
            key, value, message
            ):
    try:
        follower = class_name.objects.get(
            user=request.user.id, recipe=value)
    except class_name.DoesNotExist as exception:
        return Response(
            {"errors": f'{exception}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    data = {
        'user': request.user.id,
        key: value
    }
    context = {'request': request}
    serializer = get_serializer(data=data, context=context)
    serializer.is_valid(raise_exception=True)
    follower.delete()
    return Response(
        message.format(value),
        status.HTTP_204_NO_CONTENT
    )


def list_contains_unique_objects(ids_list, id):
    '''Function throughs validation error when
    a queryset contains duplicates
    '''
    if id in ids_list:
        raise serializers.ValidationError(
                ENTRY_DUPLICATION_MESSAGE.format('Ingredient', id)
                )
    ids_list.append(id)


def negative_value_constraint(value):
    '''Function throughs validation error
    against values <= 0
    '''
    if value <= 0:
        raise serializers.ValidationError(
                    NEGATIVE_VALUE_NOT_ALLOWED
                )
