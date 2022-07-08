from socket import socket

from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    PatchModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DeleteModelMixin,
)

from channels.db import database_sync_to_async
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin

from friend_app.api.serializer.friends import FriendsSerializer, UpdateFriendsSerializer, UserSerializer
from friend_app.models import Friends


class UserConsumer(
    ListModelMixin,
    RetrieveModelMixin,
    PatchModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DeleteModelMixin,
    GenericAsyncAPIConsumer,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FriendsConsumer(
    ListModelMixin,
    DeleteModelMixin,
    ObserverModelInstanceMixin,
    GenericAsyncAPIConsumer,
):
    queryset = Friends.objects.all()
    serializer_class = FriendsSerializer
    lookup_field = "pk"

    @action()
    async def connekt_user(self, **kwargs):
        token_key = self.scope["query_string"].decode()[6:]
        return await database_sync_to_async(User.objects.get)(
            auth_token=token_key
        )


    @action()
    async def create(self, pk, **kwargs):
        user = await self.connekt_user()
        friend = await database_sync_to_async(User.objects.get)(
            pk=pk
        )
        await database_sync_to_async(Friends.objects.create)(
            user=user,
            friend=friend
        )

    @action()
    async def update(self, pk, **kwargs):
        user = await self.connekt_user()
        await self.update_friend(pk, user)

    @database_sync_to_async
    def update_friend(self, pk, user):

        return Friends.objects.filter(pk=pk).update(user=user, confirmation=True)


class UpdateFriendsConsumer(
    UpdateModelMixin,
    GenericAsyncAPIConsumer,
):
    queryset = Friends.objects.all()
    serializer_class = UpdateFriendsSerializer
