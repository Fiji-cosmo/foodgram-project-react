from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Recipe


def post_and_delete(serializer_, model, request, recipe_id):
    """Опция добавления и удаления рецепта."""
    user = request.user
    data = {'user': user.id,
            'recipe': recipe_id}
    serializer = serializer_(data=data, context={'request': request})

    if request.method == 'POST':
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    get_object_or_404(
        model, user=user, recipe=get_object_or_404(Recipe, id=recipe_id)
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
