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
        self.correct_key = f'game:{self.pin}:correct_counts'
        self.time_key = f'game:{self.pin}:total_time'

    async def get_state(self):

        return await redis_client.hgetall(self.state_key)

    async def get_quiz_data(self):
        data = await redis_client.get(self.quiz_key)

        return json.loads(data) if data else None

    async def initialise_game_state(self, first_question_id, quiz_data):
        await redis_client.hset(
            self.state_key,
            mapping = {'status' : 'staging', 'current_question_index' : 0, 'current_question_id' : first_question_id}
        )
        await redis_client.set(self.quiz_key, json.dumps(quiz_data))

    async def register_new_player(self, team_code, name):
        await redis_client.hset(self.players_key, team_code, name)
        await redis_client.zadd(self.scores_key, {team_code : 0}, nx = True)
        await redis_client.hincrby(self.active_key, team_code, 1)

    async def add_active_player(self, team_code):
        await redis_client.hincrby(self.active_key, team_code, 1)

    async def remove_active_player(self, team_code):
        count = await redis_client.hincrby(self.active_key, team_code, -1)
        
        if count <= 0:
            await redis_client.hdel(self.active_key, team_code)

    async def stage_question_state(self, question_index, question_id):
        await redis_client.hset(self.state_key, mapping = {'status' : 'staging', 'current_question_index' : question_index, 'current_question_id' : question_id})
        await redis_client.hdel(self.state_key, 'start_time')

    async def activate_timer_state(self):
        """Starts the official timer for the current staged Q"""

        await redis_client.hset(self.state_key, mapping = {'status' : 'active', 'start_time' : time.time()})

    async def get_active_players_count(self):

        return await redis_client.hlen(self.active_key)

    async def get_player_name(self, team_code):

        return await redis_client.hget(self.players_key, team_code)

    async def mark_player_answered(self, question_id, team_code):
        answered_key = f'game:{self.pin}:answered:{question_id}' # Dynamic key for each Q

        return await redis_client.sadd(answered_key, team_code)

    async def has_player_answered(self, question_id, team_code):
        answered_key = f'game:{self.pin}:answered:{question_id}'
        return await redis_client.sismember(answered_key, team_code)


    async def get_answered_count(self, question_id):
        answered_key = f'game:{self.pin}:answered:{question_id}'

        return await redis_client.scard(answered_key)

    async def increment_player_score(self, team_code, points):
        await redis_client.zincrby(self.scores_key, points, team_code)

    async def increment_correct_answers(self, team_code):
        await redis_client.hincrby(self.correct_key, team_code, 1)

    async def add_player_time(self, team_code, time_taken):
        await redis_client.hincrbyfloat(self.time_key, team_code, time_taken)

    async def get_player_time(self, team_code):
        val = await redis_client.hget(self.time_key, team_code)

        return float(val) if val else 0.0

    async def get_correct_answers(self, team_code):
        count = await redis_client.hget(self.correct_key, team_code)

        return int(count) if count else 0

    async def get_final_scores(self):

        return await redis_client.zrevrange(self.scores_key, 0, -1, withscores = True) # zrevrange returns tuples of (member, score) where score is float.

    async def set_leaderboard_state(self):
        await redis_client.hset(self.state_key, mapping = {'status' : 'leaderboard'})

    async def cleanup_game_data(self):
        cursor = 0

        match_pattern = f'game:{self.pin}:*'

        while True:
            cursor, keys = await redis_client.scan(cursor = cursor, match = match_pattern, count = 100)

            if keys:
                await redis_client.delete(*keys)
            if cursor == 0 or cursor == '0':
                break
