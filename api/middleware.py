from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from api.models import User
import jwt


@database_sync_to_async
def get_user(token_key):
    try:
        user_id: int = jwt.decode(token_key, key=settings.SECRET_KEY, algorithms=['HS256'])['user_id']
        return User.objects.get(id=user_id) if user_id is not None else AnonymousUser()
    except:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            token_key = scope['query_string'].decode().split('=')[-1]
        except ValueError:
            token_key = None
        scope['user'] = await get_user(token_key) if token_key is not None else AnonymousUser()
        return await super().__call__(scope, receive, send)
