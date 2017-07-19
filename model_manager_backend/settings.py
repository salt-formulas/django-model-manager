import os


ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = None
STATIC_ROOT = None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.abspath(os.path.join(ROOT_PATH, 'backend_db.sqlite3')),
    }
}

ALLOWED_HOSTS = ['*']

DEBUG = False
USE_I18N = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Admin', 'root@localhost'),
)

MANAGERS = ADMINS

SITE_ID = 1
SITE_NAME = 'devops_portal_backend'

USE_TZ = True
TIME_ZONE = 'Europe/Prague'

LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'EN'),
)

if not MEDIA_ROOT:
    MEDIA_ROOT = os.path.abspath(os.path.join(ROOT_PATH, 'media'))
MEDIA_URL = '/media/'

if not STATIC_ROOT:
    STATIC_ROOT = os.path.abspath(os.path.join(ROOT_PATH, 'static'))
STATIC_URL = '/static/'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': TEMPLATE_CONTEXT_PROCESSORS,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'devops_portal_backend.urls'

TEMPLATE_DIRS = (
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'templates'),
)

INSTALLED_APPS = (
    'django',
    'django_extensions',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'devops_portal_backend',
)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'

AUTH_USER_MODEL = 'devops_portal_backend.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

APPEND_SLASH = True

REST_FRAMEWORK = {
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'devops_portal_backend.pagination.PageNumberPagination',
    'PAGE_SIZE': 25
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from local_settings import *
except ImportError:
    pass

try:
    with open("/etc/devops_portal_backend/settings.py") as f:
        code = compile(f.read(), "/etc/devops_portal_backend/settings.py", 'exec')
        exec(code)
except IOError:
    pass

if hasattr(globals(), "LOCAL_INSTALLED_APPS"):
    INSTALLED_APPS += LOCAL_INSTALLED_APPS

