# consumers.py


from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from urllib.parse import parse_qs

from .handlers import GameSessionHandler

import jwt


class GameConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.pin = self.scope['url_route']['kwargs']['pin']
        self.room_group_name = f'game_{self.pin}'
        self.handler = GameSessionHandler(self)

        self.is_verified_host = False

        query_string = self.scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)

        if 'token' in query_params:
            token = query_params['token'][0]

            try:
                payload = jwt.decode(token, settings.HUB_SECRET_KEY, algorithms = ['HS256'])

                if payload.get('role') == 'host':
                    self.is_verified_host = True
            except jwt.PyJWTError:
                pass # Invalid/expired token. They're a normal player.
        
        if not await self.handler.verify_session():
            await self.close(code = 4004) # Drop connection instantly

            return
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        total_players = await self.handler.redis.get_active_players_count()

        await self.send_json({'event' : 'room_status', 'data' : {'total_players' : total_players}})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await self.handler.handle_disconnect()

    async def receive_json(self, content):
        action = content.get('action')
        data = content.get('data', {})

        claimed_host = content.get('role') == 'host'
        is_host = claimed_host and self.is_verified_host

        if claimed_host and not self.is_verified_host:
            await self.send_json({'event_type' : 'error', 'message' : "Unauthorized host action intercepted."})

            return

        if action == 'host_start' and is_host:
            await self.handler.handle_host_start()
        elif action == 'host_next_question' and is_host:
            await self.handler.handle_next_question()
        elif action == 'host_start_timer' and is_host:
            await self.handler.handle_start_timer()
        elif action == 'player_join' and not is_host:
            await self.handler.handle_player_join(content.get('data'))
        elif action == 'submit_answer' and not is_host:
            await self.handler.handle_submit_answer(content.get('data'))
        elif action == 'host_show_leaderboard' and is_host:
            await self.handler.handle_show_leaderboard()
        elif action == 'host_force_sync' and is_host:
            await self.handler.handle_force_sync()
        else:
            await self.send_json({'event_type' : 'error', 'message' : "Invalid action, missing data or unauthorized role."})

    async def broadcast_event(self, event):
        """Fires the actual data through WS to the React frontend"""

        await self.send_json({'event' : event['event_type'], 'data' : event.get('data', {})})