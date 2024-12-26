
from pathlib import Path
from decouple import config
import cloudinary
import cloudinary.uploader
import cloudinary.api
import sys
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

# SECURITY WARNING: do not deploy the development db!
DEVELOPMENT_DATABASE = config('DEVELOPMENT_DATABASE', default=False, cast=bool)

# Cloudinary
cloudinary.config(secure=True)  # Enforce secure connections
CLOUDINARY_URL = config('CLOUDINARY_URL')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1'
]

# Allow localhost:5173 (Frontend)
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
    ]
# TODO else: production URL here!

# Allow all HTTP methods
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    # Cloud solution for media
    'cloudinary_storage',
    'cloudinary',
    # Created apps
    'apps.users',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# SECURITY WARNING: Do not deploy the development database!
# If you need to access the production database (USE WITH CAUTION)
# in development, change the DEVELOPMENT_DATABASE environment
# variable to False. Since environment variables are configured
# in Heroku, you won't deploy the development database by mistake.
# Therefore, DO NOT access the production database by changing the
# if statement below!
if 'test' in sys.argv:  # When tests are running
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',  # Use in-memory database for tests
        }
    }
elif DEVELOPMENT_DATABASE:
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DEVELOPMENT_DATABASE_URL')
        )
    }
else:
    DATABASES = {
        'default': dj_database_url.config(default=config('DATABASE_URL'))
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
            ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static media for development
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
if DEBUG:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / "media"
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [BASE_DIR / "static"]
else:
    # Static media for production (Cloudinary)
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
