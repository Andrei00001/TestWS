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
        self.user_group_name = f"chat_{self.user}"
        self.valid_u = {'message': f'User not valid'}
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.user_group_name,
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
        data = json.loads(kwargs["text_data"])

        type_func = {
            "message": self.print_message_fo_group_room(data),
            "friend": self.print_message_fo_user_room(data),
        }

        await type_func[data["type"]]

    async def print_message_fo_user_room(self, event):
        friend = event["message"]
        action = event["action"]

        valid_friend_obj = await self.valid_user(friend)

        if valid_friend_obj:
            type_func = {
                "friendship_created": self.create_friend(valid_friend_obj),
                "add_friends": self.update_friend(valid_friend_obj),
                "del_friends": self.delete_friend(valid_friend_obj),
            }
            await type_func[action]

            await self.channel_layer.group_send(
                f"chat_{friend}",
                {
                    'type': action,
                    'message': friend,
                    'user': self.user.username,
                }
            )
        else:
            await self.send_json(self.valid_u)

    async def friendship_created(self, event):
        await self.send_json({
            'message': f'User {event["user"]} add in friend {event["message"]}',
        })

    async def add_friends(self, event):
        await self.send_json({
            "message": f"{event['user']} add confirmation {event['message']}"
        })

    async def del_friends(self, event):
        await self.send_json({
            "message": f"{event['user']} delete confirmation {event['message']}"
        })

    async def print_message_fo_group_room(self, event):
        message = event["message"]
        await self.add_messages_to_room(message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        await self.send_json({
            'message': message,
            'user': user
        })

    @database_sync_to_async
    def add_messages_to_room(self, messages):
        user: User = self.user
        room: Room = Room.objects.get(name=self.room_name)
        Message.objects.create(room=room, text=messages, user=user)

        # Send message to room group

        # Receive message from room group

    @database_sync_to_async
    def valid_user(self, user):
        try:
            return User.objects.get(username=user)
        except BaseException:
            return None

    @database_sync_to_async
    def create_friend(self, friend):
        user: User = self.user
        return Friends.objects.create(user=user, friend=friend)
        # Send a message to WebSocket

    @database_sync_to_async
    def update_friend(self, friend):
        return Friends.objects.filter(user=friend, friend=self.user).update(confirmation=True)

    @database_sync_to_async
    def delete_friend(self, friend):
        return Friends.objects.filter(user=friend, friend=self.user).delete()

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
    def story_messages_to_room(self):
        story = Message.objects.filter(room__name=self.room_name)
        lib = []
        for obj in story:
            lib.append({'message': obj.text, 'user': obj.user.username})
        return lib

    async def print_story(self, messages):
        for obj in messages:
            await self.send_json(obj)
