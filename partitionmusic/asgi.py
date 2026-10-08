import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'partitionmusic.settings')

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import dashboard.routing
import partitions.routing
# import comptes.routing  # à décommenter quand P1 l'aura créé

websocket_urlpatterns = (
    dashboard.routing.websocket_urlpatterns
    + partitions.routing.websocket_urlpatterns
    # + comptes.routing.websocket_urlpatterns
)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    ),
})