from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from favorites.models import Favorite, ShoppingList, Subscription
from users.models import User
from recipes.models import Recipe
from recipes.serializers import RecipeShortSerializer
from favorites.serializers import SubscribeSerializer


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class PostDeleteViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    pass


class FavoriteViewSet(PostDeleteViewSet):
    """Вьюсет для создания и удаления экземпляра модели Favorite"""

    serializer_class = RecipeShortSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        if Favorite.objects.filter(
                user=request.user, recipe_id=recipe).exists():
            return Response(
                {'errors': 'Этот рецепт уже был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(
                {'message': 'Рецепт успешно удален из избранного'},
                status=status.HTTP_204_NO_CONTENT)
        return Response(
                {'errors': 'Такого рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST)


class ShoppongCartViewSet(PostDeleteViewSet):
    serializer_class = RecipeShortSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        if ShoppingList.objects.filter(
                user=request.user, recipe_id=recipe).exists():
            return Response(
                {'errors': 'Этот рецепт уже был добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingList.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe,)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        if ShoppingList.objects.filter(
                user=request.user, recipe=recipe).exists():
            ShoppingList.objects.filter(
                user=request.user, recipe=recipe).delete()
            return Response(
                {'message': 'Рецепт успешно удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT)
        return Response(
                {'errors': 'Такого рецепта нет в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST)


class SubscribeViewSet(PostDeleteViewSet):
    """Вьюсет для работы с моделью Subscribe."""

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('user_id'))
        if Subscription.objects.filter(
                subscriber=request.user, author_id=author.id).exists():
            return Response(
                {'errors': 'Вы уже пописаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.create(
            subscriber=request.user, author_id=author.id)
        context = {
            'user': request.user,
            'recipes_limit': request.query_params.get('recipes_limit')}
        serializer = SubscribeSerializer(author, context=context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('user_id'))
        if Subscription.objects.filter(
                subscriber=request.user, author_id=author.id).exists():
            Subscription.objects.filter(
                subscriber=request.user, author_id=author).delete()
            return Response(
                {'message': 'Автор успешно удален из подписки'},
                status=status.HTTP_204_NO_CONTENT)
        return Response(
                {'errors': 'Подписки на этого автора не существует!'},
                status=status.HTTP_400_BAD_REQUEST)
