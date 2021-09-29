"""
Django settings for warehouse project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import sys
import os
import sentry_sdk
import requests
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "..", "..", "environments"))
from project import create_configuration_and_session, MODE, CONTEXT, PROJECT
from utils.packaging import get_package_info
from utils.logging import ElasticsearchHandler, create_elasticsearch_handler

# We're adding the environments directory outside of the project directory to the path
# That way we can load the environments and re-use them in different contexts
# Like maintenance tasks and harvesting tasks
PACKAGE_INFO = get_package_info()
environment, session = create_configuration_and_session(service='service')
IS_AWS = environment.aws.is_aws

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environment.secrets.django.secret_key

DOMAIN = environment.django.domain
PROTOCOL = environment.django.protocol
BASE_URL = "{}://{}".format(PROTOCOL, DOMAIN)
try:
    response = requests.get("https://api.ipify.org/?format=json")
    IP = response.json()["ip"]
except Exception:
    IP = None

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = environment.django.debug

# We're disabling the ALLOWED_HOSTS check, because containers will run in a VPC environment
# This environment is expected to be unreachable with disallowed hosts.
# It hurts to have this setting enabled on AWS, because health checks don't pass the domain check.
ALLOWED_HOSTS = ["*"]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# list of allowed endpoints to redirect
ALLOWED_REDIRECT_HOSTS = [
    BASE_URL
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'ckeditor',
    'mptt',
    'social_django',

    'rest_framework',
    'django_filters',

    'surf.vendor.surfconext',

    'surf',
    'surf.apps.core',
    'surf.apps.users',
    'surf.apps.filters',
    'surf.apps.materials',
    'surf.apps.communities',
    'surf.apps.themes',
    'surf.apps.stats',
    'surf.apps.locale',
]

SESSION_COOKIE_SECURE = PROTOCOL == "https"
CSRF_COOKIE_SECURE = PROTOCOL == "https"

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'", "'unsafe-eval'", "https://webstats.surf.nl"]
CSP_IMG_SRC = ["'self'", "data:"]
CSP_CONNECT_SRC = ["'self'", "https://webstats.surf.nl"]
if MODE != 'localhost':
    CSP_IMG_SRC.append(f"{environment.aws.image_upload_bucket}.s3.amazonaws.com")
    CSP_IMG_SRC.append(f"{environment.aws.harvest_content_bucket}.s3.amazonaws.com")

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'surf.urls'


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "surf.settings.jinja2.environment",
            "extensions": [
                "webpack_loader.contrib.jinja2ext.WebpackExtension",
            ],
        }
    },
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


WSGI_APPLICATION = 'surf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environment.postgres.database,
        'USER': environment.postgres.user,
        'PASSWORD': environment.secrets.postgres.password,
        'HOST': environment.postgres.host,
        'PORT': environment.postgres.port,
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# Django Rest Framework
# https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'surf.apps.core.pagination.SurfPageNumberPagination',
    'PAGE_SIZE': 20,

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'surf.apps.users.authentication.SessionTokenAuthentication',
    ),

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ),

}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '..', '..', 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_ALLOW_ALL_ORIGINS = True
STATICFILES_DIRS = []


# Media uploads

if MODE != 'localhost':
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = environment.aws.image_upload_bucket
    AWS_S3_REGION_NAME = 'eu-central-1'

AWS_HARVESTER_BUCKET_NAME = environment.aws.harvest_content_bucket

MEDIA_ROOT = os.path.join(BASE_DIR, '..', '..', 'media')
MEDIA_URL = '/media/'


# Django Webpack loader
# https://github.com/owais/django-webpack-loader

PORTAL_BASE_DIR = os.path.join(STATIC_ROOT, "portal") if CONTEXT == 'container' else \
    os.path.join(BASE_DIR, "apps", "materials", "static", "portal")

if not os.path.exists(PORTAL_BASE_DIR):
    os.makedirs(PORTAL_BASE_DIR)

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': PORTAL_BASE_DIR + os.sep,  # must end with slash
        'STATS_FILE': os.path.join(PORTAL_BASE_DIR, 'webpack-stats.json'),
    }
}


# Logging
# https://docs.djangoproject.com/en/2.2/topics/logging/
# https://docs.sentry.io/

MATOMO_ID = environment.django.matomo_id

_logging_enabled = sys.argv[1:2] != ['test']
_log_level = environment.django.logging.level if _logging_enabled else 'CRITICAL'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'es_service': create_elasticsearch_handler(
            'service-logs',
            ElasticsearchHandler.IndexNameFrequency.WEEKLY,
            environment,
            session
        ),
    },
    'loggers': {
        'service': {
            'handlers': ['es_service'] if environment.django.logging.is_elastic else ['console'],
            'level': _log_level,
            'propagate': True,
        }
    },
}

if not DEBUG:

    def strip_sensitive_data(event, hint):
        user_agent = event.get('request', {}).get('headers', {}).get('User-Agent', None)

        if user_agent:
            del event['request']['headers']['User-Agent']

        return event

    # Initiates sentry without sending personal data
    sentry_sdk.init(
        before_send=strip_sensitive_data,
        dsn="https://21fab3e788584cbe999f20ea1bb7e2df@sentry.io/2964956",
        environment=environment.env,
        integrations=[DjangoIntegration()]
    )

    # We kill all DisallowedHost logging on the servers,
    # because it happens so frequently that we can't do much about it
    ignore_logger('django.security.DisallowedHost')


# Social Auth
# https://python-social-auth.readthedocs.io/en/latest/index.html

AUTH_USER_MODEL = 'users.User'

SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_SURF_CONEXT_OIDC_ENDPOINT = environment.surfconext.oidc_endpoint
SOCIAL_AUTH_LOGIN_ERROR_URL = BASE_URL
SOCIAL_AUTH_SURF_CONEXT_KEY = environment.surfconext.client_id
SOCIAL_AUTH_SURF_CONEXT_SECRET = environment.secrets.surfconext.secret_key

AUTHENTICATION_BACKENDS = (
    'surf.vendor.surfconext.oidc.backend.SurfConextOpenIDConnectBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# https://python-social-auth.readthedocs.io/en/latest/pipeline.html
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.social_auth.associate_by_email',  # trusts SURFConext to do e-mail validation!
    'surf.vendor.surfconext.pipeline.require_data_permissions',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'surf.vendor.surfconext.pipeline.store_data_permissions',
    'social_core.pipeline.user.user_details',
    'surf.vendor.surfconext.pipeline.get_groups',
    'surf.vendor.surfconext.pipeline.assign_communities',
    'social_core.pipeline.social_auth.load_extra_data',

)

LOGIN_REDIRECT_URL = BASE_URL + "/login/success"
LOGOUT_REDIRECT_URL = "https://engine.surfconext.nl/logout"

VOOT_API_ENDPOINT = environment.surfconext.voot_api_endpoint


# Search

ELASTICSEARCH_HOST = environment.elastic_search.host
ELASTICSEARCH_PROTOCOL = environment.elastic_search.protocol
ELASTICSEARCH_VERIFY_CERTS = environment.elastic_search.verify_certs  # ignored when protocol != https
ELASTICSEARCH_NL_INDEX = "latest-nl"
ELASTICSEARCH_EN_INDEX = "latest-en"
ELASTICSEARCH_UNK_INDEX = "latest-unk"


# CKEditor
# https://github.com/django-ckeditor/django-ckeditor

CKEDITOR_CONFIGS = {
    "default": {
        "width": "600px",
        "height": "250px",
        'toolbar_SurfToolbar': [
            {'name': 'document', 'items': ['Source']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'insert',
             'items': ['Image', 'Table', 'HorizontalRule', 'SpecialChar']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'links', 'items': ['Link', 'Unlink']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
        ],
        'toolbar': 'SurfToolbar',  # put selected toolbar config here
    }
}


# Robots
# https://pypi.org/project/django-x-robots-tag-middleware/

X_ROBOTS_TAG = ['noindex', 'nofollow']

if MODE != 'production':
    MIDDLEWARE.append('x_robots_tag_middleware.middleware.XRobotsTagMiddleware')


# Debug Toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/

if DEBUG:
    # Activation
    INSTALLED_APPS += [
        'debug_toolbar'
    ]
    MIDDLEWARE = MIDDLEWARE[0:4] + ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE[4:]

    # Configuration
    # NB: INTERAL_IPS doesn't work well for Docker containers
    INTERNAL_HOSTS = [
        '127.0.0.1:8080',
        'localhost:8080',
    ]
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: request.get_host() in INTERNAL_HOSTS
    }


EMAIL_HOST = 'outgoing.mf.surf.net'
EMAIL_PORT = 25
ENABLE_ADMINISTRATIVE_EMAILS = environment.django.administrative_emails
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


EDUTERM_API_KEY = environment.secrets.eduterm.api_key
DEEPL_API_KEY = environment.secrets.deepl.api_key
