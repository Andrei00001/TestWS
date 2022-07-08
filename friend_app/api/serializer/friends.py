from rest_framework import serializers

from ...models import Friends

from django.contrib.auth.models import User


class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = "__all__"
        read_only_fields = "user", "confirmation"

    publisher_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
        source="user",
    )


class UpdateFriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = "__all__"
        read_only_fields = "user", "friend"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user