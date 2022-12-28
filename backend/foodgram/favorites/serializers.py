from rest_framework import serializers

from users.models import User
from recipes.models import Recipe
from favorites.models import Subscription
from recipes.serializers import RecipeShortSerializer


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для возвращении данных автора после подписки."""

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            subscriber=self.context.get('user'), author=obj).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            queryset = Recipe.objects.filter(author=obj)[:int(recipes_limit)]
        else:
            queryset = Recipe.objects.filter(author=obj)
        serializer = RecipeShortSerializer(queryset, many=True)
        return serializer.data
