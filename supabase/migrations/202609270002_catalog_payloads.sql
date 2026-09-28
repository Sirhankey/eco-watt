-- Compatibility patch for databases that already ran the first migration.
alter table if exists public.official_appliances
  add column if not exists source_payload jsonb not null default '{}'::jsonb;

alter table if exists public.official_pc_components
  add column if not exists source_payload jsonb not null default '{}'::jsonb;

alter table if exists public.official_facts
  add column if not exists source_payload jsonb not null default '{}'::jsonb;

alter table if exists public.official_presets
  add column if not exists source_payload jsonb not null default '{}'::jsonb;
