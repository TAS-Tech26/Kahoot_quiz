import os
import django
from django.utils import timezone
from datetime import timedelta
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from game.models import Quiz, GameSession, PlayerResult
from django.test import Client
from django.conf import settings

def seed_and_test():
    User = get_user_model()
    
    # 1. Seed User
    user, created = User.objects.get_or_create(
        username='testadmin',
        defaults={'is_staff': True, 'is_superuser': True, 'email': 'testadmin@example.com'}
    )
    if created:
        user.set_password('password123')
        user.save()
        print("Created test user.")

    # 2. Seed Quiz
    quiz, created = Quiz.objects.get_or_create(
        title='Test Event Quiz',
        author=user,
        defaults={'is_published': True, 'is_active': True}
    )
    if created:
        print("Created test quiz.")

    # 3. Seed GameSession for an event
    event_name = 'TestEvent2026'
    
    # Clean up previous data for idempotency
    GameSession.objects.filter(event_name=event_name).delete()
    
    session1 = GameSession.objects.create(
        pin='111111',
        quiz=quiz,
        event_name=event_name,
        ended_at=timezone.now() - timedelta(minutes=10) # Mark as ended
    )
    session2 = GameSession.objects.create(
        pin='222222',
        quiz=quiz,
        event_name=event_name,
        ended_at=timezone.now() - timedelta(minutes=5) # Mark as ended
    )
    print(f"Created 2 ended game sessions for event '{event_name}'.")

    # 4. Seed PlayerResults
    # Team A in Session 1
    PlayerResult.objects.create(
        name='Player1', total_score=1000, correct_answers=5, total_time=50.0, team_code='TEAM_A', session=session1
    )
    # Team B in Session 1
    PlayerResult.objects.create(
        name='Player2', total_score=800, correct_answers=4, total_time=60.0, team_code='TEAM_B', session=session1
    )
    # Team A in Session 2 (Team A played another game for some reason)
    PlayerResult.objects.create(
        name='Player3', total_score=1200, correct_answers=6, total_time=45.0, team_code='TEAM_A', session=session2
    )
    # Team C in Session 2
    PlayerResult.objects.create(
        name='Player4', total_score=1500, correct_answers=7, total_time=40.0, team_code='TEAM_C', session=session2
    )
    print("Created player results for teams: TEAM_A, TEAM_B, TEAM_C.")

    # 5. Test the endpoint using test client
    client = Client()
    
    print("\n--- Testing API Endpoint ---")
    url = f'/api/export-scores/{event_name}/'
    
    # Test without auth
    response = client.get(url, SERVER_NAME='localhost')
    print(f"GET (No auth) -> Status: {response.status_code}")
    
    # Test with API Key
    api_key = getattr(settings, 'KAHOOT_SECRET_KEY', '')
    response_with_key = client.get(url, headers={'X-Kahoot-API-Key': api_key}, SERVER_NAME='localhost')
    print(f"GET (With API Key) -> Status: {response_with_key.status_code}")
    
    if response_with_key.status_code == 200:
        data = response_with_key.json()
        print("\nResponse Data:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Response Error: {response_with_key.content}")
        
    print("\nTest completed.")

if __name__ == '__main__':
    seed_and_test()
