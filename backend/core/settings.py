# settings.py


from dotenv import load_dotenv
from pathlib import Path

import cloudinary, dj_database_url, os


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
KAHOOT_SECRET_KEY = os.environ.get('KAHOOT_SECRET_KEY')
HUB_SECRET_KEY = os.environ.get('HUB_SECRET_KEY') # For HubJWTAuthentication
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'channels',
    'game'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application' # Enables WebSockets

DATABASES = {'default': dj_database_url.config(default = os.environ.get('DATABASE_URL'), conn_max_age = 0)}

DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True

CHANNEL_LAYERS = {
    'default' : {
        'BACKEND' : 'channels_redis.core.RedisChannelLayer',
        'CONFIG' : {'hosts' : [{'address' : os.environ.get('REDIS_URL', 'redis://127.0.0.1:6380/1'), 'socket_timeout' : None}]}
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES' : ['game.authentication.HubJWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES' : ['rest_framework.permissions.IsAuthenticated']
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default' : {'BACKEND' : 'django.core.files.storage.FileSystemStorage'},
    'staticfiles' : {'BACKEND' : 'whitenoise.storage.CompressedManifestStaticFilesStorage'}
}

cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure = True
)

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = ['http://localhost:5173']