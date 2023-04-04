from django.contrib import admin

from .models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)

EMPTY_VALUE_DISPLAY = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'slug',)
    ordering = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name',)
    ordering = ('pk',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'author', 'count_favorites', 'cooking_time', 'get_tags'
    )
    readonly_fields = ('count_favorites',)
    list_filter = ('name', 'tags',)
    search_fields = ('name', 'cooking_time', 'author__email')
    ordering = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        return ', '.join(_.name for _ in obj.tags.all())
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Кол-во в избранных')
    def count_favorites(self, obj):
        return obj.favorite_recipe.count()


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_filter = ('user', 'recipe',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class ShoppingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    empty_value_display = EMPTY_VALUE_DISPLAY


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(FavoriteRecipe, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingAdmin)
