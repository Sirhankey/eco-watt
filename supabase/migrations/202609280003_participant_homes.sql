create table public.participant_homes (
  id uuid primary key default gen_random_uuid(),
  participant_id uuid not null unique references public.participants(id) on delete cascade,
  name text not null check (char_length(btrim(name)) between 1 and 120),
  tariff numeric not null check (tariff > 0),
  monthly_kwh numeric not null default 0 check (monthly_kwh >= 0),
  rooms jsonb not null default '[]'::jsonb check (jsonb_typeof(rooms) = 'array'),
  appliances jsonb not null default '[]'::jsonb check (jsonb_typeof(appliances) = 'array'),
  is_public boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index participant_homes_public_name_idx
  on public.participant_homes(name)
  where is_public;

create trigger participant_homes_updated_at
before update on public.participant_homes
for each row execute function public.touch_updated_at();

alter table public.participant_homes enable row level security;

comment on table public.participant_homes is
  'One saved household snapshot per participant. Set is_public=true administratively to publish it as a shared preset.';
comment on column public.participant_homes.is_public is
  'Administrator-controlled publication flag; participant UI cannot change it.';