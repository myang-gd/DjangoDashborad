"""
Django settings for django_dashboard project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys
import djcelery
from django.conf import settings

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = False

LOGIN_REDIRECT_URL = "/admin/"
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODERATOR_EMAILS = ['QA-Architecture@greendotcorp.com', 'ApplicationSecurity@greendotcorp.com', 'RE@greendotcorp.com', 'IT-DevOps@greendotcorp.com']
MAIL_SERVER = 'mailhost.nextestate.com'
MAIL_PORT = 25
APPLICATION_URL = "https://gdcqatools01:8200"
SENDER = 'API-HealtCheck-Monitor@greendotcorp.com'
MONITOR_SENDER = 'QA-Monitor@greendotcorp.com'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_gh00mgcbfhdqayj962ldd4*v3d+c&2=+ru6ifm8ca!b$+$j(*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Celery 
djcelery.setup_loader()
# BROKER_URL = 'django://'
BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_TIMEZONE  = TIME_ZONE
CELERY_ALWAYS_EAGER = False
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_python3_ldap',
    'apps.healthcheck',
    'apps.qa_monitor',
    'apps.spfinder', 
	'apps.card_finder',
    'apps.customerFinder',	
    'apps.testrail_report', 
    'apps.case_report', 
    'apps.lib', 
    'debug_toolbar',
    'djcelery',
    'kombu.transport.django',
    'import_export',
    'djangosecure',
    'sslserver',
    'widget_tweaks',
    'apps.ConfigModifier',
    'apps.pts_utility',
	'apps.aci_utility',
    'apps.baas_utility',
    'apps.EncryptDecryptUtility',
    'apps.jiratool',
    'guardian',
    'rest_framework',
    'apps.hack',
    'apps.testdata_monitor',
	'apps.CommonAPI.CalendarAPI',
	'apps.CommonAPI.MilestoneAPI',
	'apps.query_view',
	'apps.dmwn_card_finder',
	'apps.BrowserStack',
    'apps.License'
]

REST_FRAMEWORK = {
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAdminUser',
#     ],
    'PAGE_SIZE': 10
}

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'apps.lib.middleware.ajaxmessaging.AjaxMessaging',
]

ROOT_URLCONF = 'django_dashboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'django_dashboard.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
ODBC_Driver = 'ODBC Driver 17 for SQL Server'
DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'Healthcheck',
        'HOST': 'GDCQAAUTOSQL201',
        'USER': 'qa_automation',
        'PASSWORD': 'Gr33nDot!',
        "OPTIONS": {"driver": ODBC_Driver},
    },
    'qa_monitor': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'qa_monitor',
        'HOST': 'GDCQAAUTOSQL201',
        'USER': 'qa_automation',
        'PASSWORD': 'Gr33nDot!',
        "OPTIONS": {"driver": ODBC_Driver,},
    },
    'config_lock': {
     'ENGINE': 'sql_server.pyodbc',
     'NAME': 'config_lock',
     'HOST': 'GDCQAAUTOSQL201',
#      'USER': 'auto_reader',
#      'PASSWORD': 
      "OPTIONS": {"driver": ODBC_Driver},
    },
    'QA3': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'NEC',
        'HOST': 'GDCQA3SQL',
        'USER': 'qa_automation',
        'PASSWORD': 'Gr33nDot!',
        "OPTIONS": {"driver": ODBC_Driver,},
    },
    'QA4': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'NEC',
        'HOST': 'GDCQA4SQL',
        'USER': 'qa_automation',
        'PASSWORD': 'Gr33nDot!',
        "OPTIONS": {"driver": ODBC_Driver,},
    },
    'QA5': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'NEC',
        'HOST': 'GDCQA5SQL01',
        'USER': 'qa_automation',
        'PASSWORD': 'Gr33nDot!',
        "OPTIONS": {"driver": ODBC_Driver,},
    },
    'PIE': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'NEC',
        'HOST': 'GDCPIESQL',
        'USER': 'qa_automation',
        'PASSWORD': 'Gr33nDot!',
        "OPTIONS": {"driver": ODBC_Driver,},
    },
    'GDCAUTO': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'QueryStore',
        'HOST': 'GDCQAAUTOSQL201',
        'USER': 'qa_automation',
        'PASSWORD': 'Gr33nDot!',
        "OPTIONS": {"driver": ODBC_Driver}
    },
    'automation': {
     'ENGINE': 'sql_server.pyodbc',
     'NAME': 'automation',
     'HOST': 'GDCQAAUTOSQL201',
     'USER': 'qa_automation',
     'PASSWORD': 'Gr33nDot!',
      "OPTIONS": {"driver": ODBC_Driver}
    }
    
}

DATABASE_ROUTERS = ['django_dashboard.db_router.DBRouter']  

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'healthcheck_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'healthcheck.log',
            'formatter': 'verbose'
        },
        'qa_monitor_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'qa_monitor.log',
            'formatter': 'verbose'
        },
        'spfinder_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'spfinder.log',
            'formatter': 'verbose'
        },
        'case_report_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'case_report.log',
            'formatter': 'verbose'
        },
        'configModifier_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'configModifier.log',
            'formatter': 'verbose'
        },
		'extend_views_database_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'extend_views_database.log',
            'formatter': 'verbose'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'level':'INFO'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO'
        },
        'healthcheck': {
            'handlers': ['healthcheck_file'],
            'level': 'WARNING',
        },
        'qa_monitor' : {
            'handlers': ['qa_monitor_file'],
            'level': 'WARNING',
        },
        'spfinder' : {
            'handlers': ['spfinder_file'],
            'level': 'WARNING',
        },
        'configModifier' : {
            'handlers': ['configModifier_file'],
            'level': 'WARNING',
        },
        'case_report' : {
            'handlers': ['case_report_file'],
            'level': 'WARNING',
        },
		'extend_views_database' : {
            'handlers': ['extend_views_database_file'],
            'level': 'INFO',
        },

    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static_iis')
STATICFILES_DIRS = (os.path.join(BASE_DIR,'static'),)
APP_FILE_ROOT = os.path.join(BASE_DIR,'app_file')

LOGIN_REDIRECT_URL = "/healthcheck"

LOGIN_URL = '/login'

AUTHENTICATION_BACKENDS = (
    'apps.lib.ldap.auth.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)
###########################################################
#  LDAP AUTHENTICATION - django_python3_ldap settings
###########################################################

# The URL of the LDAP server.
LDAP_AUTH_URL = "ldap://nextestate.com:389"

# Initiate TLS on connection.
LDAP_AUTH_USE_TLS = False

# The LDAP search base for looking up users.
LDAP_AUTH_SEARCH_BASE = "dc=nextestate,dc=com"

# The LDAP class that represents a user.
LDAP_AUTH_OBJECT_CLASS = "user"

# User model fields mapped to the LDAP
# attributes that represent them.
LDAP_AUTH_USER_FIELDS = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# A tuple of django model fields used to uniquely identify a user.
LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)

# Path to a callable that takes a dict of {model_field_name: value},
# returning a dict of clean model data.
# Use this to customize how data loaded from LDAP is saved to the User model.
LDAP_AUTH_CLEAN_USER_DATA = "django_python3_ldap.utils.clean_user_data"

# Path to a callable that takes a user model and a dict of {ldap_field_name: [value]},
# and saves any additional user relationships based on the LDAP data.
# Use this to customize how data loaded from LDAP is saved to User model relations.
# For customizing non-related User model fields, use LDAP_AUTH_CLEAN_USER_DATA.
LDAP_AUTH_SYNC_USER_RELATIONS = "django_python3_ldap.utils.sync_user_relations"

# Path to a callable that takes a dict of {ldap_field_name: value},
# returning a list of [ldap_search_filter]. The search filters will then be AND'd
# together when creating the final search filter.
LDAP_AUTH_FORMAT_SEARCH_FILTERS = "django_python3_ldap.utils.format_search_filters"

# Path to a callable that takes a dict of {model_field_name: value}, and returns
# a string of the username to bind to the LDAP server.
# Use this to support different types of LDAP server.
LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_active_directory"

# Sets the login domain for Active Directory users.
LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN = "nextestate"

# The LDAP username and password of a user for authenticating the `ldap_sync_users`
# management command. Set to None if you allow anonymous queries.
LDAP_AUTH_CONNECTION_USERNAME = None
LDAP_AUTH_CONNECTION_PASSWORD = None

# Global vars

SUCCESS_Y = 'Y'
SUCCESS_N = 'N'

# SSL

SECURE_SSL_REDIRECT = False

# LOG

LOG_ROOT_PATH = '%s\django_dashboard_log' %(os.environ['SYSTEMDRIVE'])
RUN_LOG_PATH = '%s\healthcheck_run.log' % (LOG_ROOT_PATH)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11212',
        'TIMEOUT': 86400,
    },
}
settings.configure(CACHES=CACHES) # include any other settings you might need

from django.core.cache import cache
cache.clear()

