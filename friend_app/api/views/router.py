from rest_framework import routers

from ...api.views.friend import FriendsView, UpdateFriendsView

api_router = routers.DefaultRouter()
api_router.register("friend", FriendsView)
api_router.register("add_friend_y_or_n", UpdateFriendsView)


