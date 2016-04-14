"""
Django settings for mrv_toolbox project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import djcelery
djcelery.setup_loader()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q&!@4(l92sy&5al9f@4#420$v1+6%)-6x(&o-x3t__*$e7^m#z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

#ROOT_BREADCRUMB_URL = 'http://35.8.163.102:8000'
ROOT_BREADCRUMB_URL = 'http://localhost:8070'
COPYRIGHT_LABEL = 'Copyright &copy; 2013 MSU'
GOOGLE_ANALYTICS_CODE = 'UA-42541231-1'
GOOGLE_ANALYTICS_DOMAIN = 'carbon2markets.org'
DOCUMENTS_PATH = 'documents/'
IMAGES_FOLDER_PATH = 'images/'

# email admin SMTP
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'goesmrv@gmail.com'
EMAIL_HOST_PASSWORD = 'GoesMrv1024@'

# External CDN
#MATHJAX_CDN_URL = 'https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'
MATHJAX_CDN_URL = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML'

# Bulletin Message
# BULLETIN ITEM
BULLETIN_TRUE = False
BULLETIN_HEADING = "Database Reset"
BULLETIN_DATE = ''
BULLETIN_MESSAGE  = ''
BULLETIN_COLOR = 'warning'

TASTYPIE_FULL_DEBUG = True
LOGIN_URL = '/cas/login/'
LOGOUT_URL = '/cas/logout/'
LOGIN_REDIRECT_URL = '/core/splash/'

SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_HTTPONLY = False
#comment
CAS_TICKET_EXPIRATION = 5
CAS_AUTO_REDIRECT_AFTER_LOGOUT = False

AUTHENTICATION_BACKEND = (
    'django.contrib.auth.backends.ModelBackend',
)



BROKER_URL = "amqp://gchange:cgv4tr9v4xl5@35.8.163.102:5672/nevis"
CELERY_RESULT_BACKEND='amqp' #'djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['json','pickle','msgpack','yaml']
CELERY_IGNORE_RESULT = False
CELERY_ALWAYS_EAGER = True
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'south',
    'core',
    'tastypie',
    'ecalc',
    'cas_provider',
    'mrvapi',
    'mrvutils',
    #'mobileapi',
    'django.contrib.gis',
    'sampling_design',
    'measuring',
    'allometric',
    'reports',
    'mapping',
    'djcelery',
    'django_jenkins'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'ecalc.context_processors.admin_media_prefix',
    'core.context_processor.add_project',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mrv_toolbox.urls'
WSGI_APPLICATION = 'mrv_toolbox.wsgi.application'



# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

POSTGIS_VERSION = ( 2, 1 )
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'gcf',
        'USER': 'goes',
        'PASSWORD': 'goes',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = False

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_URL = '/static/'
