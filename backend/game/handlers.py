# handlers.py


from channels.db import database_sync_to_async
from django.utils import timezone

from .models import GameSession, PlayerResult
from .serializers import PlayerJoinSerializer
from .redis_service import GameRedisManager

import json, time, uuid


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
        if hasattr(self.consumer, 'player_id'):
            await self.redis.remove_active_player(self.consumer.player_id)

            total_players = await self.redis.get_active_players_count()

            await self.consumer.channel_layer.group_send(
                self.consumer.room_group_name,
                {'type' : 'broadcast_event', 'event_type' : 'player_left', 'data' : {'total_players' : total_players}}
            )

    async def handle_host_start(self):
        quiz_data = await self._get_compiled_quiz_data()
        first_question = quiz_data['questions'][0]

        await self.redis.initialise_game_start(first_question['id'], quiz_data)

        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
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
        provided_id = data.get('player_id')

        if provided_id:
            existing_name = await self.redis.get_player_name(provided_id)

            if existing_name:
                self.consumer.player_id = provided_id

                await self.redis.add_active_player(provided_id)

                total_players = await self.redis.get_active_players_count()

                await self.consumer.send_json({'event_type' : 'rejoin_success', 'player_id' : provided_id, 'name' : existing_name})
                await self.consumer.channel_layer.group_send(
                    self.consumer.room_group_name,
                    {'type' : 'broadcast_event', 'event_type' : 'player_joined', 'data' : {'name' : existing_name, 'total_players' : total_players}}
                )

                return

        serializer = PlayerJoinSerializer(data = data)

        if not serializer.is_valid():
            await self.consumer.send_json({'event_type' : 'error', 'message' : serializer.errors})

            return

        validated_data = serializer.validated_data

        new_player_id = str(uuid.uuid4())
        self.consumer.player_id = new_player_id

        await self.redis.register_new_player(new_player_id, validated_data['full_name'])

        total_players = await self.redis.get_active_players_count()

        await self.create_player_result(new_player_id, validated_data)

        await self.consumer.send_json({'event_type' : 'join_success', 'player_id' : new_player_id})
        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
            {'type' : 'broadcast_event', 'event_type' : 'player_joined', 'data' : {'name' : validated_data['full_name'], 'total_players' : total_players}}
        )

    async def handle_submit_answer(self, data):
        if not hasattr(self.consumer, 'player_id'):

            return

        choice_id = data.get('choice_id')

        state = await self.redis.get_state()

        if state.get('status') != 'active':

            return

        question_id = int(state.get('current_question_id'))
        start_time = float(state.get('start_time'))

        if not await self.redis.mark_player_answered(question_id, self.consumer.player_id):

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

            await self.redis.increment_player_score(self.consumer.player_id, points_earned)

        total_answers = self.redis.get_answered_count(question_id)

        await self.consumer.send_json({'event_type' : 'answer_result', 'data' : {'is_correct' : is_correct, 'points_earned' : points_earned}})
        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
            {'type' : 'broadcast_event', 'event_type' : 'answer_registered', 'data' : {'total_answers' : total_answers}}
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

        await self.redis.update_state_for_next_question(next_index, next_question['id'])

        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
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

    async def _handle_end_game(self):
        raw_scores = await self.redis.get_final_scores()

        final_leaderboard = []
        player_scores_map = {}

        for player_id, score in raw_scores:
            name = await self.redis.get_player_name(player_id)

            score_int = int(score)

            final_leaderboard.append({'name' : name, 'score' : score_int, 'player_id' : player_id})

            player_scores_map[player_id] = score_int

        await self.consumer.channel_layer.group_send(
            self.consumer.room_group_name,
            {'type' : 'broadcast_event', 'event_type' : 'game_over', 'data' : {'leaderboard' : final_leaderboard[:5]}}
        )

        if player_scores_map:
            await self._bulk_save_final_scores(player_scores_map, final_leaderboard)

        await self.redis.cleanup_game_data()

    # --- DB Readers/Writers
    @database_sync_to_async
    def _get_game_session(self, pin):
        try:

            return GameSession.objects.get(pin = pin)
        
        except GameSession.DoesNotExist:

            return None

    @database_sync_to_async
    def _get_compiled_quiz_data(self):

        return self.session_record.quiz.compiled_data

    @database_sync_to_async
    def _create_player_result(self, player_id, validated_data):
        PlayerResult.objects.create(
            session = self.session_record,
            player_id = player_id,
            full_name = validated_data['full_name'],
            contact_info = validated_data['contact_info'],
            school_name = validated_data['school_name'],
            grade_level = validated_data['grade_level']
        )

    @database_sync_to_async
    def _bulk_save_final_scores(self, player_scores_map, final_leaderboard):
        results = PlayerResult.objects.filter(session = self.session_record, player_id__in = player_scores_map.keys())

        for result in results:
            result.total_score = player_scores_map[result.player_id]

        if results:
            PlayerResult.objects.bulk_update(result, ['total_score'])

        self.session_record.final_leaderboard = final_leaderboard
        self.session_record.ended_at = timezone.now()
        self.session_record.save(update_fields = ['final_leaderboard', 'ended_at'])
