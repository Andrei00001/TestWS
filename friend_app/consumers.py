import json

import self as self
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User
from djangochannelsrestframework.decorators import action

from friend_app.models import Room, Message, Friends


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.add_user_to_room()

        await self.send_json({
            'message': f'You have connected to the chat as {self.user.username}!',
            "user": self.user.username
        })
        await self.print_story(await self.story_messages_to_room())

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Receive message from WebSocket

    async def receive(self, *args, **kwargs):
        text_data_json = json.loads(kwargs["text_data"])
        if 'message' in text_data_json:
            message = text_data_json['message']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.user.username,
                }
            )
        elif 'friend' in text_data_json:
            friend = text_data_json['friend']
            await self.friendship_created(friend, self.user.username)

        elif 'username' in text_data_json:
            username = text_data_json['username']
            await self.confirmation_user(username, self.user.username)

        elif 'user_del' in text_data_json:
            user_del = text_data_json['user_del']
            await self.del_user_friend(user_del, self.user.username)
        # Send message to room group

        # Receive message from room group

    async def friendship_created(self, event, user):
        friend = event
        friend_user = await self.add_friend(friend)
        if friend_user:
            await self.send_json({
                'message': f'User {user} add in friend {friend}',
            })
        else:
            await self.send_json({
                "message": f"Dont username {friend}"
            })

        # Send a message to WebSocket

    async def confirmation_user(self, event, user):
        username = event
        await self.update_friend(username)
        await self.send_json({
            "message": f"{user} add confirmation {username}"
        })

    @database_sync_to_async
    def update_friend(self, username):
        return Friends.objects.filter(user__username=username).update(confirmation=True)

    async def del_user_friend(self, event, user):
        user_del = event
        await self.delete_friend(user_del)
        await self.send_json({
            "message": f"{user} delete confirmation {user_del}"
        })

    @database_sync_to_async
    def delete_friend(self, username):
        return Friends.objects.filter(user__username=username).delete()

    @database_sync_to_async
    def add_friend(self, friend):
        user: User = self.user
        try:
            friend = User.objects.get(username=friend)
            return Friends.objects.create(user=user, friend=friend)
        except BaseException:
            return None

    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        await self.add_messages_to_room(message)
        await self.send_json({
            'message': message,
            'user': user
        })

    @database_sync_to_async
    def add_user_to_room(self):
        user: User = self.user
        try:
            room = Room.objects.get(name=self.room_name)
            user.current_rooms.add(room)
        except BaseException:
            Room.objects.create(name=self.room_name, host=user)
            user.current_rooms.add(Room.objects.get(name=self.room_name))

    @database_sync_to_async
    def add_messages_to_room(self, messages):
        user: User = self.user
        room: Room = Room.objects.get(name=self.room_name)
        Message.objects.create(room=room, text=messages, user=user)

    @database_sync_to_async
    def story_messages_to_room(self):
        story = Message.objects.filter(room__name=self.room_name)
        lib = []
        for obj in story:
            lib.append({'message': obj.text, 'user': obj.user.username})
        return lib

    async def print_story(self, messages):
        for obj in messages:
            await self.send_json(obj)
