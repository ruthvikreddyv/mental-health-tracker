-- Mental Health Tracker. Run in the newly-created Supabase project only.
-- The application uses Supabase Auth JWTs and PostgREST; NO service-role key in the browser.
create extension if not exists pgcrypto with schema extensions;
create table if not exists public.mindspace_journals (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  text text not null check (length(trim(text)) between 1 and 3000),
  mood smallint check (mood between 1 and 5),
  created_at timestamptz not null default now()
);
create index if not exists mindspace_journals_owner_created_idx on public.mindspace_journals (user_id, created_at desc);
create table if not exists public.mindspace_checkins (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  answers jsonb not null check (jsonb_typeof(answers) = 'array' and jsonb_array_length(answers) = 10),
  total smallint not null check (total between 0 and 30),
  created_at timestamptz not null default now()
);
create index if not exists mindspace_checkins_owner_created_idx on public.mindspace_checkins (user_id, created_at desc);

alter table public.mindspace_journals enable row level security;
alter table public.mindspace_checkins enable row level security;
revoke all on public.mindspace_journals from anon, public;
revoke all on public.mindspace_checkins from anon, public;
grant select, insert, delete on public.mindspace_journals to authenticated;
grant select, insert, delete on public.mindspace_checkins to authenticated;

create policy "journal_read_own" on public.mindspace_journals for select to authenticated
  using ((select auth.uid()) = user_id);
create policy "journal_write_own" on public.mindspace_journals for insert to authenticated
  with check ((select auth.uid()) = user_id);
create policy "journal_delete_own" on public.mindspace_journals for delete to authenticated
  using ((select auth.uid()) = user_id);
create policy "checkin_read_own" on public.mindspace_checkins for select to authenticated
  using ((select auth.uid()) = user_id);
create policy "checkin_write_own" on public.mindspace_checkins for insert to authenticated
  with check ((select auth.uid()) = user_id);
create policy "checkin_delete_own" on public.mindspace_checkins for delete to authenticated
  using ((select auth.uid()) = user_id);
