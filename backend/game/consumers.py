# consumers.py


from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .models import GameSession, PlayerResult, Quiz

import redis.asyncio as redis
import json, os, time, uuid


redis_client = redis.from_url(os.environ.get('REDIS_URL', 'redis://127.0.0.1:6380/1'), decode_responses = True)


class GameConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.pin = self.scope['url_route']['kwargs']['pin']
        self.room_group_name = f'game_{self.pin}'
        self.session = await self.get_game_session(self.pin) # Check if the pin exists in Postgres

        if not self.session:
            await self.close(code = 4004) # Drop connection instantly

            return
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content):
        action = content.get('action')
        is_host = content.get('role') == 'host'

        if action == 'host_start' and is_host:
            await self.handle_host_start()
        elif action == 'host_next_question' and is_host:
            await self.handle_next_question()
        elif action == 'player_join' and not is_host:
            await self.handle_player_join(content.get('data'))
        elif action == 'submit_answer' and not is_host:
            await self.handle_submit_answer(content.get('data'))
        else:
            pass

    async def handle_host_start(self):
        """Gets the pre-compiled JSON from Postgres, loads into Redis & starts the game"""

        quiz_data = await self.get_compiled_quiz_data()

        first_question = quiz_data['questions'][0]
        
        # The reason we use this fomatting for keys is because it's the std convention to store Redis keys like this. Moreover, most softwares used to visualise Redis
        # storages use this kind of formatting to neatly display all the tables & related fields.
        state_key = f'game:{self.pin}:state' # Stores active state in a Redis hash
        
        await redis_client.hset(
            state_key,
            mapping = {'status' : 'active', 'current_question_index' : 0, 'current_question_id' : first_question['id'], 'start_time' : time.time()}
        )
        await redis_client.set(f'game:{self.pin}:quiz', json.dumps(quiz_data)) # Stores the entire compiled quiz in Redis as a JSON str for faster reads

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type' : 'broadcast_event',
                'event_type' : 'question_revealed',
                'data' : {
                    'question_id' : first_question['id'],
                    'text' : first_question['text'],
                    'time_limit' : first_question['time_limit'],
                    'choices' : [{'id' : c['id'], 'text' : c['text']} for c in first_question['choices']]
                }
            }
        )

    async def handle_player_join(self, data):
        """Generates UUID, tracks player in Redis, adds to leaderboard."""

        provided_id = data.get('player_id')

        players_key = f'game:{self.pin}:players'

        # To re-connect the player if they've disconnected (A new player ID would be generated if the player got disconnected but their data is already stored in Redis.
        # connecting to the old player ID. That means if they got disconnected, they'd lose all the game data, including their score, leaderboard ranking etc. So we
        # check if the player already exists in Redis & if so, connect the new player ID to the old 1.)
        if provided_id:
            existing_name = await redis_client.hget(players_key, provided_id)

            if existing_name:
                # Bind the existing identity to the new socket instance
                self.player_id = provided_id

                await self.send_json({'event_type' : 'rejoin_success', 'player_id' : provided_id, 'name' : existing_name})

                return

        # Data validation (To prevent Postgres NULL crashes)
        full_name = data.get('full_name')
        contact_info = data.get('contact_info')

        if not full_name or contact_info:
            await self.send_json({'event_type' : 'error', 'message' : "Missing required fields for new player registration."})

            return

        new_player_id = str(uuid.uuid4())

        self.player_id = new_player_id

        await redis_client.hset(players_key, new_player_id, full_name) # Redis Hash: Map UUID to name
        await redis_client.zadd(f'game:{self.pin}:scores', {new_player_id : 0}, nx = True) # Redis Sorted Set: Add to leaderboard with 0 points (nx = True guarantees we
                                                                                            # never overwrite an existing score to 0)
        
        await self.create_player_result(new_player_id, full_name, data.get('contact_info'), data.get('school_name'), data.get('grade_level'))
        await self.send_json({'event_type' : 'join_success', 'player_id' : new_player_id})
        await self.channel_layer.group_send(self.room_group_name, {'type' : 'broadcast_event', 'event_type' : 'player_joined', 'data' : {'name' : full_name}})

    async def broadcast_event(self, event):
        """Fires the actual data through the WebSocket to the React frontend"""
        await self.send_json({'event' : event['event_type'], 'data' : event.get('data', {})})

    async def handle_submit_answer(self, data):
        if not hasattr(self, 'player_id'):

            return
        
        choice_id = data.get('choice_id')

        state_key = f'game:{self.pin}:state'
        state = await redis_client.hgetall(state_key)

        # Dropping Q if Q is already over or lobby is waiting.
        if state.get('status') != 'active':

            return
        
        question_id = int(state.get('current_question_id'))
        start_time = float(state.get('start_time'))

        # Prevents the user to spam answers (takes only the 1st input)
        answered_key = f'game:{self.pin}:answered:{question_id}'
        is_first_attempt = await redis_client.sadd(answered_key, self.player_id)

        if not is_first_attempt:
            
            return
        
        time_taken = time.time() - start_time # Check how long the user took to ans the Q
        
        quiz_data = json.loads(await redis_client.get(f'game:{self.pin}:quiz')) # Data validation, read from Redis

        current_question = next((q for q in quiz_data['questions'] if q['id'] == question_id), None)

        if not current_question:
            
            return
        
        time_limit = float(current_question['time_limit'])

        chosen_choice = next((c for c in current_question['choices'] if c['id'] == choice_id), None)
        is_correct = chosen_choice.get('is_correct', False) if chosen_choice else False

        points_earned = 0

        if is_correct and time_taken <= time_limit:
            points_earned = round((1 - (time_taken / (time_limit * 2))) * 1000)

            await redis_client.zincrby(f'game:{self.pin}:scores', points_earned, self.player_id) # Automatically increment score in Redis Sorted Set.

        # Send priv data only to the person who answered
        await self.send_json({'event_type' : 'answer_result', 'data' : {'is_correct' : is_correct, 'points_earned' : points_earned}})

        # Send a msg to the entire room that the frontend can update the ans submitted counter.
        await self.channel_layer.group_send(self.room_group_name, {'type' : 'broadcast_event', 'event_type' : 'answer_registered'})

    async def handle_next_question(self):
        state_key = f'game:{self.pin}:state'
        state = await redis_client.hgetall(state_key)

        # Fetch current index
        current_index = int(state.get('current_question_index', 0))
        next_index = current_index + 1

        # Load compiled quiz
        quiz_data = json.loads(await redis_client.get(f'game:{self.pin}:quiz'))
        total_questions = len(quiz_data['questions'])

        # Check if game is over
        if next_index >= total_questions:
            await self.handle_end_game()

            return

        # Fetch next Q data
        next_question = quiz_data['questions'][next_index]

        # Change state to new Q
        await redis_client.hset(state_key, mapping = {'current_question_index' : next_index, 'current_question_id' : next_question['id'], 'start_time' : time.time()})

        # Broadcast to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type' : 'broadcast_event',
                'event_type' : 'question_revealed',
                'data' : {
                    'question_id' : next_question['id'],
                    'text' : next_question['text'],
                    'time_limit' : next_question['time_limit'],
                    'choices' : [{'id' : c['id'], 'text' : c['text']} for c in next_question['choices']]
                }
            }
        )

    async def handle_end_game(self):
        scores_key = f'game:{self.pin}:scores'
        players_key = f'game:{self.pin}:players'

        raw_scores = await redis_client.zrevrange(scores_key, 0, -1, withscores = True)

        final_leaderboard = []
        player_scores_map = {}

        for player_id, score in raw_scores:
            name = await redis_client.hget(players_key, player_id)
            
            score_int = int(score)

            final_leaderboard.append({'name' : name, 'score' : score_int, 'player_id' : player_id})

            player_scores_map[player_id] = score_int

        await self.channel_layer.group_send(
            self.room_group_name,
            {'type' : 'broadcast_event', 'event_type' : 'game_over', 'data' : {'leaderboard' : final_leaderboard[:5]}} # Send top 5 to frontend
        )
        
        if player_scores_map:
            await self.bulk_save_final_scores(player_scores_map, final_leaderboard)

        # Clean-up Redis memory
        cursor = b'0'

        match_pattern = f'game:{self.pin}:*'

        while cursor:
            cursor, keys = await redis_client.scan(cursor = cursor, match = match_pattern, count = 100)

            if keys:
                await redis_client.delete(*keys)

    """DB readers"""
    @database_sync_to_async
    def get_game_session(self, pin):
        try:
            
            return GameSession.objects.get(pin = pin)
        
        except GameSession.DoesNotExist:

            return None
        
    @database_sync_to_async
    def get_compiled_quiz_data(self):

        return self.session.quiz.compiled_data
    
    @database_sync_to_async
    def create_player_result(self, player_id, full_name, contact_info, school_name, grade_level):
        PlayerResult.objects.create(
            session = self.session,
            player_id = player_id,
            full_name = full_name,
            contact_info = contact_info,
            school_name = school_name,
            grade_level = grade_level
        )

    @database_sync_to_async
    def bulk_save_final_scores(self, player_scores_map, final_leaderboard):
        """Executes a single SQL query to update all player scores simultaneously & save the session leaderboard."""
        
        # Fetch all records in 1 query
        results = PlayerResult.objects.filter(session = self.session, player_id__in = player_scores_map.keys())

        # Update player scores
        for result in results:
            result.total_score = player_scores_map[result.player_id]

        # Write back to DB in 1 transactiono
        if results:
            PlayerResult.objects.bulk_update(results, ['total_score'])

        self.session.final_leaderboard = final_leaderboard
        self.session.ended_at = timezone.now()
        self.session.save(update_fields = ['final_leaderboard', 'ended_at'])