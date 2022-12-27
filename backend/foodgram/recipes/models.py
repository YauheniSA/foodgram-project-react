from django.db import models
from colorfield.fields import ColorField
from django.core.validators import MinValueValidator

from users.models import User
from foodgram.settings import MIN_COOKINGTIME


class Tag(models.Model):
    name = models.CharField(
        verbose_name='name',
        help_text='Название тега',
        unique=True,
        max_length=200
    )
    color = ColorField(
        default='#FF0000'
    )
    slug = models.CharField(
        verbose_name='slug',
        help_text='Уникальный слаг',
        unique=True,
        max_length=200
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='name',
        help_text='Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='measurement_unit',
        help_text='Единицы измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиент'
        constraints = (
            models.UniqueConstraint(
                name='name_and_measurement_unit_have_unique_relationships',
                fields=('name', 'measurement_unit')
            ),
        )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='name',
        help_text='Название рецепта',
        max_length=200,
    )

    image = models.ImageField(
        upload_to='recipes/images/',
        default=None
    )

    text = models.TextField(
        verbose_name='text',
        help_text='Описание рецепта',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(MIN_COOKINGTIME), ],
        verbose_name='cooking_time',
        help_text='Время приготовления, мин',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        verbose_name='tag',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipe',
        on_delete=models.CASCADE
    )


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ingredient',
        related_name='ingredient_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='recipe',
        related_name='ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='amount',
        help_text='Количество'
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='user',
        related_name='favorite',
        help_text='Кому понравился рецепт',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipe',
        related_name='is_favorited',
        help_text='Какой рецепт понравился',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                name='user_and_favorite_recipe_have_unique_relationships',
                fields=('user', 'recipe')
            ),
        )


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='user',
        related_name='shopping_list',
        help_text='Кто добавил рецепт в список',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipe',
        related_name='is_in_shopping_list',
        help_text='Рецепт в списке покупок',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = (
            models.UniqueConstraint(
                name='user_and_shopping_recipe_have_unique_relationships',
                fields=('user', 'recipe')
            ),
        )
