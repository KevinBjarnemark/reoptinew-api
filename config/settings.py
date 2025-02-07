import os
import sys
from datetime import timedelta
from pathlib import Path
from decouple import config
import cloudinary
import cloudinary.uploader
import cloudinary.api
import dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)

# SECURITY WARNING: do not deploy the development db!
DEVELOPMENT_DATABASE = config("DEVELOPMENT_DATABASE", default=False, cast=bool)

# Cloudinary
cloudinary.config(secure=True)  # Enforce secure connections
CLOUDINARY_URL = config("CLOUDINARY_URL")

# Enable or disable all debug logs executed by static/py/utils/logging.py.
SHOW_ALL_LOGS = config("SHOW_ALL_LOGS", default=False, cast=bool)

dev_server_host = config("DEV_SERVER_HOST")
dev_server_frontend_port = config("DEV_SERVER_FRONTEND_PORT")

if DEBUG:
    # Allow localhost in development
    CORS_ALLOWED_ORIGINS = [
        f"http://{dev_server_host}:{int(dev_server_frontend_port)}"
    ]
    ALLOWED_HOSTS = [dev_server_host]
else:
    # Allow the deployed frontend in production
    CORS_ALLOWED_ORIGINS = [
        "https://reoptinew-09d333f23d8e.herokuapp.com",
    ]
    ALLOWED_HOSTS = ["reoptinew-api-c16dc2520739.herokuapp.com"]

# Allow all HTTP methods
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

AUTH_USER_MODEL = "users.User"

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    # Cloud solution for media
    "cloudinary_storage",
    "cloudinary",
    # Created apps
    "apps.users",
    "apps.posts",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CORS
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        # Detailed logs for error tracking (saved in error.log)
        "file_error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "error.log"),
            "formatter": "verbose",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,  # Keep the last 5 files
        },
        # Detailed logs for debugging (saved in debug.log)
        "file_debug": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "debug.log"),
            "formatter": "verbose",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
        },
        # Minimal logs for terminal output during development
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file_error", "console"],
            "level": "ERROR",
            "propagate": True,
        },
        "app": {
            "handlers": ["file_debug", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# SECURITY WARNING: Do not deploy the development database!
# If you need to access the production database (USE WITH CAUTION)
# in development, change the DEVELOPMENT_DATABASE environment
# variable to False. Since environment variables are configured
# in Heroku, you won't deploy the development database by mistake.
# Therefore, DO NOT access the production database by changing the
# if statement below!
if "test" in sys.argv:  # When tests are running
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",  # Use in-memory database for tests
        }
    }
elif DEVELOPMENT_DATABASE:
    DATABASES = {
        "default": dj_database_url.config(
            default=config("DEVELOPMENT_DATABASE_URL")
        )
    }
else:
    DATABASES = {
        "default": dj_database_url.config(default=config("DATABASE_URL"))
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation." "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Static media for development
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
if DEBUG:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
else:
    # Static media for production (Cloudinary)
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
