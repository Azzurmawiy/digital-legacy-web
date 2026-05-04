# config/settings.py
# Digital Legacy App — Django Settings
# Security-first configuration following Django deployment checklist
# and OWASP best practices.
#
# Sensitive values are NEVER hardcoded — loaded from .env via django-environ.

import environ
import os
from pathlib import Path
from datetime import timedelta

# ============================================================
# PATH & ENVIRONMENT SETUP
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # Declare types and defaults for all env vars
    DEBUG=(bool, False),
    SECRET_KEY=(str, ''),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    DATABASE_URL=(str, ''),
    REDIS_URL=(str, 'redis://localhost:6379/0'),
    AWS_REGION=(str, 'eu-west-1'),
    BCRYPT_ROUNDS=(int, 12),
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:5173', 'http://localhost:5174', 'http://localhost:3000']),
    JWT_ACCESS_TOKEN_LIFETIME_MINUTES=(int, 15),
    JWT_REFRESH_TOKEN_LIFETIME_DAYS=(int, 7),
    DMS_DEFAULT_THRESHOLD_DAYS=(int, 90),
    DMS_DEFAULT_COOLING_OFF_DAYS=(int, 14),
    LOG_LEVEL=(str, 'INFO'),
    SENDGRID_API_KEY=(str, ''),
    TWILIO_ACCOUNT_SID=(str, ''),
    TWILIO_AUTH_TOKEN=(str, ''),
    TWILIO_PHONE_NUMBER=(str, ''),
    AWS_ACCESS_KEY_ID=(str, ''),
    AWS_SECRET_ACCESS_KEY=(str, ''),
    AWS_S3_BUCKET_NAME=(str, 'digital-legacy-vault-dev'),
    AWS_KMS_KEY_ID=(str, ''),
    ENCRYPTION_KEY=(str, ''),
)

# Read .env file
environ.Env.read_env(BASE_DIR / '.env')

# ============================================================
# CORE DJANGO SETTINGS
# ============================================================
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# ---- Application Definition ----
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_celery_beat',
    'axes',
    'storages',                    # django-storages for S3
    'django_extensions',
]

LOCAL_APPS = [
    'core',
    'apps.authentication',
    'apps.vault',
    'apps.dms',
    'apps.beneficiary',
    'apps.notifications',
    'apps.audit',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ============================================================
# MIDDLEWARE — Order matters! Security headers first.
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',       # HTTPS/HSTS enforcement
    'corsheaders.middleware.CorsMiddleware',               # CORS (must be before CommonMiddleware)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.activity.ActivityTrackingMiddleware',  # Track user activity
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.request_id.RequestIdMiddleware',      # Inject X-Request-Id
    'core.middleware.audit.AuditMiddleware',               # Log all requests to audit trail
    'core.middleware.security_headers.SecurityHeadersMiddleware', # Extra security headers
    'axes.middleware.AxesMiddleware',                       # Account lockout (after AuthenticationMiddleware)
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ============================================================
# AUTHENTICATION BACKENDS
# ============================================================
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # Account lockout backend
    'django.contrib.auth.backends.ModelBackend',  # Default Django backend
]

# ============================================================
# DATABASE
# ============================================================
DATABASES = {
    'default': env.db('DATABASE_URL')
}
# Persistent connections for performance
DATABASES['default']['CONN_MAX_AGE'] = 60

# PostgreSQL-specific options (not applicable to SQLite)
if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
        'sslmode': 'require' if not DEBUG else 'prefer',
    }

# ============================================================
# AUTHENTICATION
# ============================================================
AUTH_USER_MODEL = 'authentication.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        # Custom validator: require uppercase, lowercase, digit, symbol
        'NAME': 'core.utils.validators.StrongPasswordValidator',
    },
]

# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'core.utils.renderers.StandardJSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.utils.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/min',
        'user': '1000/min',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'core.exceptions.handlers.custom_exception_handler',
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
}

# ============================================================
# JWT CONFIGURATION
# ============================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env('JWT_ACCESS_TOKEN_LIFETIME_MINUTES')),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env('JWT_REFRESH_TOKEN_LIFETIME_DAYS')),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

# ============================================================
# CACHING
# ============================================================
# Use Redis in production, local memory cache in development
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
else:
    # Production: Redis caching
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': env('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'RETRY_ON_TIMEOUT': True,
                'MAX_CONNECTIONS': 1000,
                'CONNECTION_POOL_KWARGS': {'max_connections': 100},
            },
            'KEY_PREFIX': 'digital_legacy',
            'TIMEOUT': 300,  # 5 minutes default
        }
    }

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ============================================================
# AXES (Account Lockout)
# ============================================================
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_LOCKOUT_URL = '/api/auth/lockout/'
AXES_RESET_ON_SUCCESS = True
AXES_VERBOSE = True

# ============================================================
# CELERY (Background Tasks — DMS Scheduler)
# ============================================================
# Use Redis in production, in-memory broker in development
if DEBUG and not env('REDIS_URL', default=''):
    # Development (without Redis): Use in-memory broker
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'rpc://'
    CELERY_TASK_ALWAYS_EAGER = True
else:
    # Production or Development with Redis: Use Redis
    CELERY_BROKER_URL = env('REDIS_URL')
    CELERY_RESULT_BACKEND = env('REDIS_URL')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Lagos'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
# Security: tasks cannot be executed with elevated permissions
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_ACKS_LATE = True

from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'check_dms_inactivity_daily': {
        'task': 'apps.dms.tasks.check_dms_inactivity',
        'schedule': crontab(minute=0, hour=0),  # Run daily at midnight
    },
}

# ============================================================
# FILE STORAGE (AWS S3 for production)
# ============================================================
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_S3_BUCKET_NAME')
AWS_S3_REGION_NAME = env('AWS_REGION')
AWS_KMS_KEY_ID = env('AWS_KMS_KEY_ID')
AWS_S3_FILE_OVERWRITE = False                    # Never overwrite existing files
AWS_DEFAULT_ACL = None                           # No public access
AWS_S3_OBJECT_PARAMETERS = {
    'ServerSideEncryption': 'aws:kms',           # KMS encryption on every upload
    'CacheControl': 'max-age=0, no-cache',       # No browser caching of vault files
}

if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_LOCATION = 'static'
    MEDIA_LOCATION = 'media'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'

# ============================================================
# SECURITY SETTINGS
# ============================================================
# HTTPS settings — enforced in production
SECURE_SSL_REDIRECT = not DEBUG
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000          # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_HSTS_SECONDS = 0
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Cookie security
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Custom encryption key (for symmetric encryption in vault)
ENCRYPTION_KEY = env('ENCRYPTION_KEY')

# For envelope encryption (recommended)
DATA_KEY_LENGTH = 32  # 256-bit

# Account lockout settings (used in auth service)
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# ============================================================
# CORS
# ============================================================
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization',
    'content-type', 'dnt', 'origin', 'user-agent',
    'x-csrftoken', 'x-requested-with', 'x-request-id',
]
CORS_EXPOSE_HEADERS = ['X-Request-Id']

# ============================================================
# DEAD MAN'S SWITCH SETTINGS
# ============================================================
DMS_DEFAULT_THRESHOLD_DAYS = env('DMS_DEFAULT_THRESHOLD_DAYS')
DMS_DEFAULT_COOLING_OFF_DAYS = env('DMS_DEFAULT_COOLING_OFF_DAYS')
DMS_ALERT_75_PERCENT = 0.75
DMS_ALERT_90_PERCENT = 0.90

# ============================================================
# NOTIFICATION SETTINGS
# ============================================================
SENDGRID_API_KEY = env('SENDGRID_API_KEY')
EMAIL_FROM = 'noreply@digitallegacy.ng'
EMAIL_FROM_NAME = 'Digital Legacy App'

TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER')

# ============================================================
# EMAIL CONFIGURATION
# ============================================================
# Use real SMTP if credentials are provided, otherwise fall back to console
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = env('EMAIL_PORT', default=587)
    EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@digitallegacy.ng')

# ============================================================
# LOGGING — Structured JSON in production
# ============================================================
LOG_LEVEL = env('LOG_LEVEL')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json' if not DEBUG else 'verbose',
        },
        'file_error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'error.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'level': 'ERROR',
            'formatter': 'json',
        },
        'file_info': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_error'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file_info', 'file_error'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file_info'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# ============================================================
# API DOCUMENTATION (drf-spectacular)
# ============================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Digital Legacy App API',
    'DESCRIPTION': 'Secure digital asset management and legacy planning platform.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
    },
    'COMPONENT_SPLIT_REQUEST': True,
}

# ============================================================
# INTERNATIONALISATION
# ============================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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