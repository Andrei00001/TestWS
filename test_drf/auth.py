from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser, User


class TokenAuthMiddleware(BaseMiddleware):
    """
    Token authorization middleware for Django Channels 2
    """

    async def __call__(self, scope, receive, send):

        try:
            token_key = scope["query_string"].decode()[6:]
            scope['user'] = await database_sync_to_async(User.objects.get)(
                auth_token=token_key
            )
        except BaseException:
            scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
