import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV = os.getenv(
    "DJANGO_SETTINGS_MODULE",
    "config.settings.develop",
).rsplit(
    ".", maxsplit=1
)[-1]

load_dotenv(BASE_DIR / f"environments/{ENV}/.app.env")

SECRET_KEY = os.getenv("SECRET_KEY")
JWT_SIGNING_KEY = os.environ.get("JWT_SIGNING_KEY", SECRET_KEY)
JWT_PAYLOAD_ENCRYPTION_KEY = os.environ.get("JWT_PAYLOAD_ENCRYPTION_KEY", SECRET_KEY)

DEBUG = os.getenv("DEBUG", True)

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

AUTH_USER_MODEL = "users.User"

INSTALLED_APPS = [
    # Django
    "jazzmin",  # this package must be upper then django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "django_json_widget",
    "django_extensions",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "gears",
    # Business logic
    "apps.users",
    "apps.core",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DB_URL = os.environ.get("DB_URL")
DATABASES = {"default": dj_database_url.config(default=DB_URL)}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": i}
    for i in (
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "django.contrib.auth.password_validation.MinimumLengthValidator",
        "django.contrib.auth.password_validation.CommonPasswordValidator",
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    )
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAdminUser",),
    "DEFAULT_RENDERER_CLASSES": ("gears.renderers.renderer.APIRenderer",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "EXCEPTION_HANDLER": "gears.renderers.exception_handlers.exception_handler",
}

# SIMPLE_JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        hours=int(os.getenv("ACCESS_TOKEN_LIFETIME", 2))
    ),
    "REFRESH_TOKEN_TIMELINE": timedelta(
        hours=int(os.getenv("REFRESH_TOKEN_TIMELINE", 24 * 30))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "SIGNING_KEY": JWT_SIGNING_KEY,
}

# CORS
CORS_ALLOW_ALL_ORIGINS = bool(os.getenv("CORS_ALLOW_ALL_ORIGINS", True))
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = (
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "stripe_signature",
    "Project",
)

# LOGGING

LOGS_ROOT = BASE_DIR / "logs"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOGS_ROOT / "default_logger.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "default": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# REDIS SETTINGS #

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = {
    "production": 0,
    "staging": 1,
    "development": 2,
    "test": 3,
}[ENV]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": [
            f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        ],
        "TIMEOUT": 24 * 60 * 60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.HerdClient",
        },
    },
}

JAZZMIN_SETTINGS = {
    "usermenu_links": [
        {"name": "Redoc UI", "url": "/redoc/", "new_window": True},
        {"name": "Swagger UI", "url": "/doc/", "new_window": True},
        {"name": "Swagger YAML", "url": "/doc.yaml", "new_window": True},
        {"name": "Swagger JSON", "url": "/doc.json", "new_window": True},
    ],
    "icons": {
        "users.user": "fas fa-user",
        "users.appraiser": "fas fa-comments-dollar",
        "users.customer": "fas fa-address-card",
        "users.lawyer": "fas fa-user-graduate",
        "users.realtor": "fas fa-user-graduate",
        "auth.group": "fas fa-users",
        "codes.code": "fas fa-barcode",
        "filemanager.form": "fas fa-address-card",
        "filemanager.template": "fas fa-id-card",
        "register.bank": "fas fa-landmark",
        "register.location": "fas fa-map",
        "roadmap.customerstep": "fas fa-route",
        "flow.flowobject": "fas fa-code-branch",
        "flow.observertask": "fas fa-clock",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
}

# JUPYTER
SHELL_PLUS = "ipython"
SHELL_PLUS_PRINT_SQL = False
NOTEBOOK_ARGUMENTS = [
    "--ip",
    "0.0.0.0",
    "--port",
    "8888",
    "--allow-root",
    "--no-browser",
]
IPYTHON_ARGUMENTS = [
    "--ext",
    "django_extensions.management.notebook_extension",
    "--debug",
]
IPYTHON_KERNEL_DISPLAY_NAME = "Django Shell-Plus"
SHELL_PLUS_POST_IMPORTS = [
    # ("module1.submodule", ("func1", "func2", "class1", "etc")),
    # ("module2.submodule", ("func1", "func2", "class1", "etc")),
]

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {"JWT": {"type": "jwt"}},
}
SWAGGER_USE_COMPAT_RENDERERS = False
