-- ============================================================
-- CONSULTAS DE ANALYTICS DO ECOWATT
-- Execute uma consulta por vez no Supabase SQL Editor.
-- A tabela utilizada e: public.analytics_events
-- ============================================================

-- 1. EVENTOS RECENTES
-- Mostra eventos recentes sem username ou dados demograficos.
select
  id,
  occurred_at,
  event,
  participant_id,
  session_id,
  details
from public.analytics_events
order by occurred_at desc
limit 50;


-- 2. RESUMO GERAL
-- Conta eventos, sessoes e participantes identificados.
select
  count(*) as total_eventos,
  count(distinct session_id) as sessoes,
  count(distinct coalesce(participant_id::text, user_id::text)) as participantes
from public.analytics_events;


-- 3. PAGINAS MAIS ACESSADAS
-- Mostra quantas vezes cada tela foi aberta.
-- O nome da pagina fica dentro do campo JSONB details.
select
  details->>'page' as pagina,
  count(*) as acessos
from public.analytics_events
where event = 'page_view'
group by details->>'page'
order by acessos desc;


-- 4. PERFIL DOS PARTICIPANTES (DADOS HISTORICOS)
-- Eventos novos nao coletam perfil demografico.
select
  role as perfil,
  count(distinct user_id) as participantes
from public.analytics_events
where event = 'user_identified'
group by role
order by participantes desc;


-- 5. FAIXA ETARIA (DADOS HISTORICOS)
-- Resume os participantes por faixa etaria.
select
  age_group as faixa_etaria,
  count(distinct user_id) as participantes
from public.analytics_events
where event = 'user_identified'
group by age_group
order by participantes desc;


-- 6. GENERO (DADOS HISTORICOS)
-- Resume os participantes por resposta de genero.
select
  gender as genero,
  count(distinct user_id) as participantes
from public.analytics_events
where event = 'user_identified'
group by gender
order by participantes desc;


-- 7. AREAS PREFERIDAS
-- Mostra qual area foi escolhida como mais interessante no feedback.
select
  details->>'main_interest' as area,
  count(*) as respostas
from public.analytics_events
where event = 'experience_feedback_submitted'
group by details->>'main_interest'
order by respostas desc;


-- 8. MEDIA DAS AVALIACOES
-- Calcula a media das notas de 1 a 5 estrelas.
select
  round(avg((details->>'rating')::numeric), 2) as media,
  count(*) as total_avaliacoes
from public.analytics_events
where event = 'experience_feedback_submitted';


-- 9. DISTRIBUICAO DAS ESTRELAS
-- Mostra quantas respostas receberam cada nota.
select
  (details->>'rating')::integer as estrelas,
  count(*) as respostas
from public.analytics_events
where event = 'experience_feedback_submitted'
group by (details->>'rating')::integer
order by estrelas;


-- 10. CONHECIMENTO PREVIO SOBRE KWH
-- Mostra quantas pessoas ja conheciam kWh antes do aplicativo.
select
  details->>'knew_kwh' as conhecimento_previo,
  count(*) as respostas
from public.analytics_events
where event = 'experience_feedback_submitted'
group by details->>'knew_kwh'
order by respostas desc;


-- 11. AJUDA PARA ENTENDER A CONTA
-- Mostra se o aplicativo ajudou a entender a conta de energia.
select
  details->>'helped_bill' as resposta,
  count(*) as respostas
from public.analytics_events
where event = 'experience_feedback_submitted'
group by details->>'helped_bill'
order by respostas desc;


-- 12. FEEDBACK COMPLETO
-- Lista as respostas e seus IDs pseudonimos sem nome ou demografia.
select
  occurred_at,
  participant_id,
  session_id,
  (details->>'rating')::integer as estrelas,
  details->>'knew_kwh' as conhecia_kwh,
  details->>'helped_bill' as ajudou_conta,
  details->>'main_interest' as area_interessante,
  details->>'learned' as o_que_aprendeu
from public.analytics_events
where event = 'experience_feedback_submitted'
order by occurred_at desc;


-- 13. USUARIOS DISPONIVEIS
-- Lista IDs pseudonimos para consultar o fluxo individual.
select
  coalesce(participant_id::text, user_id::text) as participant_id,
  count(*) as total_eventos,
  min(occurred_at) as primeiro_acesso,
  max(occurred_at) as ultimo_acesso
from public.analytics_events
where participant_id is not null or user_id is not null
group by coalesce(participant_id::text, user_id::text)
order by ultimo_acesso desc;


-- 14. FLUXO DE TELAS DE TODOS OS USUARIOS
-- Mostra cada tela acessada em ordem cronologica.
select
  coalesce(participant_id::text, user_id::text) as participant_id,
  session_id,
  occurred_at,
  details->>'page' as pagina
from public.analytics_events
where event = 'page_view'
order by participant_id, session_id, occurred_at;


-- 15. FLUXO AGRUPADO POR SESSAO
-- Cria uma linha por sessao, por exemplo:
-- calculator -> comparison -> home_simulator -> pc_builder
select
  coalesce(participant_id::text, user_id::text) as participant_id,
  session_id,
  min(occurred_at) as inicio_sessao,
  max(occurred_at) as fim_sessao,
  count(*) as total_telas,
  string_agg(
    coalesce(details->>'page', 'desconhecida'),
    ' -> '
    order by occurred_at
  ) as fluxo
from public.analytics_events
where event = 'page_view'
group by coalesce(participant_id::text, user_id::text), session_id
order by inicio_sessao desc;


-- 16. TODOS OS EVENTOS DE UM USUARIO
-- Altere o participant_id na CTE parametros; use a consulta 13 para encontra-lo.
with parametros as (
  select 'COLE_PARTICIPANT_ID_AQUI'::text as participant_id
)
select
  e.occurred_at,
  e.event,
  e.details->>'page' as pagina,
  e.details
from public.analytics_events e
cross join parametros p
where coalesce(e.participant_id::text, e.user_id::text) = p.participant_id
order by e.occurred_at;


-- 17. FLUXO DE UM USUARIO EM UMA SESSAO
-- Altere participant_id e session_id na CTE parametros.
with parametros as (
  select
    'COLE_PARTICIPANT_ID_AQUI'::text as participant_id,
    'COLE_SESSION_ID_AQUI'::text as session_id
)
select
  e.occurred_at,
  e.event,
  e.details->>'page' as pagina,
  e.details
from public.analytics_events e
cross join parametros p
where coalesce(e.participant_id::text, e.user_id::text) = p.participant_id
  and e.session_id = p.session_id
order by e.occurred_at;


-- 18. FLUXOS MAIS COMUNS
-- Agrupa a sequencia de paginas por sessao e conta as repeticoes.
with fluxos as (
  select
    session_id,
    string_agg(
      coalesce(details->>'page', 'desconhecida'),
      ' -> '
      order by occurred_at
    ) as fluxo
  from public.analytics_events
  where event = 'page_view'
  group by session_id
)
select
  fluxo,
  count(*) as sessoes
from fluxos
group by fluxo
order by sessoes desc, fluxo;


-- 19. ACOES MAIS REALIZADAS
-- Resume os eventos de interacao alem da navegacao entre paginas.
select
  event,
  count(*) as ocorrencias,
  count(distinct coalesce(participant_id::text, user_id::text)) as participantes,
  count(distinct session_id) as sessoes
from public.analytics_events
where event <> 'page_view'
group by event
order by ocorrencias desc;


-- 20. ATIVIDADE POR DIA
-- Mostra o movimento diario da feira.
select
  date(occurred_at) as dia,
  count(*) as total_eventos,
  count(distinct coalesce(participant_id::text, user_id::text)) as participantes,
  count(distinct session_id) as sessoes
from public.analytics_events
group by date(occurred_at)
order by dia desc;


-- ============================================================
-- OBSERVACOES
-- participant_id: UUID pseudonimo estavel da conta; user_id serve a eventos historicos.
-- session_id: identificador de uma sessao de acesso.
-- page_view: evento de abertura de uma tela.
-- details: dados especificos do evento em formato JSONB.
-- Execute uma consulta por vez para evitar varios resultados juntos.
-- ============================================================
