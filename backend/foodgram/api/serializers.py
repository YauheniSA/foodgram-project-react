import base64

from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer
from foodgram.settings import MIN_AMOUNT, MIN_COOKING_TIME
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag, TagRecipe)
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from users.models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов модели User."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.subscriber.filter(author=obj).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    """Переопределенный сериализатор djoser для создания пользователя."""

    username = serializers.CharField(
        validators=(
            UniqueValidator(queryset=User.objects.all()),
        ),
        required=True
    )
    email = serializers.CharField(
        validators=(
            UniqueValidator(queryset=User.objects.all()),
        ),
        required=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


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
    ingredients = IngredientRecipeSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.favorite.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.shopping_list.filter(recipe=obj).exists()
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipePostPatchSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredient_recipe')
    author = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'author',
                  'name', 'image', 'text', 'cooking_time')

    def to_representation(self, instance):
        serializer = RecipeGetSerializer(
            instance, context={'request': self.context.get('request')}
            )
        return serializer.data

    def validate(self, data):
        ingredients = data['ingredient_recipe']
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise serializers.ValidationError(
                    'Введите одинаковые игредиенты в одной строке'
                )
            if ingredient['amount'] < MIN_AMOUNT:
                raise serializers.ValidationError(
                    f'Укажите верно количество {ingredient["ingredient"]}'
                )
        if data['cooking_time'] < MIN_COOKING_TIME:
            raise serializers.ValidationError(
                    'Укажите верное время приготовления блюда'
                )
        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        new_recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            TagRecipe.objects.create(
                recipe=new_recipe, tag=tag
            )
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=ingredient['ingredient'], recipe=new_recipe,
                amount=ingredient['amount']
            )
        return new_recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for tag in tags:
            TagRecipe.objects.create(
                recipe=instance, tag=tag
            )
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=ingredient['ingredient'], recipe=instance,
                amount=ingredient['amount']
            )
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор с сокращенными полями для связных моделей."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'cooking_time')

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('user')
        if self.context.get('model') == 'favorite':
            if Favorite.objects.filter(
                recipe=recipe, user=user
            ).exists():
                raise serializers.ValidationError(
                    detail='Этот рецепт уже есть в избранном!',
                    code=status.HTTP_400_BAD_REQUEST
                )
        if self.context.get('model') == 'shopping_cart':
            if ShoppingList.objects.filter(
                recipe=recipe, user=user
            ).exists():
                raise serializers.ValidationError(
                    detail='Этот рецепт уже есть в списке покупок!',
                    code=status.HTTP_400_BAD_REQUEST
                )
        return data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для возвращения данных автора после подписки."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        user = self.context.get('user')
        if user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=user, author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = RecipeShortSerializer(queryset, many=True)
        return serializer.data

    def validate(self, data):
        author = self.instance
        subscriber = self.context.get('user')
        if Subscription.objects.filter(
            subscriber=subscriber, author=author
        ).exists():
            raise serializers.ValidationError(
                detail='Вы уже пописаны на этого автора',
                code=status.HTTP_400_BAD_REQUEST
            )
        if author == subscriber:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data
