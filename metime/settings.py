"""
Django settings for metime project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import enum
import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY", "django-insecure-yh(y)y1#4$m@x8$j9bfk(+!9(volqgp08fn#1h%c!_z@f*okqu"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if os.getenv("DEBUG", "false").lower() not in ("true", "yes") else True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "phonenumber_field",
    "users_app.apps.UsersAppConfig",
    "auth_app.apps.AuthAppConfig",
    "rest_framework_simplejwt",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "metime.urls"

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

WSGI_APPLICATION = "metime.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DB_NAME = os.getenv("POSTGRES_DB", "metime")
DB_USER = os.getenv("POSTGRES_USER", "metime")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "metime")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
# DB_CONNECTION_URI = (
#     f"db+postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# )

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "PORT": DB_PORT,
        "HOST": DB_HOST,
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = os.getenv("TIME_ZONE", "UTC")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

AUTH_USER_MODEL = "users_app.CustomUser"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:9999",
    f"http://localhost:{os.getenv('NGINX_PORT', '9999')}",
]
CORS_ALLOW_ALL_ORIGINS = DEBUG

SPECTACULAR_SETTINGS = {
    "TITLE": "MeTime Test API",
    "DESCRIPTION": "Test project for MeTime application",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "auth_app.backend.CustomJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "metime.permissions.IsAdminUser",
    ],
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/day",
        "user": "1000/day",
        "user_register": "1000/day",
        "user_update": "1000/day",
        "change_password": "1000/day",
        "resend_verification_code": "1000/day",
        "otp_code_verify": "1000/day",
        "token_obtain": "1000/day",
        "token_refresh": "1000/day",
        "healthcheck": "1000/day",
    },
}

PHONENUMBER_DEFAULT_REGION = os.getenv("PHONENUMBER_DEFAULT_REGION", "IR")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME_MINUTES", 60))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", 30))),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "TOKEN_OBTAIN_SERIALIZER": "auth_app.serializers.CustomTokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "auth_app.serializers.CustomTokenRefreshSerializer",
    "AUTH_TOKEN_CLASSES": ("auth_app.tokens.CustomAccessToken",),
}

AUTHENTICATION_BACKENDS = ["auth_app.backend.CustomUserAuthBackend"]

REDIS_USER = os.getenv("REDIS_USER", "default")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "foobared")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CONNECTION_URI = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CONNECTION_URI,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": False,
        },
        "KEY_FUNCTION": "metime.redis.make_key",
        "KEY_PREFIX": "METIME",
        "VERSION": 1,
    }
}

if REDIS_PASSWORD:
    CACHES["default"]["OPTIONS"]["PASSWORD"] = REDIS_PASSWORD
    REDIS_CONNECTION_URI = (
        f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
    )
    CACHES["default"]["LOCATION"] = REDIS_CONNECTION_URI

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    # TODO
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    # DEFAULT_FROM_EMAIL = "Default@MeTime.com"
    # EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    # EMAIL_USE_TLS = True
    # EMAIL_HOST = "smtp.gmail.com"
    # EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "test@gmail.com")
    # EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_USER", "password")
    # EMAIL_PORT = 587


class UserIdentifierField(enum.Enum):
    EMAIL = "email"
    PHONE = "phone"


VERIFICATION_CODE_DIGITS_COUNT = int(os.getenv("VERIFICATION_CODE_DIGITS_COUNT", 6))

VERIFICATION_EMAIL_SUBJECT = os.getenv("VERIFICATION_EMAIL_SUBJECT", "MeTime | Account Verification")
VERIFICATION_CACHE_KEY = "{user_id}-{identifier_field}-VERIFY-KEY"
VERIFICATION_TIMEOUT = 43200

RESET_PASSWORD_EMAIL_SUBJECT = os.getenv("RESET_PASSWORD_EMAIL_SUBJECT", "MeTime | Password Recovery")
RESET_PASSWORD_CACHE_KEY = "{}-RESET-PASS"
RESET_PASSWORD_TIMEOUT = 43200
