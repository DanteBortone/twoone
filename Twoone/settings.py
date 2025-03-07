"""
Django settings for Twoone project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import django_heroku
import dj_database_url




# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '527!5$b3$l8x&=mie9x7q2ewuh^&angm47+ugo_ngbhpb!l4k@'
SITE_ID = 1

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', 'twoone.herokuapp.com']


# Application definition

INSTALLED_APPS = ['user.apps.UserConfig',
                  'create.apps.CreateConfig',
                  'engage.apps.EngageConfig',
                  'django.contrib.admin',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.messages',
                  'whitenoise.runserver_nostatic',
                  'django.contrib.staticfiles',
                  'pybb.apps.PybbConfig',
                  'django.contrib.sites', # added due to error after adding pybb:"RuntimeError: Model class django.contrib.sites.models.Site doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS."
                  #'django_extensions', # to reset the database
                  ]

MIDDLEWARE = [
    # 'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Twoone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./templates',],
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

WSGI_APPLICATION = 'Twoone.wsgi.application'

# Redirect to home URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = '/user/'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'twoone_db'),
        'USER': os.environ.get('DB_USER', 'dantebortone'),
        'PASSWORD': os.environ.get('DB_PASS', '12qwaszx'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

#print("pre: ", DATABASES)
# https://medium.com/agatha-codes/9-straightforward-steps-for-deploying-your-django-app-with-heroku-82b952652fb4
db_from_env = dj_database_url.config(conn_max_age=300)
DATABASES['default'].update(db_from_env)
#print("post: ", DATABASES)


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


# pybb additions
TEMPLATE_CONTEXT_PROCESSORS = ('pybb.context_processors.processor',)
MIDDLEWARE_CLASSES = ('pybb.middleware.PybbMiddleware',)

PYBB_MARKUP = 'markdown'
PYBB_ALLOW_DELETE_OWN_POST = False
PYBB_SMILES = {}
PYBB_TOPIC_PAGE_SIZE = 10

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (
                    os.path.join(BASE_DIR, 'static'),
                    )

# print("STATIC_ROOT: ", STATIC_ROOT)
# print("STATICFILES_DIRS: ", STATICFILES_DIRS)

# To add compression and caching support: http://whitenoise.evans.io/en/stable/django.html
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# to add compression but no caching:
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'



django_heroku.settings(locals())

