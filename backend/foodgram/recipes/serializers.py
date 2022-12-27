from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, IngredientRecipe
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с моделью Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с моделью Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с M2M моделью IngredientRecipe."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user_favotited = self.context['request'].user.favorite
        return user_favotited.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user_shopping_cart = self.context['request'].user.shopping_list
        return user_shopping_cart.filter(recipe=obj).exists()


class RecipePostPatchSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(many=True)

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')

        new_recipe = Recipe.objects.create(validated_data)
        new_recipe.tags.set(tags)
        new_recipe.ingredients.set(ingredients)

    def update(self, instance, validated_data):
        pass


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор с сокращенными полями для связных моделей."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
