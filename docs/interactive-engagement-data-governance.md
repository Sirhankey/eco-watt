# Governanca de dados interativos

## Identidade e visibilidade

- Contas de participantes usam UUID interno; `participant_id` liga dados pessoais e eventos à conta enquanto ela existir.
- `created_by_user_id` e `moderator_id` continuam identificando operadores administrativos autenticados pelo Supabase Auth.
- Usernames são pseudônimos escolhidos pelo participante; eventos novos não armazenam nome real, turma ou dados demográficos.
- Comparacoes de casas usam somente `pseudonymous_label` quando `comparison_consent = true` e o evento estiver habilitado.
- Ranking nominal e exposicao publica de respostas do quiz ficam desabilitados por padrao.

## Retencao

- Credenciais e sessões autenticadas: remover após a apresentação; o token de sessão nunca é armazenado em texto puro.
- Aparelhos, presets pessoais e submissões vinculadas: removidos com a conta do participante no encerramento.
- Tentativas, respostas e pontuações do quiz: preservar somente pelo UUID pseudônimo, sem username ou hash de credencial, até a equipe solicitar a limpeza explícita.
- Analytics: novos eventos mantêm `participant_id` pseudônimo separado de `session_id`; campos históricos de nome/demografia não são preenchidos pelo login novo.
- A equipe deve registrar o `event_key`, a data de encerramento e a decisão de manter/remover resultados na operação do evento.

## Conta administrativa do evento

A moderação exige uma conta autenticada no Supabase com `app_metadata.role` igual a `moderator` ou `admin`. O papel deve ser concedido somente pela equipe responsável pelo projeto. As contas de participantes são próprias do aplicativo e não têm e-mail nem login Supabase Auth. A `service_role` é usada apenas pelo código servidor para auth e persistência privada, além de migrations e rotinas administrativas; nunca deve ser enviada ao navegador, incluída em componentes ou configurada como segredo do participante.

## Operacao e rollback

As flags de catálogo remoto, presets pessoais, PC Builder interativo, quiz e autenticação podem ser desabilitadas individualmente. Desabilitar autenticação bloqueia o acesso; não restaura a identidade antiga em query parameters. Os loaders públicos ainda podem usar JSON local, mas contas e tentativas exigem o Supabase e não são simuladas offline.

Os instantes sao armazenados como `timestamptz` em UTC pelo Supabase. A apresentacao para o evento converte apenas a exibicao para `America/Sao_Paulo`.
