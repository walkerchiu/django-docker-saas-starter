"""
Django settings for app project.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
from ssm_parameter_store import EC2ParameterStore
import django
import environ
import os

from django.utils.encoding import force_str

from corsheaders.defaults import default_headers


django.utils.encoding.force_text = force_str


# set casting, default value
env = environ.Env(
    DEBUG=(bool, False),
    PLAYGROUND=(bool, True),
    JWT_EXPIRATION_MINUTES=(int, 60),
    JWT_REFRESH_EXPIRATION_DAYS=(int, 7),
    JWT_REVOKE_AND_REFRESH=(bool, True),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

APP_DOMAIN = env("APP_DOMAIN")
APP_ENV = env("APP_ENV")
APP_NAME = env("APP_NAME")


AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")


# Get parameters and populate os.environ (region not required if AWS_DEFAULT_REGION environment variable set)
if APP_ENV in ["dev", "staging", "prod"]:
    parameter_store = EC2ParameterStore(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=env("AWS_SSM_REGION_NAME"),
    )
    django_parameters = parameter_store.get_parameters_by_path(
        "/" + APP_ENV + "/", strip_path=True, recursive=True
    )
    EC2ParameterStore.set_env(django_parameters)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't enable the following settings in production!
DEBUG = env("DEBUG")
PLAYGROUND = env("PLAYGROUND")

WSGI_APPLICATION = "app.wsgi.application"


# Application definition

# Multitenancy
# https://django-tenants.readthedocs.io/en/latest/

SHARED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "corsheaders",
    "django_tenants",
    "graphene_django",
    "rest_framework",
    "safedelete",
    "tenant",
)

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

PUBLIC_SCHEMA_NAME = "public"

TENANT_APPS = (
    "graphql_jwt.refresh_token.apps.RefreshTokenConfig",
    "account",
    "organization",
    "role",
)

TENANT_DOMAIN_MODEL = "tenant.Domain"

TENANT_MODEL = "tenant.Tenant"

INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]


# Route
# https://docs.djangoproject.com/en/4.1/topics/http/urls/

ROOT_URLCONF = "app.urls"
APPEND_SLASH = False


# ALLOWED_HOSTS
# https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts

ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(" ")


# Middleware
# https://docs.djangoproject.com/en/4.1/topics/http/middleware/

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.DepthCheckMiddleware",
    "core.middleware.HealthCheckMiddleware",
    "tenant.middleware.XTenantMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": env("SQL_ENGINE"),
        "NAME": env("SQL_DATABASE"),
        "USER": env("SQL_USER"),
        "PASSWORD": env("SQL_PASSWORD"),
        "HOST": env("SQL_HOST"),
        "PORT": env("SQL_PORT"),
    }
}


# Cache
# https://docs.djangoproject.com/en/4.1/topics/cache/

if APP_ENV in ["dev", "staging", "prod"]:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env("AWS_CACHE_ENDPOINT"),
            "OPTIONS": {
                # ElastiCache: RedisCluster(Cluster mode: On)
                # "REDIS_CLIENT_CLASS": "rediscluster.RedisCluster",
                # "CONNECTION_POOL_CLASS": "rediscluster.connection.ClusterConnectionPool",
                # "CONNECTION_POOL_KWARGS": {"skip_full_coverage_check": True},
                # ElastiCache: RedisCluster(Cluster mode: Off)
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }


# CORS
# https://pypi.org/project/django-cors-headers/

CORS_URLS_REGEX = r"^/(api|auth|dashboard)/.*$"

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https?://(\w+\.)?localhost:3000$",
]

CORS_ALLOW_METHODS = [
    "GET",
    "OPTIONS",
    "POST",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "X-Tenant",
]


# GraphQL
# https://docs.graphene-python.org/en/latest/quickstart/
# https://django-graphql-jwt.domake.io/

GRAPHENE = {
    "ATOMIC_MUTATIONS": True,
    "CAMELCASE_ERRORS": True,
    # By default GraphiQL headers editor tab is enabled, set to False to hide it
    # This sets headerEditorEnabled GraphiQL option, for details go to
    # https://github.com/graphql/graphiql/tree/main/packages/graphiql#options
    "GRAPHIQL_HEADER_EDITOR_ENABLED": True,
    "GRAPHIQL_SHOULD_PERSIST_HEADERS": False,
    "MIDDLEWARE": [
        "core.graphql_jwt.middleware.JSONWebTokenMiddleware",
        "account.graphql.middleware.LoaderMiddleware",
        "tenant.graphql.middleware.LoaderMiddleware",
    ],
    # Set to True if the connection fields must have
    # either the first or last argument
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": False,
    # Max items returned in ConnectionFields / FilterConnectionFields
    "RELAY_CONNECTION_MAX_LIMIT": 100,
    "SCHEMA": "django_root.schema.schema",
    "SCHEMA_INDENT": 2,
    "SCHEMA_OUTPUT": "schema.json",
    "TESTING_ENDPOINT": "/graphql",
}

GRAPHENE_MAX_BREADTH = 1
GRAPHENE_MAX_DEPTH = 18

GRAPHQL_JWT = {
    "JWT_ALGORITHM": "HS256",
    "JWT_ALLOW_ARGUMENT": True,
    "JWT_ALLOW_REFRESH": True,
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_EXPIRATION_DELTA": timedelta(
        minutes=int(os.environ["JWT_EXPIRATION_MINUTES"])
    ),
    "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
    "JWT_PAYLOAD_HANDLER": "core.graphql_jwt.utils.jwt_payload",
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(
        days=int(os.environ["JWT_REFRESH_EXPIRATION_DAYS"])
    ),
    "JWT_REUSE_REFRESH_TOKENS": True,
    "JWT_SECRET_KEY": SECRET_KEY,
    "JWT_VERIFY_EXPIRATION": True,
}


# Authentication
# https://docs.djangoproject.com/en/4.1/topics/auth/

AUTH_USER_MODEL = "account.User"

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]


# Templates
# https://docs.djangoproject.com/en/4.1/topics/templates/

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

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Storage
# https://docs.djangoproject.com/en/4.1/ref/settings/#media-root

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "storage")


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# DATA_UPLOAD_MAX_MEMORY_SIZE
# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-DATA_UPLOAD_MAX_MEMORY_SIZE

DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400

# FILE_UPLOAD_MAX_MEMORY_SIZE
# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-FILE_UPLOAD_MAX_MEMORY_SIZE

FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400


# DEFAULT_FILE_STORAGE
# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-DEFAULT_FILE_STORAGE

if APP_ENV in ["dev", "staging", "prod"]:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
AWS_S3_SIGNATURE_VERSION = env("AWS_S3_SIGNATURE_VERSION")
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=" + str(env("AWS_QUERYSTRING_EXPIRE")),
}
AWS_QUERYSTRING_EXPIRE = env("AWS_QUERYSTRING_EXPIRE")
