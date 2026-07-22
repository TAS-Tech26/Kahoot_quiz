# views.py


from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import GameSession, Quiz

import random


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
    session = GameSession.objects.create(quiz = quiz, pin = pin)

    return Response({'message' : "Session created successfully.", 'pin' : session.pin, 'quiz_id' : quiz.id}, status = 201)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_host_quizzes(request):
    """Allows the host to fetch a list of all available quizzes."""

    quizzes = Quiz.objects.filter(author = request.user).values('id', 'title', 'is_published')

    return Response(list(quizzes))

@api_view(['GET'])
def verify_pin(request, pin):
    if GameSession.objects.filter(pin = pin).exists():

        return Response({'valid' : True})

    return Response({'error' : "Invalid PIN"}, status = 404)