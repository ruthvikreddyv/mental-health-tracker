"""Supabase-backed APIs. User JWTs, never service-role credentials, enforce RLS."""
import json
import logging
import os
import re
import uuid

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

log = logging.getLogger(__name__)
TIMEOUT = (3.5, 9)


def configured():
    return bool(os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_PUBLISHABLE_KEY'))


def api_config(request):
    return JsonResponse({
        'cloud_enabled': configured(),
        'url': os.getenv('SUPABASE_URL', '') if configured() else '',
        'publishable_key': os.getenv('SUPABASE_PUBLISHABLE_KEY', '') if configured() else '',
    })


def api_health(request):
    if not configured():
        return JsonResponse({'status': 'demo', 'backend': 'unconfigured', 'database': 'not_connected'})
    try:
        resp = requests.get(os.environ['SUPABASE_URL'].rstrip('/') + '/auth/v1/health',
                            headers={'apikey': os.environ['SUPABASE_PUBLISHABLE_KEY']},
                            timeout=TIMEOUT)
        return JsonResponse({'status': 'ok' if resp.ok else 'degraded',
                             'backend': 'supabase', 'auth_http_status': resp.status_code},
                            status=200 if resp.ok else 503)
    except requests.RequestException:
        return JsonResponse({'status': 'degraded', 'backend': 'supabase', 'error': 'un¶»§q«^