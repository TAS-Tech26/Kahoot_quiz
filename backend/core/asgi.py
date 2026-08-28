# asgi.py


from django.core.asgi import get_asgi_application

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
import game.routing 

# 3. Define the application routing
application = ProtocolTypeRouter({'http': django_asgi_app, 'websocket': URLRouter(game.routing.websocket_urlpatterns)})