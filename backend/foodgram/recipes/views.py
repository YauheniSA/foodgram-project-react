from rest_framework import mixins, viewsets, filters, status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.db.models import Sum

from recipes.models import (Tag, Ingredient, IngredientRecipe,
                            Recipe, Favorite, ShoppingList)
from recipes.serializers import (TagSerializer,
                                 IngredientSerializer,
                                 RecipeGetSerializer,
                                 RecipeShortSerializer)


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class PostDeleteViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    pass


class TagViewSet(ListRetrieveViewSet):
    """Вьюсет для получения списка и экземляра модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = None


class IngredientViewSet(TagViewSet):
    """Вьюсет для получения списка и экземляра модели Ingredient"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAuthenticated,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer

    @action(
        methods=['get'],
        detail=False,
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__is_in_shopping_list__user=request.user
        ).values(
            'ingredient__name',  'ingredient__measurement_unit'
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
        # не работает перенос строки
        return Response("  ".join(data), content_type='text/plain')


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
        serializer = RecipeShortSerializer(recipe)
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
