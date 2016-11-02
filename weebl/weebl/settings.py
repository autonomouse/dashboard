"""
Django settings for weebl project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import yaml

SITE_ID = 1

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'd)nfvgqd2efxi9c9#99v%y&s6e3=ia3a9srw+wphvchub*gr@#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']  # FIXME: Need to pass in the IP from the weebl charm.
# ALLOWED_HOSTS will not accept localhost or 127.0.0.1 nor does [] work anymore

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'oilserver',
    'tastypie',
    'django_extensions',
    'social.apps.django_app.default',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.ubuntu.UbuntuOpenId',
)

LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'

ROOT_URLCONF = 'weebl.urls'

WSGI_APPLICATION = 'weebl.wsgi.application'

CONFIG_PATH = '/etc/weebl/weebl.yaml'

STATICFILES_DIRS = [
    "/usr/share/javascript/jquery/",
    "/usr/share/javascript/angular.js/",
    "/usr/share/javascript/yui3/",
]

BUILTIN_STATIC = os.path.join(BASE_DIR, 'oilserver', 'static')

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as config_file:
        custom_config = yaml.load(config_file.read())
        db_config = custom_config['database']
        if 'static_root' in custom_config:
            STATIC_ROOT = custom_config['static_root']
            STATICFILES_DIRS.append(BUILTIN_STATIC)
        else:
            STATIC_ROOT = BUILTIN_STATIC
else:
    db_config = {
        'database': 'bugs_database',
        'host': 'localhost',
        'port': None,
        'user': 'weebl',
        'password': 'passweebl',
    }
    STATIC_ROOT = BUILTIN_STATIC

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': db_config['database'],
        'USER': db_config['user'],
        'PASSWORD': db_config['password'],
        'HOST': db_config['host'],
        'PORT': db_config['port'],
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

TASTYPIE_DEFAULT_FORMATS = ['json']

API_LIMIT_PER_PAGE = 0

GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}
