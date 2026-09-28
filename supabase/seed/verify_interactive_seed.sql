-- Execute after running scripts/import_catalogs.py.
select 'official_appliances' as table_name, count(*) as rows from public.official_appliances
union all
select 'official_pc_components', count(*) from public.official_pc_components
union all
select 'official_facts', count(*) from public.official_facts
union all
select 'official_presets', count(*) from public.official_presets
union all
select 'official_preset_items', count(*) from public.official_preset_items
union all
select 'event_quizzes', count(*) from public.event_quizzes
union all
select 'quiz_questions', count(*) from public.quiz_questions
order by table_name;

select id, event_key, title, enabled, reward_enabled
from public.event_quizzes
where event_key = 'ecowatt-quiz-basics-2026';
