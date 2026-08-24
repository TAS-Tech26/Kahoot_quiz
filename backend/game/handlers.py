# handlers.py


from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.conf import settings
from django.utils import timezone

from .models import GameSession, PlayerResult
from .redis_service import GameRedisManager

import asyncio, httpx, os, time


class GameSessionHandler:

    def __init__(self, consumer):
        self.consumer = consumer
        self.pin = consumer.pin
        self.redis = GameRedisManager(self.pin)
        self.session_record = None

    async def verify_session(self):
        self.session_record = await self._get_game_session(self.pin)

        return self.session_record is not None

    async def handle_disconnect(self):
        if hasattr(self.consumer, 'identity'):
            await self.redis.remove_active_player(self.consumer.identity)

            total_players = await self.redis.get_active_players_count()

            await self.consumer.channel_layer.group_send(
                self.consumer.room_group_name,
                {'type' : 'broadcast_event', 'event_type' : 'player_left', 'data' : {'total_players' : total_players}}
            )

    async def handle_host_start(self):
        quiz_data = await self._get_compiled_quiz_data()
        first_question = quiz_data['questions'][0]

        await self.redis.initialise_game_state(first_question['id'], quiz_data)

        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
            {
                'type' : 'broadcast_event',
                'event_type' : 'question_staged',
                'data' : {
                    'question_id' : first_question['id'],
                    'text' : first_question['text'],
                    'media_url' : first_question.get('media_url'),
                    'media_type' : first_question.get('media_type')
                }
            }
        )

    async def handle_player_join(self, data):
        """2 ways to check for existing players. 1st - They accidentally disconnect/network drop etc. The player gets reconnected without seeing log in screen (using 
        localStorage). 2nd - They try to cheat the system by opening a new incognito tab/device switching etc, then a single identity is forced, overriding localStorage"""

        event_name = self.session_record.event_name

        team_pin = data.get('team_pin')

        if not team_pin:
            await self.consumer.send_json({'event' : 'error', 'data' : {'message' : "Team PIN is required."}})

            return

        existing_name = await self.redis.get_player_name(team_pin)

        if existing_name:
            self.consumer.identity = team_pin

            await self.redis.add_active_player(team_pin)

            total_players = await self.redis.get_active_players_count()

            sync_payload = await self._build_rejoin_payload(team_pin, existing_name)

            await self.consumer.send_json(sync_payload)
            await self.consumer.channel_layer.group_send(
                self.consumer.room_group_name,
                {'type' : 'broadcast_event', 'event_type' : 'player_joined', 'data' : {'name' : existing_name, 'total_players' : total_players}}
            )

            return

        hub_url = os.environ.get('HUB_SERVICE_URL', 'http://127.0.0.1:8000')
        hub_secret = os.environ.get('HUB_SECRET_KEY')

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f'{hub_url}/api/admin/verify-team/{team_pin}/{event_name}/', headers = {'X-Hub-Secret' : hub_secret})
            except httpx.RequestError:
                await self.consumer.send_json({'event' : 'error', 'data' : {'message' : "Failed to contact the orchestrator."}})

                return

        if response.status_code != 200:
            await self.consumer.send_json({'event' : 'error', 'data' : {'message' : "Invalid team credentials for this event."}})

            return

        self.consumer.identity = team_pin
        full_name = f"Team {team_pin}"

        await self.redis.register_new_player(team_pin, full_name)

        total_players = await self.redis.get_active_players_count()

        asyncio.create_task(self._create_player_result(team_pin, full_name))

        await self.consumer.send_json({'event' : 'join_success', 'data' : {'team_pin' : team_pin}})
        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
            {'type' : 'broadcast_event', 'event_type' : 'player_joined', 'data' : {'name' : full_name, 'total_players' : total_players}}
        )

    async def handle_submit_answer(self, data):
        if not hasattr(self.consumer, 'identity'):

            return
        
        state = await self.redis.get_state()

        if state.get('status') != 'active':

            return
        
        choice_id = data.get('choice_id')

        question_id = int(state.get('current_question_id'))
        start_time = float(state.get('start_time'))

        if not await self.redis.mark_player_answered(question_id, self.consumer.identity):

            return

        time_taken = time.time() - start_time

        quiz_data = await self.redis.get_quiz_data()
        current_question = next((q for q in quiz_data['questions'] if q['id'] == question_id), None)

        if not current_question:

            return

        time_limit = float(current_question['time_limit'])

        chosen_choice = next((c for c in current_question['choices'] if c['id'] == choice_id), None)
        is_correct = chosen_choice.get('is_correct', None) if chosen_choice else False

        points_earned = 0

        if is_correct and time_taken <= time_limit:
            points_earned = round((1 - (time_taken / (time_limit * 2))) * 1000)

            await self.redis.increment_player_score(self.consumer.identity, points_earned)
            await self.redis.increment_correct_answers(self.consumer.identity)
            await self.redis.add_player_time(self.consumer.identity, time_taken)

        total_answers = await self.redis.get_answered_count(question_id)

        await self.consumer.send_json({'event' : 'answer_result', 'data' : {'is_correct' : is_correct, 'points_earned' : points_earned}})
        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
            {'type' : 'broadcast_event', 'event_type' : 'answer_registered', 'data' : {'total_answers' : total_answers}}
        )

    async def handle_show_leaderboard(self):
        top_5, player_ranks, _, _, _ = await self._get_current_leaderboard()

        await self.redis.set_leaderboard_state()

        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
            {'type' : 'broadcast_event', 'event_type' : 'round_leaderboard', 'data' : {'leaderboard' : top_5, 'player_ranks' : player_ranks}}
        )

    async def handle_force_sync(self):
        state = await self.redis.get_state()

        if not state:

            return

        status = state.get('status')

        if status == 'leaderboard':
            await self.handle_show_leaderboard()

            return

        quiz_data = await self.redis.get_quiz_data()

        q_id = int(state.get('current_question_id'))
        
        current_q = next((q for q in quiz_data['questions'] if q['id'] == q_id), None)

        if not current_q:

            return

        if status == 'staging':
            await self.consumer.channel_layer.group_send(
                self.consumer.room_group_name,
                {
                    'type' : 'broadcast_event',
                    'event_type' : 'question_staged',
                    'data' : {
                        'question_id' : current_q['id'],
                        'text' : current_q['text'],
                        'media_url' : current_q.get('media_url'),
                        'media_type' : current_q.get('media_type')
                    }
                }
            )
        elif status == 'active':
            start_time = float(state.get('start_time'))
            elapsed = time.time() - start_time
            remaining = max(0, float(current_q['time_limit']) - elapsed)

            await self.consumer.channel_layer.group_send(
                self.consumer.room_group_name,
                {
                    'type' : 'broadcast_event',
                    'event_type' : 'question_revealed',
                    'data' : {
                        'question_id' : current_q['id'],
                        'text' : current_q['text'],
                        'time_limit' : remaining,
                        'choices' : [{'id' : c['id'], 'text' : c['text']} for c in current_q['choices']]
                    }
                }
            )

    async def handle_next_question(self):
        state = await self.redis.get_state()

        current_index = int(state.get('current_question_index', 0))
        next_index = current_index + 1

        quiz_data = await self.redis.get_quiz_data()
        total_questions = len(quiz_data['questions'])

        if next_index >= total_questions:
            await self._handle_end_game()

            return

        next_question = quiz_data['questions'][next_index]

        await self.redis.stage_question_state(next_index, next_question['id'])

        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
            {
                'type' : 'broadcast_event',
                'event_type' : 'question_staged',
                'data' : {
                    'question_id' : next_question['id'],
                    'text' : next_question['text'],
                    'media_url' : next_question.get('media_url'),
                    'media_type' : next_question.get('media_type')
                }
            }
        )

    async def handle_start_timer(self):
        state = await self.redis.get_state()

        if state.get('status') != 'staging':

            return

        await self.redis.activate_timer_state()

        q_id = int(state.get('current_question_id'))

        quiz_data = await self.redis.get_quiz_data()

        current_q = next((q for q in quiz_data['questions'] if q['id'] == q_id), None)

        if current_q:
            await self.consumer.channel_layer.group_send(
                self.consumer.room_group_name,
                {
                    'type' : 'broadcast_event',
                    'event_type' : 'question_active',
                    'data' : {
                        'question_id' : current_q['id'],
                        'time_limit' : current_q['time_limit'],
                        'choices' : [{'id' : c['id'], 'text' : c['text']} for c in current_q['choices']]
                    }
                }
            )

    async def _build_rejoin_payload(self, team_code, name):
        """Builds the rejoin payload & attaches the active game state if a Q is live."""

        data_block = {'team_pin' : team_code, 'name' : name}

        state = await self.redis.get_state()

        if state:
            status = state.get('status')

            quiz_data = await self.redis.get_quiz_data()

            q_id = int(state.get('current_question_id'))

            current_q = next((q for q in quiz_data['questions'] if q['id'] == q_id), None)

            if current_q:
                if status == 'staging':
                    data_block['active_question'] = {
                        'status' : 'staging',
                        'question_id' : current_q['id'],
                        'text' : current_q['text'],
                        'media_url' : current_q.get('media_url'),
                        'media_type' : current_q.get('media_type')
                    }
                elif status == 'active':
                    start_time = float(state.get('start_time', time.time()))
                    elapsed = time.time() - start_time
                    remaining = max(0, float(current_q['time_limit']) - elapsed)

                    data_block['active_question'] = {
                        'status' : 'active',
                        'question_id' : current_q['id'],
                        'text' : current_q['text'],
                        'time_limit' : remaining,
                        'choices' : [{'id' : c['id'], 'text' : c['text']} for c in current_q['choices']]
                    }

        return {'event' : 'rejoin_success', 'data' : data_block}
    
    async def _get_current_leaderboard(self, limit = 5):
        raw_scores = await self.redis.get_final_scores()

        top_5 = []
        player_ranks = {}
        player_scores_map = {}
        player_correct_map = {}
        player_time_map = {}

        for index, (team_code, score) in enumerate(raw_scores):
            rank = index + 1

            score_int = int(score)

            player_ranks[team_code] = rank
            player_scores_map[team_code] = score_int

            correct_count = await self.redis.get_correct_answers(team_code)
            player_correct_map[team_code] = correct_count

            time_taken = await self.redis.get_player_time(team_code)
            player_time_map[team_code] = time_taken

            if rank <= limit:
                name = await self.redis.get_player_name(team_code)

                top_5.append({'name' : name, 'score' : score_int, 'team_pin' : team_code, 'rank' : rank})

        return top_5, player_ranks, player_scores_map, player_correct_map, player_time_map

    async def _handle_end_game(self):
        top_5, player_ranks, player_scores_map, player_correct_map, player_time_map = await self._get_current_leaderboard()

        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
            {'type' : 'broadcast_event', 'event_type' : 'game_over', 'data' : {'leaderboard' : top_5, 'player_ranks' : player_ranks}}
        )

        if player_scores_map:
            await self._bulk_save_final_scores(player_scores_map, player_correct_map, player_time_map, top_5)
            await self._push_results_to_orchestrator(player_scores_map, player_correct_map, player_time_map, player_ranks)

        await self.redis.cleanup_game_data()

    async def _push_results_to_orchestrator(self, player_scores_map, player_correct_map, player_time_map, player_ranks):
        event_name = self.session_record.event_name

        hub_url = os.environ.get('HUB_SERVICE_URL', 'http://127.0.0.1:8000')
        hub_secret = os.environ.get('HUB_SECRET_KEY')

        results_payload = []

        for team_code, rank in player_ranks.items():
            score = player_scores_map.get(team_code, 0)
            correct = player_correct_map.get(team_code, 0)
            time_taken = player_time_map.get(team_code, 0.0)

            assets_str = f"{score} PTS | {correct} Qs | {time_taken:.2f}s" # Format the data into a single str for the Hub's EventStanding model

            results_payload.append({'team_code' : team_code, 'rank' : rank, 'assets' : assets_str})

        async with httpx.AsyncClient() as client:
            for attempt in range(3): # 3 retry attempts
                try:
                    response = await client.post(
                        f'{hub_url}/api/webhooks/ingest/{event_name}/',
                        json = {'results' : results_payload},
                        headers = {'X-Hub-Secret' : hub_secret},
                        timeout = 10
                    )

                    if response.status_code == 200:

                        return

                    print(f"Hub rejected payload with status {response.status_code}. Retrying...")
                except httpx.RequestError as e:
                    print(f"Attempt {attempt + 1}: Failed to push results to orchestrator: {e}")

                await asyncio.sleep(2 ** attempt)

            print(f"Failed to push final results to Hub for room {self.pin} after 3 attempts")

    # --- DB Readers/Writers
    @database_sync_to_async
    def _get_game_session(self, pin):
        try:

            return GameSession.objects.select_related('quiz').get(pin = pin)
        
        except GameSession.DoesNotExist:

            return None

    @database_sync_to_async
    def _get_compiled_quiz_data(self):

        return self.session_record.quiz.compiled_data

    @database_sync_to_async
    def _create_player_result(self, team_code, name):
        PlayerResult.objects.create(
            session_id = self.session_record.id,
            team_code = team_code,
            name = name
        )

    @database_sync_to_async
    def _bulk_save_final_scores(self, player_scores_map, player_correct_map, player_time_map, final_leaderboard):
        results = PlayerResult.objects.filter(session = self.session_record, team_code__in = player_scores_map.keys())

        for result in results:
            result.total_score = player_scores_map[result.team_code]
            result.correct_answers = player_correct_map.get(result.team_code, 0)
            result.total_time = player_time_map.get(result.team_code, 0.0)

        if results:
            PlayerResult.objects.bulk_update(results, ['total_score', 'correct_answers', 'total_time'])

        self.session_record.final_leaderboard = final_leaderboard
        self.session_record.ended_at = timezone.now()
        self.session_record.save(update_fields = ['final_leaderboard', 'ended_at'])
