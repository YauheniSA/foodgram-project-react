from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserCreateSerializer

from users.models import User
# from recipes.serializers import RecipeShortSerializer


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user_subscribes = self.context['request'].user.subscriber
        return user_subscribes.filter(author=obj).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для возвращении данных автора после подписки."""

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    # recipes = RecipeShortSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user_subscribes = self.context['request'].user.subscriber
        return user_subscribes.filter(author=obj).exists()

    def get_recipes_count(self, obj):
        pass


class CustomUserCreateSerializer(UserCreateSerializer):
    """Переопределенный сериализатор djoser для создания пользователя."""

    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True
    )
    email = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True
    )

    def validate_username(self, name):
        if name.lower() == 'me':
            raise serializers.ValidationError('Username "me" is not valid')
        return name

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
