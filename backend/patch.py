import os

def patch_file(path, replacements):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        for old, new in replacements:
            content = content.replace(old, new)
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched {path}")
    except Exception as e:
        print(f"Error patching {path}: {e}")

# settings.py
settings_path = r"d:\Projects\Kahoot_quiz\Kahoot_app\backend\core\settings.py"
settings_reps = [
    ("DEBUG = os.environ.get('DEBUG', 'True') == 'True'", "DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'"),
    ("ALLOWED_HOSTS = ['127.0.0.1', 'localhost']", "ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')"),
    ("HUB_SECRET_KEY = os.environ.get('HUB_SECRET_KEY') # For HubJWTAuthentication\n\nDEBUG", "HUB_SECRET_KEY = os.environ.get('HUB_SECRET_KEY') # For HubJWTAuthentication\n\nif not SECRET_KEY or not KAHOOT_SECRET_KEY or not HUB_SECRET_KEY:\n    raise ValueError('Missing critical SECRET_KEY environment variables.')\n\nDEBUG"),
    ("'DEFAULT_PERMISSION_CLASSES' : ['rest_framework.permissions.IsAuthenticated']\n}", "'DEFAULT_PERMISSION_CLASSES' : ['rest_framework.permissions.IsAuthenticated'],\n    'DEFAULT_THROTTLE_CLASSES': [\n        'rest_framework.throttling.AnonRateThrottle',\n        'rest_framework.throttling.UserRateThrottle'\n    ],\n    'DEFAULT_THROTTLE_RATES': {\n        'anon': '100/day',\n        'user': '1000/day'\n    }\n}"),
    ("CORS_ALLOW_ALL_ORIGINS = False", "CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'"),
    ("CORS_ALLOWED_ORIGINS = ['http://localhost:5173']", "CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')\nCSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:5173').split(',')")
]
patch_file(settings_path, settings_reps)

# handlers.py
handlers_path = r"d:\Projects\Kahoot_quiz\Kahoot_app\backend\game\handlers.py"
handlers_reps = [
    ("return GameSession.objects.select_related('quiz').get(pin = pin)\n            return GameSession.objects.select_related('quiz').get(pin = pin, ended_at__isnull = True)", "return GameSession.objects.select_related('quiz').get(pin = pin, ended_at__isnull = True)"),
    ("hub_secret = os.environ.get('HUB_SECRET_KEY')", "hub_secret = getattr(settings, 'HUB_SECRET_KEY', '')"),
    ("has_answered = await self.redis.sismember(f\"game:{self.pin}:answered:{current_q['id']}\", team_code)", "has_answered = await self.redis.has_player_answered(current_q['id'], team_code)")
]
patch_file(handlers_path, handlers_reps)

# redis_service.py
redis_path = r"d:\Projects\Kahoot_quiz\Kahoot_app\backend\game\redis_service.py"
redis_reps = [
    ("if keys:\n                await redis_client.delete(*keys)", "if keys:\n                await redis_client.delete(*keys)\n            if cursor == 0 or cursor == '0':\n                break")
]
patch_file(redis_path, redis_reps)

