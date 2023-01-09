from django.contrib import admin

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            TagRecipe,
                            IngredientRecipe,
                            Favorite,
                            ShoppingList)


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
        'name',
    )


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

    def in_favorite(self, obj):
        return obj.is_favorited.count()

    in_favorite.short_description = 'Количество добавлений в избранное'


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'tag',
                    'recipe')
    list_filter = (
        'tag',
        'recipe')


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'ingredient',
                    'recipe',
                    'amount')
    list_filter = (
        'ingredient',
        'recipe'
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_filter = (
        'user',
        'recipe'
    )


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_filter = (
        'user',
        'recipe'
    )
