import dj_database_url

from .env import BASE_DIR, env

SECRET_KEY = env.str("SECRET_KEY")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_redis",
    # apps
    "apps.accounts",
    "apps.products.apps.ProductsConfig",
    "apps.images",
    "apps.checkout",
    "apps.cart.apps.CartConfig",
    "apps.admin_panel",
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
ASGI_APPLICATION = "config.asgi.application"


POSTGRES_DB = env.str("POSTGRES_DB")
POSTGRES_USER = env.str("POSTGRES_USER")
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
POSTGRES_HOST = env.str("POSTGRES_HOST")
POSTGRES_PORT = env.str("POSTGRES_PORT")


DATABASE_URL = (
    f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

AUTH_USER_MODEL = "accounts.User"

DATABASES = {"default": dj_database_url.parse(str(DATABASE_URL), conn_max_age=600)}

REDIS_URL = env("REDIS_URL")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
    }
}


SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
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
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR.parent / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_FROM_EMAIL = env.str(
    "DEFAULT_FROM_EMAIL",
    default="Dabelo & Motee <hello@dabelomontee.com>",
)

SITE_ID = 1
SITE_NAME = "Dabelo & Motee"
SITE_URL = env.str("SITE_URL", default="https://dabelomontee.com")
TWITTER_SITE = env.str("TWITTER_SITE", default="@dabelomontee")
DEFAULT_OG_IMAGE = "/static/img/og-default.jpg"

PAYSTACK_PUBLIC_KEY = env.str("PAYSTACK_PUBLIC_KEY")
PAYSTACK_SECRET_KEY = env.str("PAYSTACK_SECRET_KEY")

IMAGE_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
IMAGE_CACHE_TTL = 60 * 60 * 24 * 7  # 7 days

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Image service
IMAGE_STORAGE_BACKEND = "apps.images.storage.LocalBackend"
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

SUPERADMIN_EMAIL = env.str("SUPERADMIN_EMAIL")
SUPERADMIN_PASSWORD = env.str("SUPERADMIN_PASSWORD")
SUPERADMIN_FIRST_NAME = env.str("SUPERADMIN_FIRST_NAME")
SUPERADMIN_LAST_NAME = env.str("SUPERADMIN_LAST_NAME")
