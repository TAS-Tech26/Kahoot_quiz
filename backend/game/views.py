# views.py


from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import GameSession, PlayerResult, Quiz
from .serializers import QuizSerializer

import cloudinary.utils, hmac, os, random, time


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
    event_name = request.data.get('event_name')

    if not quiz_id:

        return Response({'error' : "quiz_id is required"}, status = 400)

    if not event_name or str(event_name).strip() == '':

        return Response({'error' : "event_name is strictly required for tournament sessions."}, status = 400)
    
    try:
        quiz = Quiz.objects.get(id = quiz_id, author = request.user, is_active = True)
    except ObjectDoesNotExist:
        
        return Response({'error' : f"Quiz not found, deleted or unauthorized access."}, status = 404)
    
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

    quizzes = Quiz.objects.filter(author = request.user, is_active = True).values('id', 'title', 'is_published')

    return Response(list(quizzes))

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_quiz_detail(request, quiz_id):
    """Gets all the details of 1 specific quiz."""

    try:
        quiz = Quiz.objects.get(id = quiz_id, author = request.user, is_active = True)
    except Quiz.DoesNotExist:

        return Response({'error' : "Quiz not found."}, status = 404)

    serializer = QuizSerializer(quiz)

    return Response(serializer.data, status = 200)

@api_view(['GET'])
def verify_pin(request, pin):
    try:
        session = GameSession.objects.get(pin = pin)

        return Response({'valid' : True, 'event_name' : session.event_name})
    except GameSession.DoesNotExist:

        return Response({'error' : "Session not found or invalid PIN."}, status = 404)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_quiz(request):
    serializer = QuizSerializer(data = request.data, context = {'request' : request})

    if serializer.is_valid():
        quiz = serializer.save()

        return Response({'message' : "Quiz created successfully.", 'quiz_id' : quiz.id}, status = 201)

    return Response({'error' : serializer.errors}, status = 400)

@api_view(['GET'])
@permission_classes([AllowAny]) # Anyone can access this endpoint, but they must provide the correct KAHOOT_SECRET_KEY
def export_event_scores(request, event_name):
    # Secure authentication
    provided_key = request.headers.get('X-Kahoot-API-Key', '')
    expected_key = getattr(settings, 'KAHOOT_SECRET_KEY', '')
    is_valid_server = expected_key and hmac.compare_digest(provided_key, expected_key) 

    is_valid_host = request.user and request.user.is_authenticated and request.user.is_staff

    if not (is_valid_server or is_valid_host):

        return Response({'error' : "Unauthorized access. Invalid API key or expired host session."}, status = 403)

    # Don't export if the tournament phase is still active
    active_rooms = GameSession.objects.filter(event_name = event_name, ended_at__isnull = True)

    if active_rooms.exists():

        return Response({'error' : f"Cannot export global scores. {active_rooms.count()} room(s) are still active for {event_name}."}, status = 400)

    # Sum scores across all rooms by team_code
    results = PlayerResult.objects.filter(
        session__event_name = event_name,
        team_code__isnull = False
    ).values('team_code').annotate(
        global_score = Sum('total_score'),
        global_correct = Sum('correct_answers'),
        global_time = Sum('total_time')
    ).order_by('-global_score', '-global_correct', 'global_time', 'team_code') # Order 1st by total score, then no. of correct answers, lowest total time taken & then alphabetic fallback

    if not results:

        return Response({'error' : f"No completed data found for event: {event_name}."}, status = 404)

    return Response({'event_name' : event_name, 'total_teams' : len(results), 'scores' : list(results)}, status = 200)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_cloudinary_signature(request):
    timestamp = int(time.time())
    signature = cloudinary.utils.api_sign_request({'timestamp' : timestamp, 'folder' : 'kahoot_media'}, os.environ.get('CLOUDINARY_API_SECRET'))

    return Response({
        'signature' : signature,
        'timestamp' : timestamp,
        'api_key' : os.environ.get('CLOUDINARY_API_KEY'),
        'cloud_name' : os.environ.get('CLOUDINARY_CLOUD_NAME')
    })

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id = quiz_id)

        if quiz.author != request.user:

            return Response({'error' : "You do not have permission to delete this quiz."}, status = 403)

        quiz.is_active = False
        quiz.save(update_fields = ['is_active'])

        return Response({'message' : "Quiz deleted."}, status = 200)
    except Quiz.DoesNotExist:

        return Response({'error' : "Quiz not found"}, status = 404)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id = quiz_id, author = request.user, is_active = True)
    except Quiz.DoesNotExist:

        return Response({'error' : "Quiz not found or you don't have permission."}, status = 404)

    serializer = QuizSerializer(quiz, data = request.data, context = {'request' : request})

    if serializer.is_valid():
        updated_quiz = serializer.save()

        return Response({'message' : "Quiz updated successfully.", 'quiz_id' : updated_quiz.id}, status = 200)

    return Response({'error' : serializer.errors}, status = 400)