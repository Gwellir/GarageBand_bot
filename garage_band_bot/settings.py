"""
Django settings for garage_band_bot project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

import dj_database_url
import dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# load ENV
dotenv_file = BASE_DIR / ".env"
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-#nj8#@3k+bqlki17kvh$4m!fcb#^=d!h91a5tp@z8pafhj(k)%",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.getenv("DJANGO_DEBUG", "1")))

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tgbot",
    "adminapp",
    "convoapp",
    "bazaarapp",
    "repairsapp",
    "filterapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "garage_band_bot.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "garage_band_bot.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {"default": dj_database_url.config(conn_max_age=600)}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = ""
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# bot settings
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TESTING_CHANNEL_ID = os.getenv("TESTING_CHANNEL_ID")
TESTING_CHANNEL_NAME = os.getenv("TESTING_CHANNEL_NAME")
TESTING_GROUP_ID = os.getenv("TESTING_GROUP_ID")

PUBLISHING_CHANNEL_ID = os.getenv("PUBLISHING_CHANNEL_ID")
PUBLISHING_CHANNEL_NAME = os.getenv("PUBLISHING_CHANNEL_NAME")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")
DISCUSSION_GROUP_ID = os.getenv("DISCUSSION_GROUP_ID")
FEEDBACK_GROUP_ID = os.getenv("FEEDBACK_GROUP_ID")

BAZAAR_FILTER_TEST_TOKEN = os.getenv("BAZAAR_TEST_TOKEN")
BAZAAR_FILTER_LIVE_TOKEN = os.getenv("BAZAAR_LIVE_TOKEN")
BAZAAR_PUBLISH_ID = os.getenv("BAZAAR_PUBLISH_ID")
BAZAAR_TEST_PUBLISH_ID = os.getenv("BAZAAR_TEST_PUBLISH_ID")

REPAIRS_FILTER_LIVE_TOKEN = os.getenv("REPAIRS_FILTER_LIVE_TOKEN")
REPAIRS_FILTER_TEST_TOKEN = os.getenv("REPAIRS_FILTER_TEST_TOKEN")

DEV_TG_ID = os.getenv("DEV_TG_ID")

# media
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
