create table public.participants (
  id uuid primary key default gen_random_uuid(),
  username text not null,
  username_normalized text not null,
  password_hash text not null,
  must_change_password boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint participants_username_normalized_key unique (username_normalized),
  constraint participants_username_normalized_matches check (
    username_normalized = lower(btrim(username))
  ),
  constraint participants_username_normalized_format check (
    username_normalized ~ '^[a-z0-9._-]{3,24}$'
  )
);

create trigger participants_updated_at
before update on public.participants
for each row execute function public.touch_updated_at();

create table public.participant_sessions (
  id uuid primary key default gen_random_uuid(),
  participant_id uuid not null references public.participants(id) on delete cascade,
  token_hash text not null unique,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  revoked_at timestamptz,
  constraint participant_sessions_expiry_check check (expires_at > created_at)
);

create index participant_sessions_owner_expiry_idx
  on public.participant_sessions(participant_id, expires_at)
  where revoked_at is null;

alter table public.participants enable row level security;
alter table public.participant_sessions enable row level security;

alter table public.personal_appliances
  add column participant_id uuid references public.participants(id) on delete cascade;
alter table public.personal_appliances
  alter column owner_user_id drop not null;
create unique index personal_appliances_participant_item_key
  on public.personal_appliances(
    participant_id, normalized_name, category, power_watts, hours_per_day, days_per_month
  )
  where participant_id is not null;

alter table public.personal_presets
  add column participant_id uuid references public.participants(id) on delete cascade;
alter table public.personal_presets
  alter column owner_user_id drop not null;
create unique index personal_presets_participant_name_key
  on public.personal_presets(participant_id, normalized_name)
  where participant_id is not null;

alter table public.catalog_submissions
  add column participant_id uuid references public.participants(id) on delete cascade;
alter table public.catalog_submissions
  alter column submitted_by drop not null;

alter table public.quiz_attempts
  add column participant_id uuid;
alter table public.quiz_attempts
  add column question_order jsonb not null default '[]'::jsonb
  check (jsonb_typeof(question_order) = 'array');
alter table public.quiz_attempts
  drop constraint if exists quiz_attempts_quiz_id_session_id_key;
create unique index quiz_attempts_participant_quiz_key
  on public.quiz_attempts(participant_id, quiz_id)
  where participant_id is not null;

drop policy if exists quiz_attempts_participant_access on public.quiz_attempts;
drop policy if exists quiz_attempts_participant_insert on public.quiz_attempts;
drop policy if exists quiz_answers_participant_access on public.quiz_answers;

create policy quiz_attempts_legacy_auth_read on public.quiz_attempts
  for select using (participant_user_id = auth.uid());
create policy quiz_attempts_legacy_auth_insert on public.quiz_attempts
  for insert with check (participant_user_id = auth.uid());
create policy quiz_answers_legacy_auth_access on public.quiz_answers
  for all using (
    exists (
      select 1 from public.quiz_attempts a
      where a.id = attempt_id and a.participant_user_id = auth.uid()
    )
  ) with check (
    exists (
      select 1 from public.quiz_attempts a
      where a.id = attempt_id and a.participant_user_id = auth.uid()
    )
  );

alter table if exists public.analytics_events
  add column if not exists participant_id uuid;

comment on table public.participants is
  'Private participant accounts. Access only through the server-side authentication repository.';
comment on table public.participant_sessions is
  'Hashed opaque login tokens. Access only through the server-side authentication repository.';
comment on column public.quiz_attempts.participant_id is
  'Pseudonymous application participant UUID; intentionally has no FK so approved results can outlive account cleanup.';