from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)


from users.models import User
from users.serializers import UserSerializer
from favorites.serializers import SubscribeSerializer


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с кастомной моделью User."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def create(self, serializer):
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request):
        context = {
            'user': request.user,
            'recipes_limit': request.query_params.get('recipes_limit')}

        queryset = User.objects.filter(
            is_subscribed__subscriber=self.request.user
        ).all()
        serializer = SubscribeSerializer(queryset, context=context, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
