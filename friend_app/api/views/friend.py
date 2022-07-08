from django.db.models import Q
from rest_framework import permissions
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from ...api.serializer.friends import FriendsSerializer, UpdateFriendsSerializer, UserSerializer
from ...models import Friends

from django.contrib.auth.models import User


class FriendsView(GenericViewSet, ListModelMixin, CreateModelMixin, DestroyModelMixin):
    """ Добавление пользователя (id) в друзья, удаление из друзей"""
    serializer_class = FriendsSerializer
    queryset = Friends.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class UpdateFriendsView(GenericViewSet, UpdateModelMixin):
    """ Изменения статуса приема в друзья """

    serializer_class = UpdateFriendsSerializer
    queryset = Friends.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(Q(user=self.request.user) | Q(friend=self.request.user))


class UserView(GenericViewSet, UpdateModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin):
    """ Изменения статуса приема в друзья """

    serializer_class = UserSerializer
    queryset = User.objects.all()
