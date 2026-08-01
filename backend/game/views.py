# views.py


from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import GameSession, PlayerResult, Quiz

import hmac, random


def generate_unique_pin():
    """Generates a 6-digit PIN & guarantees it currently doesn't exist."""

    while True:
        pin = str(random.randint(100000, 999999))

        if not GameSession.objects.filter(pin = pin).exists():

            return pin
        

@api_view(['POST'])
@permission_classes([IsAdminUser]) # Rejects anyone where is_staff = False
def create_game_session(request):
    quiz_id = request.data.get('quiz_id')

    event_name = request.data.get('event_name', 'standard')

    if not quiz_id:

        return Response({'error' : "quiz_id is required"}, status = 400)
    
    try:
        quiz = Quiz.objects.get(id = quiz_id, author = request.user)
    except ObjectDoesNotExist:
        
        return Response({'error' : f"Quiz not found or unauthorized access."}, status = 404)
    
    # Check if the compiled payload exists & if it has Qs in it
    if not quiz.compiled_data or not quiz.compiled_data.get('questions'):
        quiz.compile_for_redis() # If not, trigger the compiler

        if not quiz.compiled_data.get('questions'):

            return Response({'error' : "Cannot start a game. The quiz contains zero questions."}, status = 400)
    
    pin = generate_unique_pin()
    session = GameSession.objects.create(quiz = quiz, pin = pin, event_name = event_name)

    return Response({'message' : "Session created successfully.", 'pin' : session.pin, 'quiz_id' : quiz.id, 'event_name' : session.event_name}, status = 201)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_host_quizzes(request):
    """Allows the host to fetch a list of all available quizzes."""

    quizzes = Quiz.objects.filter(author = request.user).values('id', 'title', 'is_published')

    return Response(list(quizzes))

@api_view(['GET'])
def verify_pin(request, pin):
    try:
        session = GameSession.objects.get(pin = pin)

        return Response({'valid' : True, 'event_name' : session.event_name})
    except GameSession.DoesNotExist:

        return Response({'error' : "Session not found or invalid PIN."}, status = 404)

@api_view(['GET'])
@permission_classes([AllowAny]) # Anyone can access this endpoint, but they must provide the correct KAHOOT_SECRET_KEY
def export_event_scores(request, event_name):
    # Secure authentication
    provided_key = request.headers.get('X-Kahoot-API-Key', '')
    expected_key = getattr(settings, 'KAHOOT_SECRET_KEY', '')

    if not expected_key or not hmac.compare_digest(provided_key, expected_key):

        return Response({'error' : "Unauthorized server access."}, status = 403)

    # Don't export if the tournament phase is still active
    active_rooms = GameSession.objects.filter(event_name = event_name, ended_at__isnull = True)

    if active_rooms.exists():

        return Response({'error' : f"Cannot export global scores. {active_rooms.count()} room(s) are still active for {event_name}."}, status = 400)

    # Sum scores across all rooms by team_code
    results = PlayerResult.objects.filter(
        session__event_name = event_name,
        team_code__isnull = False
    ).values('team_code').annotate(global_score = Sum('total_score')).order_by('-global_score')

    if not results:

        return Response({'error' : f"No completed data found for event: {event_name}."}, status = 404)

    return Response({'event_name' : event_name, 'total_teams' : len(results), 'scores' : list(results)}, status = 200)