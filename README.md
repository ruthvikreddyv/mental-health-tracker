# Mental Health Detector

A polished, interactive Django web app for non-diagnostic self-reflection. It supports an **offline/browser-only demo** and optional **per-user cloud accounts backed by Supabase Auth + PostgreSQL**.

## What is included

- Responsive web UI with dashboard, mood selection, daily journaling, full-text search, activity charts, a ten-question check-in, support resources, privacy controls, export/delete, and dark mode.
- Browser-demo records are stored only in this browser's `localStorage`; anyone who can access the browser profile can read them. The user is warned accordingly.
- Cloud accounts use Supabase email/password authentication. The backend verifies a JWT with Supabase Auth, then proxies journal/check-in CRUD requests using **that user's JWT** so Postgres **row-level security** enforces ownership. The backend does not use a service-role key.
- All ten check-in answers and totals are validated in the backend. The questionnaire is **non-validated** and is **not** a diagnosis or clinical screening instrument.
- Browser-only mode works even if Supabase is absent. Cloud mode activates automatically when configured.

## Deploy backend + Supabase

1. Create a **new Supabase project** in an organization and region of your choice.
2. Run `supabase_schema.sql` **only in that new project** using Supabase SQL Editor. This creates `mindspace_journals` and `mindspace_checkins` with owner-only RLS policies. Do not use the old SQLite database.
3. In Supabase → Authentication → Providers, enable Email. Configure email confirmation and rate limits for your intended usage; email delivery setup is needed for reliable production signups.
4. In Vercel, deploy the repository with framework `django` and `.python-version` = 3.12. Add the environment variables below to Production and Preview and redeploy.

```dotenv
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxxx
DJANGO_SECRET_KEY=your-long-random-secret
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=.vercel.app
```

`SUPABASE_PUBLISHABLE_KEY` is intentionally public; Supabase verifies each access token and RLS protects the tables. **Never expose a Supabase service-role/secret key** in the client or store user data in the source repository.

The new cloud API does **not** require `DATABASE_URL` or Django ORM migrations. The original Django ORM-backed views remain for historical compatibility and are gated off without a separate `DATABASE_URL`; the modern `/demo/` workspace uses Supabase cloud APIs when configured.

### Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 manage.py check
python3 manage.py test detector
python3 manage.py runserver
```

- `/`: redesigned landing page
- `/demo/`: interactive workspace, both browser-only and signed-in cloud accounts
- `/api/config/`: indicates if Supabase is connected (publishable key is public)
- `/api/health/`: verifies Supabase Auth is reachable
- `/api/journals/` (GET, POST), `/api/journals/<uuid>/` (DELETE)
- `/api/checkins/` (GET, POST), `/api/checkins/<uuid>/` (DELETE)
- `/api/my-data/` (DELETE): removes this app's journal and check-in records, not the identity provider account

All protected API endpoints require a Bearer JWT, verified by Supabase Auth. Never disable or relax the RLS policies. The app does not export browser-demo records to cloud without explicit user action.

### Security and clinical limitations

The original public GitHub history included a SQLite database and an insecure hard-coded Django key; these have been excluded from this rebuild but remain visible in historical commits until repository history is remediated. Do not migrate sensitive records without user consent and a privacy review.

This project is **not a medical device, medical diagnosis, or emergency service**. Journaling, sentiment scores, and the ten-question check-in do not determine whether someone has a mental health condition. A separate clinical, security, privacy, and retention review is necessary before accepting sensitive real-world records at scale. For Supabase production, configure email deliverability, anti-abuse/rate limiting, and appropriate consent/privacy notices.
