import os
import json
from importlib import import_module

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, 'configs/config.json')) as config_file:
    config_json = json.load(config_file)


def import_json(value):
    if isinstance(value, list):
        result = []
        for i in value:
            result.append(import_json(i))
        return result
    if isinstance(value, dict):
        result = dict()
        for key, val in value.items():
            result[key] = import_json(val)
        return result
    if isinstance(value, str) and value.startswith("exec_res = "):
        exec("global exec_res\n" + value)
        return exec_res
    return value


def load_secret(secret):
    try:
        return import_json(config_json["secrets"][secret])
    except:
        print("No secret", secret)
        return None


def load_config(config):
    try:
        return import_json(config_json["configs"][config])
    except:
        print("No config", config)
        return None


CODEFORCES = load_secret('codeforces')
EJUDGE_CONTROL = load_secret('ejudge_control_cmd')
EJUDGE_AUTH = load_secret('ejudge')
SECRET_KEY = load_secret('django_secret')
DEBUG = load_config('django_debug')
JUDGES_DIR = load_config('ejudge_dir')
DATABASES = load_config('django_db')
CACHES = load_config('django_cache')
EJUDGE_URL = load_config('ejudge_url')
DEFAULT_MAIN = load_config("default_main")
DEFAULT_COURSE = load_config("default_course")
DEFAULT_PAGE = load_config("default_page")
DEFAULT_HOME = load_config("default_home")
MONGO = load_config('mongo_db')
GOOGLE_SHEETS_CONFIG = load_secret('google_sheets_config')
PCMS_STANDINGS = load_config('pcms_standings')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'sql.log',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'courses.apps.CoursesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'algocode.urls'

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

MEDIA_ROOT = os.path.join(BASE_DIR, 'files')
MEDIA_URL = '/files/'

WSGI_APPLICATION = 'algocode.wsgi.application'

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

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

TEMPLATE_DIRS = (os.path.join(BASE_DIR,  'templates'),)

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
