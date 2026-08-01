# redis_service.py


import redis.asyncio as redis

import json, os, time


redis_client = redis.from_url(os.environ.get('REDIS_URL', 'redis://127.0.0.1:6380/1'), decode_responses = True)


class GameRedisManager:

    def __init__(self, pin):
        self.pin = pin

        self.state_key = f'game:{self.pin}:state'
        self.players_key = f'game:{self.pin}:players'
        self.active_key = f'game:{self.pin}:active_players'
        self.scores_key = f'game:{self.pin}:scores'
        self.quiz_key = f'game:{self.pin}:quiz'
        self.identities_key = f'game:{self.pin}:identities'

    async def get_player_by_contact(self, contact_info):
        """Checks if the email/phone already belongs to a registered UUID"""

        return await redis_client.hget(self.identities_key, contact_info)

    async def get_state(self):

        return await redis_client.hgetall(self.state_key)

    async def get_quiz_data(self):
        data = await redis_client.get(self.quiz_key)

        return json.loads(data) if data else None

    async def initialise_game_state(self, first_question_id, quiz_data):
        await redis_client.hset(
            self.state_key,
            mapping = {'status' : 'active', 'current_question_index' : 0, 'current_question_id' : first_question_id, 'start_time' : time.time()}
        )
        await redis_client.set(self.quiz_key, json.dumps(quiz_data))

    async def update_state_for_next_question(self, next_index, next_question_id):
        await redis_client.hset(
            self.state_key,
            mapping = {'current_question_index' : next_index, 'current_question_id' : next_question_id, 'start_time' : time.time()}
        )

    async def register_new_player(self, player_id, full_name, contact_info):
        await redis_client.hset(self.players_key, player_id, full_name)
        await redis_client.hset(self.identities_key, contact_info, player_id)
        await redis_client.zadd(self.scores_key, {player_id : 0}, nx = True)
        await redis_client.sadd(self.active_key, player_id)

    async def add_active_player(self, player_id):
        await redis_client.sadd(self.active_key, player_id)

    async def remove_active_player(self, player_id):
        await redis_client.srem(self.active_key, player_id)

    async def get_active_players_count(self):

        return await redis_client.scard(self.active_key)

    async def get_player_name(self, player_id):

        return await redis_client.hget(self.players_key, player_id)

    async def mark_player_answered(self, question_id, player_id):
        answered_key = f'game:{self.pin}:answered:{question_id}' # Dynamic key for each Q

        return await redis_client.sadd(answered_key, player_id)

    async def get_answered_count(self, question_id):
        answered_key = f'game:{self.pin}:answered:{question_id}'

        return await redis_client.scard(answered_key)

    async def increment_player_score(self, player_id, points):
        await redis_client.zincrby(self.scores_key, points, player_id)

    async def get_final_scores(self):

        return await redis_client.zrevrange(self.scores_key, 0, -1, withscores = True) # zrevrange returns tuples of (member, score) where score is float.

    async def cleanup_game_data(self):
        cursor = b'0'

        match_pattern = f'game:{self.pin}:*'

        while cursor:
            cursor, keys = await redis_client.scan(cursor = cursor, match = match_pattern, count = 100)

            if keys:
                await redis_client.delete(*keys)