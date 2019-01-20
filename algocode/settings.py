import os
from importlib import import_module

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_secret(secret):
    file = open(os.path.join(BASE_DIR, 'secrets', secret))
    result = file.read().strip()
    file.close()
    return result


def load_config(config):
    config = import_module('configs.' + config)
    return config.value


CODEFORCES_KEY = load_secret('codeforces_key.txt')
CODEFORCES_SECRET = load_secret('codeforces_secret.txt')
INFORMATICS_LOGIN = load_secret('informatics_login.txt')
INFORMATICS_PASSWORD = load_secret('informatics_password.txt')
SECRET_KEY = load_secret('django_secret.txt')
DEBUG = load_config('django_debug')
JUDGES_DIR = load_config('ejudge_dir')
DATABASES = load_config('django_db')


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
