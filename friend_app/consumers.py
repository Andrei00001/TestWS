import json

import self as self
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User

from friend_app.models import Room, Message


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
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
            }
        )

        # Receive message from room group

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
        except  BaseException:
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
