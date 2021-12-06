'''foodgram_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
'''
from django.conf.urls import url
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views
from django.urls import re_path
from djoser import views as django_views
from djoser.urls import authtoken


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
        views.list_my_followings,
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
    # path('', include('djoser.urls')),
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
