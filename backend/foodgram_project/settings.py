import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", default=False)

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.auth.hashers',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'djoser',
    'users',
    'recipes',
    'api',
    'colorfield',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram_project.urls'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.environ.get(
            'DB_ENGINE', default="django.db.backends.postgresql"),
        'NAME': os.environ.get(
            'DB_NAME', default="postgres"),
        'USER': os.environ.get(
            'POSTGRES_USER', default="ostgres"),
        'PASSWORD': os.environ.get(
            'POSTGRES_PASSWORD', default="postgres"),
        'HOST': os.environ.get(
            'DB_HOST', default="db"),
        'PORT': os.environ.get(
            'DB_PORT', default="5432"),
    }
}

AUTH_USER_MODEL = 'users.User'

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


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],

    # 'DEFAULT_PAGINATION_CLASS':
    #     'api.paginators.CustomPageNumberPaginator',
    # 'PAGE_SIZE': 6,
}

DJOSER = {
    'SERIALIZERS': {
        'user': 'api.serializers.UserSerializer',
        'current_user': 'api.serializers.UserSerializer',
        'user_create': 'api.serializers.CustomUserCreateSerializer',
        'token_create': 'api.serializers.CustomTokenCreateSerializer',
    },
    'LOGIN_FIELD': 'email',
}

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", default='en')

TIME_ZONE = os.environ.get("TIME_ZONE", default='Europe/Moscow')

USE_I18N = True

USE_L10N = True

USE_TZ = True
