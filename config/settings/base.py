from .env import env, BASE_DIR
import dj_database_url

SECRET_KEY = env.str("SECRET_KEY")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "products",
    "images",
    "django_redis",
    "checkout",
    "cart.apps.CartConfig",
    "admin_panel",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.brand_context",
                "core.context_processors.navbar_config",
                "core.context_processors.seo_globals",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = env("DATABASE_URL")

AUTH_USER_MODEL = "accounts.User"


DATABASES = {"default": dj_database_url.parse(str(DATABASE_URL), conn_max_age=600)}

REDIS_URL = env("REDIS_URL")

REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379/1")  # type: ignore


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": env.bool("REDIS_IGNORE_EXCEPTIONS", default=True),
        },
    }
}


SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

IMAGE_STORAGE_BACKEND = env("IMAGE_STORAGE_BACKEND")


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


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Image service
IMAGE_STORAGE_BACKEND = "images.storage.LocalBackend"  # swap to S3Backend later
IMAGE_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
IMAGE_MAX_DIMENSIONS = (1920, 1920)
IMAGE_JPEG_QUALITY = 82
IMAGE_WATERMARK_OPACITY = 100  # 0–255, 40 = very light
IMAGE_WATERMARK_FONT_FRACTION = 0.08  # fraction of shorter dim
IMAGE_CACHE_TTL = 60 * 60 * 24 * 7  # 7 days
IMAGE_WATERMARK_TEXTS = {
    "dabelo": "Dabelo Café",
    "montee": "Motee Cakes",
}

SITE_NAME = "Dabelo & Motee"
SITE_URL = "https://dabelomontee.com"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# SMTP config (fill in when ready)
# EMAIL_HOST          = "smtp.sendgrid.net"
# EMAIL_PORT          = 587
# EMAIL_USE_TLS       = True
# EMAIL_HOST_USER     = "apikey"
# EMAIL_HOST_PASSWORD = env("SENDGRID_API_KEY")
# DEFAULT_FROM_EMAIL  = "Dabelo & Motee <hello@dabelomontee.com>"
