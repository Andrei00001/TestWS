from django.urls import path

from friend_app.consumers import UpdateFriendsConsumer, FriendsConsumer, UserConsumer

websocket_urlpatterns = [

    path('ws/user_castom/', UserConsumer.as_asgi()),
    path('ws/friend/', FriendsConsumer.as_asgi()),
    path('ws/add_friend_y_or_n/', UpdateFriendsConsumer.as_asgi()),
]
