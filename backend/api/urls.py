from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(
    "users",
    views.UserViewSet
)
router.register(
    r'tags',
    views.TagViewSet,
    basename='tags')
router.register(
    r'recipes',
    views.RecipeViewSet,
    basename='recipe')
router.register(
    r'ingredients',
    views.IngredientViewSet,
    basename='ingredients')

urlpatterns = [
    path(
        r'users/subscriptions/',
        views.ListMyFollowingsViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path(
        r'users/<int:user_id>/subscribe/',
        views.ManageFollowingsViewSet.as_view(),
        name='subscribe'
    ),
    path(
        r'recipes/<int:recipe_id>/favorite/',
        views.ManageFavoritesViewSet.as_view(),
        name='favorites'
    ),
    path(
        r'recipes/<int:recipe_id>/shopping_cart/',
        views.ManageCartView.as_view(),
        name='carts'
    ),
    path(
        r'recipes/download_shopping_cart/',
        views.DownloadCartView.as_view(),
        name='carts'
    ),  # amends basic djoser views
    path(
        r'auth/token/login/',
        views.CustomTokenCreateView.as_view(),
        name="login"
    ),  # amends basic djoser views
    path(
        r'auth/token/logout/',
        views.CustomTokenDestroyView.as_view(),
        name="logout"
    ),  # amends basic djoser views
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
