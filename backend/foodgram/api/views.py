from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminOwnerOrReadOnly
from api.serializers import (IngredientSerializer, RecipeGetSerializer,
                             RecipePostPatchSerializer, RecipeShortSerializer,
                             SubscribeSerializer, TagSerializer,
                             UserSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscription, User

CONTENT_TYPE = 'text/plain'


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class PostDeleteViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    pass


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с кастомной моделью User."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def create(self, serializer):
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return None

    @action(
        methods=('get', ),
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticatedOrReadOnly, ),
    )
    def subscriptions(self, request):
        context = {
            'user': request.user,
            'recipes_limit': request.query_params.get('recipes_limit')}
        queryset = User.objects.filter(
            is_subscribed__subscriber=request.user
        )
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages, context=context, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ListRetrieveViewSet):
    """Вьюсет для получения списка и экземляра модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class IngredientViewSet(TagViewSet):
    """Вьюсет для получения списка и экземляра модели Ingredient"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeGetSerializer
        return RecipePostPatchSerializer

    def get_permissions(self):
        method = self.request.method
        if method == 'DELETE' or method == 'PATCH':
            self.permission_classes = (IsAdminOwnerOrReadOnly, )
        return super().get_permissions()

    @action(
        methods=('get', ),
        detail=False,
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__is_in_shopping_list__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_sum=Sum('amount'))
        data = []
        data.append('Список ингредиентов для покупки:')
        data.append('Ингредиент | количество  | ед.изм')

        for obj in ingredients:
            name = obj.get('ingredient__name')
            measurement = obj.get('ingredient__measurement_unit')
            amount = obj.get('ingredient_sum')
            data.append(f'{name} | {amount} | {measurement}')
        return HttpResponse("\r\n".join(data), content_type=CONTENT_TYPE)


class FavoriteViewSet(PostDeleteViewSet):
    """Вьюсет для создания и удаления экземпляра модели Favorite"""

    serializer_class = RecipeShortSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        context = {
            'user': request.user,
            'model': 'favorite'
        }
        serializer = RecipeShortSerializer(
            recipe, data=request.data, context=context
        )
        serializer.is_valid(raise_exception=True)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        obj = recipe.is_favorited.filter(user=request.user)
        if obj.exists():
            obj.delete()
            return Response(
                {'message': 'Рецепт успешно удален из избранного'},
                status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Такого рецепта нет в избранном!'},
            status=status.HTTP_400_BAD_REQUEST)


class ShoppongCartViewSet(FavoriteViewSet):
    serializer_class = RecipeShortSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        context = {
            'user': request.user,
            'model': 'shopping_cart'
        }
        serializer = RecipeShortSerializer(
            recipe, data=request.data, context=context
        )
        serializer.is_valid(raise_exception=True)
        ShoppingList.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        obj = recipe.is_in_shopping_list.filter(user=request.user)
        if obj.exists():
            obj.delete()
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
        context = {
            'user': request.user,
            'recipes_limit': request.query_params.get('recipes_limit')}
        serializer = SubscribeSerializer(
            author, data=request.data, context=context
        )
        serializer.is_valid(raise_exception=True)
        Subscription.objects.create(
            subscriber=request.user, author_id=author.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('user_id'))
        obj = author.is_subscribed.filter(subscriber=request.user)
        if obj.exists():
            obj.delete()
            return Response(
                {'message': 'Автор успешно удален из подписки'},
                status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Подписки на этого автора не существует!'},
            status=status.HTTP_400_BAD_REQUEST)
