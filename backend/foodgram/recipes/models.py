from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from foodgram.settings import MIN_AMOUNT, MIN_COOKING_TIME
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        help_text='Название тега',
        unique=True,
        max_length=200
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет'
    )
    slug = models.CharField(
        verbose_name='Слаг',
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
        verbose_name='Название ингредиента',
        help_text='Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
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
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        through='TagRecipe')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        unique=True,
        help_text='Название рецепта',
        max_length=200,
    )

    image = models.ImageField(
        upload_to='recipes/images/',
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(MIN_COOKING_TIME), ),
        verbose_name='Время приготовления, мин',
        help_text='Время приготовления, мин',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Тег  в рецепте'
        verbose_name_plural = 'Теги в рецептах'
        constraints = (
            models.UniqueConstraint(
                name='tag_and_recipe_unit_have_unique_relationships',
                fields=('tag', 'recipe')
            ),
        )

    def __str__(self) -> str:
        return f'Тег {self.tag} относится к рецепту {self.recipe}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Количество',
        validators=(MinValueValidator(MIN_AMOUNT), )

    )

    class Meta:
        verbose_name = 'Ингредиент  в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = (
            models.UniqueConstraint(
                name='ingredient_and_recipe_unit_have_unique_relationships',
                fields=('ingredient', 'recipe')
            ),
        )

    def __str__(self) -> str:
        return f'{self.recipe} влючает в себя {self.amount} {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorite',
        help_text='Кому понравился рецепт',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
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

    def __str__(self) -> str:
        return f'У {self.user} в избранном рецепт {self.recipe}.'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopping_list',
        help_text='Кто добавил рецепт в список',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
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

    def __str__(self) -> str:
        return f'У {self.user} в списке покупок рецепт {self.recipe}.'
