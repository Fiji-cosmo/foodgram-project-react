from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag
from users.models import User


class IngredientFilter(filters.BaseFilterBackend):
    '''
    Фильтр для поиска ингредиента по начальным буквам. Регистронезависимый.
    '''
    allowed_fields = ('name',)

    def filter_queryset(self, request, queryset, view):
        if 'name' not in request.query_params:
            return queryset
        desired = request.query_params['name']
        return queryset.filter(name__istartswith=desired).order_by('name')


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_recipe__user=user)
        return queryset
