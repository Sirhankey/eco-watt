create table public.experience_feedback (
  id uuid primary key default gen_random_uuid(),
  participant_id uuid not null unique references public.participants(id) on delete cascade,
  rating smallint not null check (rating between 1 and 5),
  knew_kwh text not null check (char_length(knew_kwh) between 1 and 40),
  helped_bill text not null check (char_length(helped_bill) between 1 and 40),
  main_interest text not null check (char_length(main_interest) between 1 and 60),
  learned text check (learned is null or char_length(learned) <= 300),
  created_at timestamptz not null default now()
);

alter table public.experience_feedback enable row level security;

comment on table public.experience_feedback is
  'One end-of-visit survey per participant. Written only by the server with the service role.';
