from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import lottery.routing
from channels.security.websocket import AllowedHostsOriginValidator


application = ProtocolTypeRouter({

    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                lottery.routing.websocket_urlpatterns
            )
        ),
    ),
})
