from django.contrib import admin
from users.models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
    )
    list_filter = (
        'email',
        'username'
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'subscriber',
        'author')
    list_filter = (
        'subscriber',
        'author'
    )
