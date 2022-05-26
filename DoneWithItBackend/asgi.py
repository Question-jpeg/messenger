"""
ASGI config for DoneWithItBackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from api.routing import websocket_urlpatterns
from api.middleware import TokenAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'DoneWithItBackend.settings.dev')

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        TokenAuthMiddleware(
            URLRouter(
                websocket_urlpatterns
            )
        )
    )
})
