from smtplib import SMTPException
from django.db.models import query
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from django.db.models.query import QuerySet
from drf_extra_fields.fields import Base64ImageField
from django.http import HttpResponse
# from django.views import View
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.http import response as response_http
from rest_framework import permissions, viewsets, pagination
from rest_framework.pagination import PageNumberPagination
from rest_framework import (filters, generics, mixins, pagination, permissions,
                            response, status, views, viewsets)
from rest_framework.decorators import action, api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from backend.api import serializers
from backend.api.serializers import (
    CreateRecipeSerializer,
    SubscribersSerializer,
    ManageFavoriteSerializer,
    TagSerializer,
    IngredientSerializer,
    FollowingBaseSerializer,
    SimpleFollowSerializer,
    RecipeListSerializer
    )
from django.utils.translation import ugettext_lazy as _

from backend.recipes.models import IngredientRecipe, Favorites, Following, Recipe, Tag, Ingredient
from backend.users.models import User
from backend.api.permissions import IsAdmin
from backend.api.paginators import CustomPageNumberPaginator
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.pagination import LimitOffsetPagination

OBJECT_NOT_FOUND = _("Object not found")
SUCCESSFULLY_UNFOLLOWED = _("You have successfully unfollowed user with ID: {}")
UNFOLLOW_USER = _("The user is unfollowed")
RECIPE_REMOVED_FROM_FAVORITES = _("Recipe with ID {} successfully removed from favorites")


class UserViewSet(DjoserUserViewSet):
    pass


# class MyView(View):
    # def get(self, request, *args, **kwargs):
    #     return HttpResponse('Hello, World!')


class TagViewSet(viewsets.ModelViewSet):
    "Viewset for Tags"

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    ordering_fields = ("name",)
    # filterset_class = TagFilter  # TODO
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [IsAdmin]


# example: http://127.0.0.1:8000/api/ingredients?search=бур
class IngredientViewSet(viewsets.ReadOnlyModelViewSet):  # TODO changes only for Admin
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny, ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name', ]
    pagination = LimitOffsetPagination


@api_view(['get'])
def list_my_followings(request):
    followed_users = User.objects.filter(following__user=request.user)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(followed_users, request)
    serializer = SubscribersSerializer(
        result_page,
        many=True,
        context={'current_user': request.user}
    )
    return paginator.get_paginated_response(serializer.data)



# https://www.django-rest-framework.org/api-guide/views/
class ManageFollowingsViewSet(views.APIView):
    """ Viewset for adding or removing subscriptions for a user"""
    def get_queryset(self):
        followings = Following.objects.all()
        return followings

    def get_serializer_class(self, *args, **kwargs):
        return (FollowingBaseSerializer(*args, **kwargs) if self.request.method == "GET" else
                SimpleFollowSerializer(*args, **kwargs))

    def get(self, request, user_id):
        data = {"user": request.user.id,
                "author": user_id}
        context = {'request': request}
        serializer = self.get_serializer_class(
            data=data,
            context=context
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        following_record = get_object_or_404(
            Following, user=request.user.id, author=user_id
        )
        data = {
            "user": request.user.id,
            "author": user_id
        }
        context = {'request': request}
        serializer = self.get_serializer_class(data=data, context=context)
        if serializer.is_valid(raise_exception=True):
            following_record.delete()
            return Response(
                SUCCESSFULLY_UNFOLLOWED.format(user_id),
                status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageFollowingsViewSet(views.APIView):
    """ Viewset for adding or removing subscriptions for a user"""
    def get_queryset(self):
        return Following.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        return (FollowingBaseSerializer(*args, **kwargs) if self.request.method == "GET" else
                SimpleFollowSerializer(*args, **kwargs))

    def get(self, request, user_id):
        data = {"user": request.user.id,
                "author": user_id}
        context = {'request': request}
        serializer = self.get_serializer_class(
            data=data,
            context=context
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        following_record = get_object_or_404(
            Following, user=request.user.id, author=user_id
        )
        data = {
            "user": request.user.id,
            "author": user_id
        }
        context = {'request': request}
        serializer = self.get_serializer_class(data=data, context=context)
        if serializer.is_valid(raise_exception=True):
            following_record.delete()
            return Response(
                SUCCESSFULLY_UNFOLLOWED.format(user_id),
                status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


## Working with recipes: listing, adding recipes, managing favorites for recipes
class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for viewing and managing Recipes"""

    queryset = Recipe.objects.all()
    ordering_fields = ("name",)
    # filterset_class = RecipeFilter # TODO
    # permission_classes = [AuthorOrReadOnly]  # TODO
    pagination_class = CustomPageNumberPaginator
    pagination_class = pagination.LimitOffsetPagination
    # permission_classes = [IsAdmin] # TODO

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        return (
            RecipeListSerializer if self.action in ['list', 'retrieve'] else
            CreateRecipeSerializer
        )


## Managing user's list of favorites for recipes
class ManageFavoritesViewSet(views.APIView):
    """ Viewset for adding or removing recipes to/from Favorites for a user"""

    def get(self, request, recipe_id):
        data = {"user": request.user.id,
                "recipe": recipe_id}
        context = {'request': request}
        serializer = ManageFavoriteSerializer(
            data=data,
            context=context
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        favorite_record = get_object_or_404(
            Favorites, user=request.user.id, recipe__id=recipe_id
        )
        data = {
            "user": request.user.id,
            "recipe": recipe_id
        }
        context = {'request': request}
        serializer = ManageFavoriteSerializer(data=data, context=context)
        if serializer.is_valid(raise_exception=True):
            favorite_record.delete()
            return Response(
                RECIPE_REMOVED_FROM_FAVORITES.format(recipe_id),
                status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


