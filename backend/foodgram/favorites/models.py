from django.db import models

from users.models import User
from recipes.models import Recipe


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


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
        help_text='Кто подписан'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='is_subscribed',
        verbose_name='На кого подписан',
        help_text='Имена авторов, на которых подписан'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.CheckConstraint(
                name='constraint_self_follow',
                check=~models.Q(subscriber=models.F('author'))
            ),
            models.UniqueConstraint(
                name='follower_and_folowwing_have_unique_relationships',
                fields=('subscriber', 'author')
            )
        )
