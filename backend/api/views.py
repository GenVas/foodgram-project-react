from api.serializers import (CreateRecipeSerializer, FollowingBaseSerializer,
                             IngredientSerializer, ManageCartSerializer,
                             ManageFavoriteSerializer, RecipeListSerializer,
                             SimpleFollowSerializer, SubscribersSerializer,
                             TagSerializer)
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import TokenCreateView, TokenDestroyView
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import Cart, Favorites, Following, Ingredient, Recipe, Tag
from rest_framework import (filters, pagination, permissions, status, views,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from users.models import User

from .filters import IngredientNameFilter, RecipeFilter
from .paginators import CustomPageNumberPaginator
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly

OBJECT_NOT_FOUND = _('Object not found')
SUCCESSFULLY_UNFOLLOWED = _(
    'You have successfully unfollowed user with ID: {}')
UNFOLLOW_USER = _('The user is unfollowed')
RECIPE_REMOVED_FROM_FAVORITES = _(
    'Recipe with ID {} successfully removed from your favorites'
)
RECIPE_REMOVED_FROM_CART = _(
    'Recipe with ID {} has been succefully deleted from from your cart'
)
END_OF_LIST = _('End of list')
DOWNLOAD_CART_PRINT_LINE = '{} ({}) - {} \n'
EMPTY_CART_LIST = _('Cart list is empty')


class UserViewSet(DjoserUserViewSet):
    '''Viewset amends standard djoser viewset in
    order to receive targeted response code 200 '''
    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(
                self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_200_OK)


class CustomTokenCreateView(TokenCreateView):
    '''Viewset amends standard djoser viewset
    in order to receive targeted response code 201'''

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )


class CustomTokenDestroyView(TokenDestroyView):
    '''Viewset amends standard djoser viewset
    in order to receive targeted response code 201'''

    def post(self, request):
        utils.logout_user(request)
        return Response(status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ModelViewSet):
    '''Viewset for Tags'''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    ordering_fields = ('name',)
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]


# example: http://127.0.0.1:8000/api/ingredients?search=бур
class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset for ingredirents'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny, ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name', ]
    pagination = LimitOffsetPagination
    filterset_class = IngredientNameFilter


class ListMyFollowingsViewSet(viewsets.ModelViewSet):
    '''Viewset for list of followings (subscriptions)'''
    serializer_class = SubscribersSerializer
    pagination_class = CustomPageNumberPaginator

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


# https://www.django-rest-framework.org/api-guide/views/
class ManageFollowingsViewSet(views.APIView):
    ''' Viewset for adding or removing following (subscriptions) for a user'''
    def get_queryset(self):
        return Following.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        return (
            FollowingBaseSerializer(*args, **kwargs) if
            self.request.method == 'GET' else
            SimpleFollowSerializer(*args, **kwargs)
        )

    def get(self, request, user_id):
        data = {'user': request.user.id,
                'author': user_id}
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
            'user': request.user.id,
            'author': user_id
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


class RecipeViewSet(viewsets.ModelViewSet):
    '''Viewset for viewing and managing Recipes'''
    filterset_class = RecipeFilter
    ordering_fields = ('name',)
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = CustomPageNumberPaginator  # TODO
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        return (
            RecipeListSerializer if self.action in ['list', 'retrieve'] else
            CreateRecipeSerializer
        )

    def get_queryset(self):
        """modified method works with query parameters"""
        queryset = super().get_queryset()
        if self.request.query_params.get('is_favorited') in [
            '1', 'true', 'True'
        ]:
            queryset = queryset.filter(watching__user=self.request.user)
        if self.request.query_params.get('is_in_shopping_cart') in [
            '1', 'true', 'True'
        ]:
            queryset = queryset.filter(goods__user=self.request.user)
        return queryset  # noqa


class ManageFavoritesViewSet(views.APIView):
    ''' Viewset for adding or removing recipes
    to/from Favorites for a user'''

    def get(self, request, recipe_id):
        data = {'user': request.user.id,
                'recipe': recipe_id}
        context = {'request': request}
        serializer = ManageFavoriteSerializer(
            data=data,
            context=context
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                serializer.data,
                status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, recipe_id):
        try:
            favorite_record = get_object_or_404(
                Favorites, user=request.user.id, recipe__id=recipe_id
            )
        except Exception as exception:
            return Response(
                {"errors": f'{exception}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'user': request.user.id,
            'recipe': recipe_id
        }
        context = {'request': request}
        serializer = ManageFavoriteSerializer(data=data, context=context)
        if serializer.is_valid(raise_exception=True):
            favorite_record.delete()
            return Response(
                RECIPE_REMOVED_FROM_FAVORITES.format(recipe_id),
                status.HTTP_204_NO_CONTENT
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ManageCartView(views.APIView):
    ''' Viewset for adding or removing recipes
    to/from Cart (purchase list) of a user'''

    def get(self, request, recipe_id):
        data = {
            'user': request.user.id,
            'recipe': recipe_id
        }
        context = {'request': request}
        serializer = ManageCartSerializer(data=data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                serializer.data,
                status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, recipe_id):
        user = request.user
        cart_recipe = get_object_or_404(
            Cart,
            user=user,
            recipe__id=recipe_id
        )
        data = {
            'user': request.user.id,
            'recipe': recipe_id
        }
        context = {'request': request}
        serializer = ManageFavoriteSerializer(data=data, context=context)
        if serializer.is_valid(raise_exception=True):
            cart_recipe.delete()
            return Response(
                RECIPE_REMOVED_FROM_CART.format(recipe_id),
                status.HTTP_204_NO_CONTENT
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class DownloadCartView(views.APIView):
    '''Viewset for downloading current user's cart content
    decomposed by ingredients in file in .pdf format
     '''
    def get(self, request):
        cart = request.user.cart_holder.all()
        download_list = {}
        for item in cart:
            ingredients = item.recipe.portioned.all()
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                amount = ingredient.amount
                unit = ingredient.ingredient.measurement_unit
                if name not in download_list:
                    download_list[name] = {
                        'amount': amount,
                        'unit': unit
                    }
                else:
                    download_list[name]['amount'] = (
                        download_list[name]['amount'] + amount
                    )
        output_list = []

        for item in download_list:
            output_list.append(
                DOWNLOAD_CART_PRINT_LINE.format(
                    item,
                    download_list[item]['unit'],
                    download_list[item]['amount']
                )
            )

        if len(output_list) == 0:
            output_list = EMPTY_CART_LIST

        response = HttpResponse(output_list,'Content-Type: application/pdf') # noqa
        response['Content-Disposition'] = "attachment; filename='cart.pdf'"
        return response
