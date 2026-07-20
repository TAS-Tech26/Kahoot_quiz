# routing.py


from . import consumers

from django.urls import re_path


websocket_urlpatterns = [re_path(r'^ws/game/(?P<pin>\d{6})/$', consumers.GameConsumer.as_asgi())]