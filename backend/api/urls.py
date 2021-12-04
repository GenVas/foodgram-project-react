"""foodgram_project URL Configuration

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
"""
from django.conf.urls import url
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import include, path
from rest_framework import routers
from backend.api import views


router = routers.DefaultRouter()
router.register(r"tags", views.TagViewSet, basename="tags")
router.register(r"recipes", views.RecipeViewSet, basename="recipe")
router.register(r"ingredients", views.IngredientViewSet, basename="ingredients")
# router.register(r"user/subscriptions", views.FollowingListViewSet, basename="subscriptions")
# router.register(r"", views., basename="")

# authpatterns = [
#     url(r"^token/login/$", djoser_views.TokenCreateView.as_view(), name="login"),
#     url(r"^token/logout/$", djoser_views.TokenDestroyView.as_view(), name="logout"),
#     url(r"^users/$"", djoser_views.UserViewSet, name="change_password")
# ]

urlpatterns = [
    # path("auth/", include(authpatterns)),
    path(r"users/subscriptions/", views.list_my_followings, name="subscriptions"),
    path('users/<int:user_id>/subscribe/',
         views.ManageFollowingsViewSet.as_view(), name='subscribe'),
    path(r'recipes/<int:recipe_id>/favorite/',
         views.ManageFavoritesViewSet.as_view(), name='favorites'),
    path("", include('djoser.urls')),
    path("", include(router.urls)),
    # path('test/', views.MyView.as_view()),  # test url
]
