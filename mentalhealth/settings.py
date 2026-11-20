"""Secure, production-aware Django settings."""
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
DEBUG = os.getenv('DJANGO_DEBUG', 'false').lower() == 'true'
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
PERSISTENT_STORAGE_ENABLED = bool(DATABASE_URL) or DEBUG
if (DATABASE_URL or (os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_PUBLISHABLE_KEY'))) and not os.getenv('DJANGO_SECRET_KEY'):
    raise RuntimeError('Set DJANGO_SECRET_KEY before enabling a database')
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY') or os.urandom(48).hex()
ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', '.vercel.app,localhost,127.0.0.1').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app'] + ['https://' + h for h in ALLOWED_HOSTS if not h.startswith('.') and h not in ('localhost', '127.0.0.1')]
INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','detector',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'mentalhealth.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],
    'APP_DIRS':True,'OPTIONS':{'context_processors':[
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'mentalhealth.context_processors.storage_status',
]}}]
WSGI_APPLICATION = 'mentalhealth.wsgi.application'
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=0, conn_health_checks=True, ssl_require=True)}
else:
    DATABASES = {'default': {'ENGINE':'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3' if DEBUG else '/tmp/mht_unconfigured.sqlite3'}}
if not PERSISTENT_STORAGE_ENABLED:
    SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':10}},
    {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE='en-us'
TIME_ZONE='UTC'
USE_I18N=True
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
STORAGES={'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='login'
LOGIN_REDIRECT_URL='dashboard'
LOGOUT_REDIRECT_URL='home'
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SECURE=not DEBUG
CSRF_COOKIE_SECURE=not DEBUG
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_REFERRER_POLICY='same-origin'
X_FRAME_OPTIONS='DENY'
DATA_UPLOAD_MAX_MEMORY_SIZE=512*1024
