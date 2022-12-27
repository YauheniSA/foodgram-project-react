from django.contrib import admin

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            TagRecipe,
                            IngredientRecipe,
                            Favorite,
                            ShoppingList
)


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


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'author',
                    'name',
                    'text',
                    'cooking_time',
                    
)


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'tag',
                    'recipe',
    )

@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'ingredient',
                    'recipe',
                    'amount'
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'user',
                    'recipe',
    )

@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')