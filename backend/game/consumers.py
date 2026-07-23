# consumers.py


from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .handlers import GameSessionHandler


class GameConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.pin = self.scope['url_route']['kwargs']['pin']
        self.room_group_name = f'game_{self.pin}'
        self.handler = GameSessionHandler(self)

        if not self.handler.verify_session():
            await self.close(code = 4004) # Drop connection instantly

            return
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await self.handler.handle_disconnect()

    async def receive_json(self, content):
        action = content.get('action')
        is_host = content.get('role') == 'host'
        data = content.get('data', {})

        if action == 'host_start' and is_host:
            await self.handle_host_start()
        elif action == 'host_next_question' and is_host:
            await self.handle_next_question()
        elif action == 'player_join' and not is_host:
            await self.handle_player_join(content.get('data'))
        elif action == 'submit_answer' and not is_host:
            await self.handle_submit_answer(content.get('data'))
        else:
            await self.send_json({'event_type' : 'error', 'message' : "Invalid action, missing data or unauthorized role."})

    async def broadcast_event(self, event):
        """Fires the actual data through WS to the React frontend"""

        await self.send_json({'event' : event['event_type'], 'data' : event.get('data', {})})