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
        return JsonResponse({'status': 'degraded', 'backend': 'supabase', 'error': 'unreachable'}, status=503)


def error(message, status=400):
    return JsonResponse({'error': message}, status=status)


def identity(request):
    if not configured():
        return None, error('Cloud storage is not configured.', 503)
    bearer = request.headers.get('Authorization', '')
    if not re.fullmatch(r'Bearer [A-Za-z0-9._-]{30,5000}', bearer):
        return None, error('Sign in is required.', 401)
    token = bearer.split(' ', 1)[1]
    headers = {'apikey': os.environ['SUPABASE_PUBLISHABLE_KEY'], 'Authorization': 'Bearer ' + token}
    try:
        resp = requests.get(os.environ['SUPABASE_URL'].rstrip('/') + '/auth/v1/user',
                            headers=headers, timeout=TIMEOUT)
    except requests.RequestException:
        return None, error('Authentication service is temporarily unavailable.', 503)
    if resp.status_code != 200:
        return None, error('Session expired. Please sign in again.', 401)
    payload = resp.json()
    try:
        user_id = str(uuid.UUID(payload['id']))
    except (ValueError, KeyError, TypeError):
        return None, error('Authentication identity was invalid.', 401)
    return (user_id, headers), None


def proxy(user, method, table, params=None, payload=None):
    user_id, headers = user
    headers = {**headers, 'Content-Type': 'application/json', 'Prefer': 'return=representation'}
    url = os.environ['SUPABASE_URL'].rstrip('/') + '/rest/v1/' + table
    try:
        resp = requests.request(method, url, headers=headers, params=params,
                                json=payload, timeout=TIMEOUT)
    except requests.RequestException:
        return error('Storage service is temporarily unavailable.', 503)
    if not resp.ok:
        log.warning('Supabase data request returned %s for %s', resp.status_code, table)
        # Never relay schema details, database errors, or tokens to the browser.
        return error('Unable to complete this request.', 502)
    if method == 'DELETE':
        return JsonResponse({'deleted': True})
    try:
        return JsonResponse({'items': resp.json()}, status=201 if method == 'POST' else 200)
    except ValueError:
        return error('Unexpected response from storage service.', 502)


def body_json(request):
    if len(request.body) > 9000:
        raise ValueError('Request is too large.')
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError('Expected a JSON object.')
        return data
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError('Invalid JSON.')


@csrf_exempt  # Bearer-only auth; browser cookies are not authentication credentials for these routes.
@require_http_methods(['GET', 'POST'])
def journals(request):
    user, err = identity(request)
    if err:
        return err
    if request.method == 'GET':
        return proxy(user, 'GET', 'mindspace_journals', {
            'select': 'id,text,mood,created_at', 'order': 'created_at.desc', 'limit': '100'})
    try:
        body = body_json(request)
        text = body.get('text', '')
        mood = body.get('mood')
        if not isinstance(text, str) or not 1 <= len(text.strip()) <= 3000:
            raise ValueError('Reflection must contain 1–3000 characters.')
        if mood is not None and (type(mood) is not int or not 1 <= mood <= 5):
            raise ValueError('Mood must be between 1 and 5.')
    except ValueError as e:
        return error(str(e))
    return proxy(user, 'POST', 'mindspace_journals', payload={
        'user_id': user[0], 'text': text.strip(), 'mood': mood})


@csrf_exempt
@require_http_methods(['DELETE'])
def delete_journal(request, entry_id):
    user, err = identity(request)
    if err:
        return err
    return proxy(user, 'DELETE', 'mindspace_journals', {'id': 'eq.' + str(entry_id)})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def checkins(request):
    user, err = identity(request)
    if err:
        return err
    if request.method == 'GET':
        return proxy(user, 'GET', 'mindspace_checkins', {
            'select': 'id,answers,total,created_at', 'order': 'created_at.desc', 'limit': '100'})
    try:
        answers = body_json(request).get('answers')
        if not isinstance(answers, list) or len(answers) != 10 or any(
            type(a) is not int or not 0 <= a <= 3 for a in answers
        ):
            raise ValueError('Answer all ten questions using values 0 to 3.')
    except ValueError as e:
        return error(str(e))
    return proxy(user, 'POST', 'mindspace_checkins', payload={
        'user_id': user[0], 'answers': answers, 'total': sum(answers)})


@csrf_exempt
@require_http_methods(['DELETE'])
def delete_checkin(request, entry_id):
    user, err = identity(request)
    if err:
        return err
    return proxy(user, 'DELETE', 'mindspace_checkins', {'id': 'eq.' + str(entry_id)})


@csrf_exempt
@require_http_methods(['DELETE'])
def delete_all(request):
    user, err = identity(request)
    if err:
        return err
    for table in ('mindspace_journals', 'mindspace_checkins'):
        result = proxy(user, 'DELETE', table, {'user_id': 'eq.' + user[0]})
        if result.status_code != 200:
            return result
    return JsonResponse({'deleted': True, 'scope': 'journals_and_checkins_only'})
