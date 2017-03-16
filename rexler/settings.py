"""
Django settings for rexler project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wrd-ab6a*ie9^d2d-ldqr5ss$by$1#%#=iub+e6lhwbjjv5!o*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'dateSite.apps.dateSiteConfig',
    'dateSite.templatetags',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    # The Django sites framework is required
    'django.contrib.sites',
    # The Django authentication
    'allauth',
    'allauth.account',
    # Sass preprocessor
    'sass_processor',
    # PostgreSQL search
    'django.contrib.postgres',
    # Channels
    'channels',
    # autocomplete
    'dal',
    'dal_select2',
    # upload ajax files
    'django_file_form',
    'django_file_form.ajaxuploader',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rexler.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.static',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dateSite.context_processor.login_form_processor',
                'dateSite.context_processor.search_form_processor',
                'dateSite.context_processor.feeling_choices_processor',
                'dateSite.context_processor.notifications_processor',
                'dateSite.context_processor.profile_menu_processor',
                'dateSite.context_processor.user_verified_processor',
                'dateSite.context_processor.signup_form_processor',
                'dateSite.context_processor.goodluck_form_processor',
                'dateSite.context_processor.my_chats_processor',
                'dateSite.context_processor.changepass_form_processor',
                'dateSite.context_processor.billing_processor',
                'dateSite.context_processor.upload_files_processor',
            ],
        },
    },
]


WSGI_APPLICATION = 'rexler.wsgi.application'
# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rexler',#ebdb
        'USER': 'siteadmin',
        'PASSWORD': '@dm!n',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'options': '-c search_path=rexler'
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR,'static')

STATIC_URL = '/static/'

MEDIA_ROOT = 'media'

MEDIA_URL = '/media/'

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/'  # It means home view

# Change for production
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'namjoonrol@gmail.com'
EMAIL_HOST_PASSWORD = 'bangtanboys'
EMAIL_PORT = 587


AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USER_DISPLAY = lambda user: user.username
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = None
ACCOUNT_ADAPTER = 'dateSite.adapter.AccountAdapter'
ACCOUNT_FORMS = {
    'login': 'dateSite.forms.LoginForm',
    'signup': 'dateSite.forms.SignupForm',
    'reset_password': 'dateSite.forms.ResetPasswordForm',
    'change_password': 'dateSite.forms.ChangePasswordForm',
    'add_email': 'dateSite.forms.AddEmailForm'
}

# Sass configuration
SASS_PRECISION = 4
SASS_OUTPUT_STYLE = 'compact'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
)
#'redis-001.qoaazn.0001.use1.cache.amazonaws.com'
#redis_host = os.environ.get('REDIS_HOST', 'redis-rexler-001.qoaazn.0001.use1.cache.amazonaws.com')
# Channel settings
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgiref.inmemory.ChannelLayer",
        "ROUTING": "rexler.routing.channel_routing",
    },
}
"""
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(redis_host, 6379)],
        },
        "ROUTING": "rexler.routing.channel_routing",
    },
"""
