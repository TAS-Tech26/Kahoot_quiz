
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from game.models import PlayerResult, GameSession, Quiz
from django.contrib.auth.models import User
import django.utils.timezone
import random

user, _ = User.objects.get_or_create(username='admin')
quiz, _ = Quiz.objects.get_or_create(title='test', defaults={'author': user})

# Ensure unique pin to avoid IntegrityError
pin = str(random.randint(100000, 999999))
while GameSession.objects.filter(pin=pin).exists():
    pin = str(random.randint(100000, 999999))

session = GameSession.objects.create(pin=pin, quiz=quiz, event_name='Bid2Build')

PlayerResult.objects.get_or_create(
    session=session,
    team_code='2SJ7T4',
    defaults={'total_score': 500, 'correct_answers': 5, 'total_time': 100, 'name': 'E2E Team'}
)
session.ended_at = django.utils.timezone.now()
session.save()
