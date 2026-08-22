# settings.py


from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

import cloudinary, cloudinary.api, cloudinary.uploader, dj_database_url, os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
KAHOOT_SECRET_KEY = os.environ.get('KAHOOT_SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']


# Application definition

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

DATABASES = {
    'default': dj_database_url.config(
        default = os.environ.get('DATABASE_URL'),
        conn_max_age = 0
    )
}

DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True

CHANNEL_LAYERS = {
    'default' : {'BACKEND' : 'channels_redis.core.RedisChannelLayer', 'CONFIG' : {'hosts' : [{'address' : os.environ.get('REDIS_URL'), 'socket_timeout' : None}]}}
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES' : ['rest_framework_simplejwt.authentication.JWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES' : ['rest_framework.permissions.IsAuthenticated']
}

SIMPLE_JWT = {'ACCESS_TOKEN_LIFETIME' : timedelta(minutes = 60), 'REFRESH_TOKEN_LIFETIME' : timedelta(days = 1), 'AUTH_HEADER_TYPES' : ('Bearer',)}

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


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

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

CORS_ALLOW_ALL_ORIGINS = True