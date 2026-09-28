-- EcoWatt interactive engagement and user catalogs.
-- Run with Supabase migrations; service_role bypasses RLS for imports/admin jobs.

create extension if not exists pgcrypto;

create type public.content_status as enum ('published', 'archived');
create type public.submission_status as enum ('pending', 'approved', 'rejected', 'archived');
create type public.submission_kind as enum ('appliance', 'pc_component', 'fact', 'preset');

create or replace function public.is_moderator()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select coalesce((auth.jwt() -> 'app_metadata' ->> 'role') in ('admin', 'moderator'), false)
$$;

create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table public.official_appliances (
  id text primary key,
  name text not null,
  normalized_name text not null,
  category text not null default 'Geral',
  power_watts numeric not null check (power_watts >= 0),
  default_hours_per_day numeric not null check (default_hours_per_day between 0 and 24),
  default_days_per_month numeric not null default 30 check (default_days_per_month between 0 and 31),
  description text,
  status public.content_status not null default 'published',
  source text not null default 'migration',
  created_by_user_id uuid references auth.users(id),
  created_by_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (normalized_name, category, power_watts, default_hours_per_day, default_days_per_month)
);

create table public.official_pc_components (
  id text primary key,
  name text not null,
  normalized_name text not null,
  category text not null,
  tdp_watts numeric not null check (tdp_watts >= 0),
  idle_watts numeric not null check (idle_watts >= 0),
  typical_load_watts numeric not null check (typical_load_watts >= 0),
  gaming_load_watts numeric not null check (gaming_load_watts >= 0),
  description text,
  status public.content_status not null default 'published',
  source text not null default 'migration',
  created_by_user_id uuid references auth.users(id),
  created_by_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (normalized_name, category, tdp_watts, idle_watts, typical_load_watts, gaming_load_watts)
);

create table public.official_facts (
  id text primary key,
  title text not null,
  normalized_title text not null unique,
  body text not null,
  status public.content_status not null default 'published',
  source text not null default 'migration',
  created_by_user_id uuid references auth.users(id),
  created_by_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.official_presets (
  id text primary key,
  name text not null,
  normalized_name text not null unique,
  description text,
  status public.content_status not null default 'published',
  source text not null default 'migration',
  created_by_user_id uuid references auth.users(id),
  created_by_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.official_preset_items (
  id text primary key,
  preset_id text not null references public.official_presets(id) on delete cascade,
  name text not null,
  category text not null default 'Geral',
  power_watts numeric not null check (power_watts >= 0),
  hours_per_day numeric not null check (hours_per_day between 0 and 24),
  days_per_month numeric not null check (days_per_month between 0 and 31),
  snapshot jsonb not null default '{}'::jsonb,
  unique (preset_id, id)
);

create table public.personal_appliances (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid not null references auth.users(id),
  name text not null,
  normalized_name text not null,
  category text not null default 'Geral',
  power_watts numeric not null check (power_watts >= 0),
  hours_per_day numeric not null check (hours_per_day between 0 and 24),
  days_per_month numeric not null default 30 check (days_per_month between 0 and 31),
  description text,
  created_by_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner_user_id, normalized_name, category, power_watts, hours_per_day, days_per_month)
);

create table public.personal_presets (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid not null references auth.users(id),
  name text not null,
  normalized_name text not null,
  tariff numeric not null check (tariff > 0),
  monthly_kwh numeric not null check (monthly_kwh >= 0),
  visibility text not null default 'private' check (visibility in ('private', 'event')),
  comparison_consent boolean not null default false,
  pseudonymous_label text,
  created_by_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner_user_id, normalized_name)
);

create table public.personal_preset_items (
  id uuid primary key default gen_random_uuid(),
  preset_id uuid not null references public.personal_presets(id) on delete cascade,
  appliance_id text,
  name text not null,
  category text not null default 'Geral',
  power_watts numeric not null check (power_watts >= 0),
  hours_per_day numeric not null check (hours_per_day between 0 and 24),
  days_per_month numeric not null check (days_per_month between 0 and 31),
  snapshot jsonb not null default '{}'::jsonb,
  unique (preset_id, appliance_id, name, category, power_watts, hours_per_day, days_per_month)
);

create table public.catalog_submissions (
  id uuid primary key default gen_random_uuid(),
  kind public.submission_kind not null,
  payload jsonb not null,
  submitted_by uuid not null references auth.users(id),
  submitted_by_name text,
  status public.submission_status not null default 'pending',
  moderator_id uuid references auth.users(id),
  moderation_reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  moderated_at timestamptz
);

create table public.event_quizzes (
  id uuid primary key default gen_random_uuid(),
  event_key text not null,
  title text not null,
  enabled boolean not null default false,
  reward_enabled boolean not null default false,
  starts_at timestamptz,
  ends_at timestamptz,
  created_by_user_id uuid references auth.users(id),
  created_by_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (event_key)
);

create table public.quiz_questions (
  id uuid primary key default gen_random_uuid(),
  quiz_id uuid not null references public.event_quizzes(id) on delete cascade,
  prompt text not null,
  explanation text not null,
  options jsonb not null check (jsonb_typeof(options) = 'array'),
  correct_option integer not null check (correct_option >= 0),
  status public.content_status not null default 'published',
  created_by_user_id uuid references auth.users(id),
  created_by_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.quiz_attempts (
  id uuid primary key default gen_random_uuid(),
  quiz_id uuid not null references public.event_quizzes(id) on delete cascade,
  session_id text not null,
  participant_user_id uuid references auth.users(id),
  participant_name text,
  score integer not null default 0 check (score >= 0),
  completed_at timestamptz,
  participation_code text,
  created_at timestamptz not null default now(),
  unique (quiz_id, session_id)
);

create table public.quiz_answers (
  id uuid primary key default gen_random_uuid(),
  attempt_id uuid not null references public.quiz_attempts(id) on delete cascade,
  question_id uuid not null references public.quiz_questions(id),
  selected_option integer not null check (selected_option >= 0),
  is_correct boolean not null,
  answered_at timestamptz not null default now(),
  unique (attempt_id, question_id)
);

create index official_appliances_status_idx on public.official_appliances(status);
create index official_pc_components_status_category_idx on public.official_pc_components(status, category);
create index official_facts_status_idx on public.official_facts(status);
create index official_presets_status_idx on public.official_presets(status);
create index official_preset_items_preset_idx on public.official_preset_items(preset_id);
create index personal_appliances_owner_idx on public.personal_appliances(owner_user_id);
create index personal_presets_event_idx on public.personal_presets(visibility, comparison_consent, monthly_kwh);
create index catalog_submissions_status_kind_idx on public.catalog_submissions(status, kind, created_at);
create index quiz_questions_quiz_status_idx on public.quiz_questions(quiz_id, status);
create index quiz_attempts_participant_idx on public.quiz_attempts(participant_user_id, quiz_id);

create trigger official_appliances_updated_at before update on public.official_appliances for each row execute function public.touch_updated_at();
create trigger official_pc_components_updated_at before update on public.official_pc_components for each row execute function public.touch_updated_at();
create trigger official_facts_updated_at before update on public.official_facts for each row execute function public.touch_updated_at();
create trigger official_presets_updated_at before update on public.official_presets for each row execute function public.touch_updated_at();
create trigger personal_appliances_updated_at before update on public.personal_appliances for each row execute function public.touch_updated_at();
create trigger personal_presets_updated_at before update on public.personal_presets for each row execute function public.touch_updated_at();
create trigger catalog_submissions_updated_at before update on public.catalog_submissions for each row execute function public.touch_updated_at();
create trigger event_quizzes_updated_at before update on public.event_quizzes for each row execute function public.touch_updated_at();
create trigger quiz_questions_updated_at before update on public.quiz_questions for each row execute function public.touch_updated_at();

alter table public.official_appliances enable row level security;
alter table public.official_pc_components enable row level security;
alter table public.official_facts enable row level security;
alter table public.official_presets enable row level security;
alter table public.official_preset_items enable row level security;
alter table public.personal_appliances enable row level security;
alter table public.personal_presets enable row level security;
alter table public.personal_preset_items enable row level security;
alter table public.catalog_submissions enable row level security;
alter table public.event_quizzes enable row level security;
alter table public.quiz_questions enable row level security;
alter table public.quiz_attempts enable row level security;
alter table public.quiz_answers enable row level security;

create policy official_appliances_public_read on public.official_appliances for select using (status = 'published');
create policy official_pc_components_public_read on public.official_pc_components for select using (status = 'published');
create policy official_facts_public_read on public.official_facts for select using (status = 'published');
create policy official_presets_public_read on public.official_presets for select using (status = 'published');
create policy official_preset_items_public_read on public.official_preset_items for select using (exists (select 1 from public.official_presets p where p.id = preset_id and p.status = 'published'));

create policy personal_appliances_owner_access on public.personal_appliances for all using (owner_user_id = auth.uid()) with check (owner_user_id = auth.uid());
create policy personal_presets_owner_access on public.personal_presets for all using (owner_user_id = auth.uid()) with check (owner_user_id = auth.uid());
create policy personal_preset_items_owner_access on public.personal_preset_items for all using (exists (select 1 from public.personal_presets p where p.id = preset_id and p.owner_user_id = auth.uid())) with check (exists (select 1 from public.personal_presets p where p.id = preset_id and p.owner_user_id = auth.uid()));
create policy catalog_submissions_author_or_moderator_access on public.catalog_submissions for all using (submitted_by = auth.uid() or public.is_moderator()) with check (submitted_by = auth.uid() or public.is_moderator());
create policy event_quizzes_public_read on public.event_quizzes for select using (enabled = true);
create policy event_quizzes_moderator_write on public.event_quizzes for all using (public.is_moderator()) with check (public.is_moderator());
create policy quiz_questions_public_read on public.quiz_questions for select using (status = 'published' and exists (select 1 from public.event_quizzes q where q.id = quiz_id and q.enabled = true));
create policy quiz_questions_moderator_write on public.quiz_questions for all using (public.is_moderator()) with check (public.is_moderator());
create policy quiz_attempts_participant_access on public.quiz_attempts for select using (participant_user_id = auth.uid() or participant_user_id is null);
create policy quiz_attempts_participant_insert on public.quiz_attempts for insert with check (participant_user_id = auth.uid() or participant_user_id is null);
create policy quiz_answers_participant_access on public.quiz_answers for all using (exists (select 1 from public.quiz_attempts a where a.id = attempt_id and (a.participant_user_id = auth.uid() or a.participant_user_id is null))) with check (exists (select 1 from public.quiz_attempts a where a.id = attempt_id and (a.participant_user_id = auth.uid() or a.participant_user_id is null)));

create policy official_appliances_moderator_write on public.official_appliances for all using (public.is_moderator()) with check (public.is_moderator());
create policy official_pc_components_moderator_write on public.official_pc_components for all using (public.is_moderator()) with check (public.is_moderator());
create policy official_facts_moderator_write on public.official_facts for all using (public.is_moderator()) with check (public.is_moderator());
create policy official_presets_moderator_write on public.official_presets for all using (public.is_moderator()) with check (public.is_moderator());
create policy official_preset_items_moderator_write on public.official_preset_items for all using (public.is_moderator()) with check (public.is_moderator());
