from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Кастомная модель пользователя User"""

    email = models.EmailField(
        verbose_name='email',
        help_text='Адрес электронной почты',
        unique=True,
        max_length=254
    )
    username = models.CharField(
        verbose_name='username',
        help_text='Имя пользователя',
        unique=True,
        max_length=150
    )
    first_name = models.CharField(
        verbose_name='first_name',
        help_text='Имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='last_name',
        help_text='Фамилия',
        max_length=150
    )
    password = models.CharField(
        verbose_name='password',
        help_text='Пароль',
        max_length=150
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


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

    def __str__(self) -> str:
        return f'У {self.subscriber} подписан на {self.author}.'
