from rest_framework import mixins, viewsets, filters
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (Tag, Ingredient, IngredientRecipe,
                            Recipe)
from recipes.serializers import (TagSerializer,
                                 IngredientSerializer,
                                 RecipeGetSerializer,
                                 RecipePostPatchSerializer)

from recipes.permissions import IsAdminOwnerOrReadOnly
from recipes.filters import RecipeFilter


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
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
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeGetSerializer
        return RecipePostPatchSerializer

    def get_permissions(self):
        method = self.request.method
        if method == 'DELETE' or method == 'PATCH':
            self.permission_classes = [IsAdminOwnerOrReadOnly, ]
        return super().get_permissions()

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
