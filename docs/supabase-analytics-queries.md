# Consultas de Analytics no Supabase

Consultas para executar em **Supabase → SQL Editor** sobre a tabela `public.analytics_events`.

A coluna `details` é do tipo `jsonb`. Eventos de navegação usam `details->>'page'`; eventos de feedback usam campos como `details->>'rating'` e `details->>'main_interest'`.

## 1. Eventos recentes

Mostra os últimos eventos registrados sem expor username ou dados demográficos.

```sql
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
```

## 2. Resumo geral

Conta o total de eventos, sessões e participantes identificados.

```sql
select
  count(*) as total_eventos,
  count(distinct session_id) as sessoes,
  count(distinct coalesce(participant_id::text, user_id::text)) as participantes
from public.analytics_events;
```

## 3. Páginas mais acessadas

Mostra quantas vezes cada página foi aberta.

```sql
select
  details->>'page' as pagina,
  count(*) as acessos
from public.analytics_events
where event = 'page_view'
group by details->>'page'
order by acessos desc;
```

## 4. Perfil dos participantes (dados históricos)

Consulta apenas eventos antigos de identificação; contas novas não coletam perfil demográfico.

```sql
select
  role as perfil,
  count(distinct user_id) as participantes
from public.analytics_events
where event = 'user_identified'
group by role
order by participantes desc;
```

## 5. Faixa etária (dados históricos)

Resume os participantes por faixa etária.

```sql
select
  age_group as faixa_etaria,
  count(distinct user_id) as participantes
from public.analytics_events
where event = 'user_identified'
group by age_group
order by participantes desc;
```

## 6. Gênero (dados históricos)

Resume os participantes por resposta de gênero.

```sql
select
  gender as genero,
  count(distinct user_id) as participantes
from public.analytics_events
where event = 'user_identified'
group by gender
order by participantes desc;
```

## 7. Áreas preferidas

Mostra qual área foi escolhida como mais interessante na avaliação final.

```sql
select
  details->>'main_interest' as area,
  count(*) as respostas
from public.analytics_events
where event = 'experience_feedback_submitted'
group by details->>'main_interest'
order by respostas desc;
```

## 8. Média das avaliações

Calcula a média das notas de 1 a 5 estrelas.

```sql
select
  round(avg((details->>'rating')::numeric), 2) as media,
  count(*) as total_avaliacoes
from public.analytics_events
where event = 'experience_feedback_submitted';
```

## 9. Distribuição das estrelas

Mostra quantas avaliações receberam cada nota.

```sql
select
  (details->>'rating')::integer as estrelas,
  count(*) as respostas
from public.analytics_events
where event = 'experience_feedback_submitted'
group by (details->>'rating')::integer
order by estrelas;
```

## 10. Conhecimento prévio sobre kWh

Mostra quantas pessoas já conheciam kWh antes de usar o aplicativo.

```sql
select
  details->>'knew_kwh' as conhecimento_previo,
  count(*) as respostas
from public.analytics_events
where event = 'experience_feedback_submitted'
group by details->>'knew_kwh'
order by respostas desc;
```

## 11. Ajuda para entender a conta

Mostra se o aplicativo ajudou a entender a conta de energia.

```sql
select
  details->>'helped_bill' as resposta,
  count(*) as respostas
from public.analytics_events
where event = 'experience_feedback_submitted'
group by details->>'helped_bill'
order by respostas desc;
```

## 12. Feedback completo

Lista avaliações e seus identificadores pseudônimos, sem nome ou demografia.

```sql
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
```

## 13. Usuários disponíveis

Lista IDs pseudônimos para consultar o fluxo individual.

```sql
select
  coalesce(participant_id::text, user_id::text) as participant_id,
  count(*) as total_eventos,
  min(occurred_at) as primeiro_acesso,
  max(occurred_at) as ultimo_acesso
from public.analytics_events
where participant_id is not null or user_id is not null
group by coalesce(participant_id::text, user_id::text)
order by ultimo_acesso desc;
```

## 14. Fluxo de telas de todos os usuários

Mostra cada tela acessada, em ordem cronológica, por usuário e sessão.

```sql
select
  coalesce(participant_id::text, user_id::text) as participant_id,
  session_id,
  occurred_at,
  details->>'page' as pagina
from public.analytics_events
where event = 'page_view'
order by participant_id, session_id, occurred_at;
```

## 15. Fluxo agrupado em uma linha por sessão

Transforma cada sessão em uma sequência como `calculator → comparison → pc_builder`.

```sql
select
  coalesce(participant_id::text, user_id::text) as participant_id,
  session_id,
  min(occurred_at) as inicio_sessao,
  max(occurred_at) as fim_sessao,
  count(*) as total_telas,
  string_agg(
    coalesce(details->>'page', 'desconhecida'),
    ' → '
    order by occurred_at
  ) as fluxo
from public.analytics_events
where event = 'page_view'
group by coalesce(participant_id::text, user_id::text), session_id
order by inicio_sessao desc;
```

## 16. Todos os eventos de um usuário

Substitua `COLE_PARTICIPANT_ID_AQUI` pelo ID obtido na consulta 13.

```sql
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
```

## 17. Fluxo de um usuário em uma sessão específica

Use quando quiser analisar uma visita específica. Substitua os dois valores.

```sql
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
```

## 18. Fluxos mais comuns

Agrupa a sequência de páginas por sessão e mostra quais caminhos foram mais frequentes.

```sql
with fluxos as (
  select
    session_id,
    string_agg(
      coalesce(details->>'page', 'desconhecida'),
      ' → '
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
```

## 19. Ações mais realizadas

Resume os eventos de interação registrados além da navegação.

```sql
select
  event,
  count(*) as ocorrencias,
  count(distinct coalesce(participant_id::text, user_id::text)) as participantes,
  count(distinct session_id) as sessoes
from public.analytics_events
where event <> 'page_view'
group by event
order by ocorrencias desc;
```

## 20. Atividade por dia

Ajuda a acompanhar o movimento durante a feira.

```sql
select
  date(occurred_at) as dia,
  count(*) as total_eventos,
  count(distinct coalesce(participant_id::text, user_id::text)) as participantes,
  count(distinct session_id) as sessoes
from public.analytics_events
group by date(occurred_at)
order by dia desc;
```

## Observações

- `participant_id` é o UUID pseudônimo estável da conta; `user_id` aparece apenas como compatibilidade com eventos históricos.
- `session_id` identifica uma visita e pode mudar entre sessões do mesmo participante.
- `page_view` registra a abertura de uma tela.
- `details` armazena os dados específicos de cada evento em formato JSONB.
- Para consultas que usam `rating`, o cast para `integer` permite calcular média e ordenar numericamente.
- Se uma consulta retornar zero linhas, faça uma ação no aplicativo e confira se os secrets do Supabase estão configurados no Streamlit Cloud.
