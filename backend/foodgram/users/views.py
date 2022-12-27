from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)


from users.models import User, Subscription
from users.serializers import UserSerializer, SubscribeSerializer

from recipes.views import PostDeleteViewSet


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
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeViewSet(PostDeleteViewSet):
    """Вьюсет для работы с моделью Subscribe."""

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('user_id'))
        if Subscription.objects.filter(
                subscriber=request.user, author_id=author.id).exists():
            return Response(
                {'errors': 'Вы уже пописаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.create(
            subscriber=request.user, author_id=author.id)
        serializer = SubscribeSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('user_id'))
        if Subscription.objects.filter(
                subscriber=request.user, author_id=author.id).exists():
            Subscription.objects.filter(
                subscriber=request.user, author_id=author).delete()
            return Response(
                {'message': 'Автор успешно удален из подписки'},
                status=status.HTTP_204_NO_CONTENT)
        return Response(
                {'errors': 'Подписки на этого автора не существует!'},
                status=status.HTTP_400_BAD_REQUEST)
