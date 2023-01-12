from django.contrib import admin
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag, TagRecipe)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    list_filter = (
        'measurement_unit',
    )
    search_fields = ('name',)


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'author',
                    'name',
                    'text',
                    'cooking_time',
                    'in_favorite')
    inlines = (TagRecipeInline, IngredientRecipeInline)

    list_filter = ('tags',)
    list_display_links = ('name',)
    search_fields = (
        'author__username',
        'author__email',
        'name'
    )

    def in_favorite(self, obj):
        return obj.is_favorited.count()

    in_favorite.short_description = 'Количество добавлений в избранное'


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'tag',
                    'recipe')
    list_filter = ('tag',)
    search_fields = (
        'recipe__author__username',
        'recipe__author__email',
        'recipe__name'
    )
    list_filter = (
        'recipe__tags',
    )


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'ingredient',
                    'recipe',
                    'amount')
    search_fields = (
        'ingredient__name',
        'recipe__name'
    )
    list_filter = (
        'recipe__tags',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name'
    )
    list_filter = (
        'recipe__tags',
    )


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name'
    )
    list_filter = (
        'recipe__tags',
    )
