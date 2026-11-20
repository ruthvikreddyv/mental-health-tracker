# Mindful Space — Mental Health Tracker

A responsive Django application offering browser-only mood tracking and authenticated private cloud journals and check-ins.

## Production
Website: https://mental-health-tracker-rosy.vercel.app/

The deployed Django backend exposes `/api/config/`, `/api/health/`, `/api/journals/`, `/api/checkins/` and `/api/my-data/`. Public visitors can explore `/demo/` without signing in, with entries stored in local browser storage. Supabase email/password authentication enables private cloud records: the backend verifies Supabase Auth bearer tokens, and each database request executes under the same user's JWT so PostgreSQL Row-Level Security enforces ownership. No privileged Supabase key is used by the app.

## Configuration
Create a dedicated Supabase project. Apply `supabase_schema.sql` there, then configure these **Vercel** environment variables (do not commit values):
- `SUPABASE_URL` (project API URL)
- `SUPABASE_PUBLISHABLE_KEY` (public publishable key)
- `DJANGO_SECRET_KEY` (private long random signing secret)
- `DJANGO_DEBUG=false`
- `DJANGO_ALLOWED_HOSTS=.vercel.app`

Django ORM accounts in the legacy app are not required by the modern cloud workspace. `DATABASE_URL` is intentionally unused for that path. Do not add or commit PostgreSQL passwords.

## Local development
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 manage.py check
python3 manage.py test detector
python3 manage.py runserver
```
Without cloud environment variables, the browser-only demo still works.

## Privacy & safety
Journal and check-in records are private, sensitive data. The ten-question check-in is **not validated** for diagnosis. The app is not an emergency service. A clinical and privacy review, retention strategy, email deliverability, and abuse protection are needed before broad public use. The old Git history included a hard-coded Django development secret and a SQLite database: deleting those from the latest commit **does not erase past commits**; rotate exposed credentials and remediate historical sensitive content separately if it contained real users' data.
