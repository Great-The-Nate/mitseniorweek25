"""
Django settings for seniorweek25 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '<KEY>'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admindocs',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'lottery', 
    'cert_auth',
    'oidc_auth'
)

# Django requires a list of hosts this site is served from; since users can
# add new hosts with Pony at any time, we just trust SERVER_NAME (set by
# Apache) to be the correct hostname. If you want to restrict which virtual
# hosts your application can run on, disable this middleware and set
# ALLOWED_HOSTS by hand.
class AllowedHostsMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response
    def process_request(self, request):
        # Django 1.6
        global ALLOWED_HOSTS
        name = request.META.get('SERVER_NAME')
        if name and name not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(name)
    def __call__(self, request):
        # Django 1.11+
        self.process_request(request)
        return self.get_response(request)
MIDDLEWARE_CLASSES = (
    'seniorweek25.settings.AllowedHostsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cert_auth.ScriptsRemoteUserMiddleware'
)

ROOT_URLCONF = 'seniorweek25.urls'

WSGI_APPLICATION = 'seniorweek25.wsgi.application'

# Authentication

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'cert_auth.ScriptsRemoteUserBackend',
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/__scripts/django/static/'


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

# Login URL

LOGIN_URL = 'oidc_auth'

# OIDC / Petrock configuration
OIDC_PROVIDER = 'https://petrock.mit.edu'
OIDC_AUTHORIZATION_ENDPOINT = OIDC_PROVIDER + '/touchstone/oidc/authorization'
OIDC_TOKEN_ENDPOINT         = OIDC_PROVIDER + '/oidc/token'
OIDC_USERINFO_ENDPOINT      = OIDC_PROVIDER + '/oidc/userinfo'
OIDC_JWKS_URI               = OIDC_PROVIDER + '/oidc/jwks'

OIDC_CLIENT_ID     = 'XXX'
OIDC_CLIENT_SECRET = 'XXX'
OIDC_REDIRECT_URI  = 'https://nmustafa.scripts.mit.edu/seniorweek25/oidc/login'
OIDC_SCOPE         = 'openid email profile'