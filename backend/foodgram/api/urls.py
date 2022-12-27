from django.urls import include, path
from rest_framework import routers

from users.views import (CustomUserViewSet,
                         SubscribeViewSet)
from recipes.views import (TagViewSet,
                           IngredientViewSet,
                           RecipeViewSet,
                           FavoriteViewSet,
                           ShoppongCartViewSet)


app_name = 'api'
router = routers.DefaultRouter()

router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(r'', include(router.urls)),
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='favorite_create_delete'),
    path('users/<int:user_id>/subscribe/',
         SubscribeViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='subscribe_create_delete'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppongCartViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='shopping_cart_create_delete'),         
    path(r'auth/', include('djoser.urls.authtoken')),

]
