from urllib.parse import unquote
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.models import Subscribe, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteRecipeSerializer, IngredientSerializer, RecipeGETSerializer,
    RecipePOSTserializer, SetPasswordSerializer, ShopingCartRecipeSerializer,
    SubscriptionsGETSerializer, SubscriptionsPOSTSerializer, TagSerializer,
    UserGETSerializer, UserPOSTSerializer
)
from .utils import post_and_delete, download_txt


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return UserPOSTSerializer
        return UserGETSerializer

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserGETSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            {'detail': 'Пароль изменен.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPageNumberPagination
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsGETSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            serializer = SubscriptionsPOSTSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        get_object_or_404(Subscribe, user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (IngredientFilter,)

    def get_queryset(self):
        """Получает ингредиент в соответствии с параметрами запроса."""
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            if name[0] == '%':
                name = unquote(name)
            else:
                name = name.translatestr.maketrans(
                    'qwertyuiop[]asdfghjkl;\'zxcvbnm,./',
                    'йцукенгшщзхъфывапролджэячсмитьбю.'
                )
            name = name.lower()
            start_queryset = list(queryset.filter(name__istartswith=name))
            ingridients_set = set(start_queryset)
            cont_queryset = queryset.filter(name__icontains=name)
            start_queryset.extend(
                [ing for ing in cont_queryset if ing not in ingridients_set]
            )
            queryset = start_queryset
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeGETSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipePOSTserializer
        return RecipeGETSerializer

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return post_and_delete(
            FavoriteRecipeSerializer, FavoriteRecipe, request, pk
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        pagination_class=None
    )
    def shopping_cart(self, request, pk):
        return post_and_delete(
            ShopingCartRecipeSerializer, ShoppingCart, request, pk
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_list__user=self.request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(amount=Sum('amount'))
        return download_txt(self, request, ingredients)
