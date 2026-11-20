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
    'django.co¶»§q«^