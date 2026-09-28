# Governanca de dados interativos

## Identidade e visibilidade

- `created_by_user_id` e `submitted_by` identificam o autor com um UUID da conta autenticada.
- `created_by_name` e `submitted_by_name` sao snapshots administrativos capturados no momento da criacao; nao devem ser exibidos em catalogos, ranking ou telas publicas.
- Comparacoes de casas usam somente `pseudonymous_label` quando `comparison_consent = true` e o evento estiver habilitado.
- Ranking nominal e exposicao publica de respostas do quiz ficam desabilitados por padrao.

## Retencao

- Presets pessoais e aparelhos pessoais: mantidos enquanto a conta existir ou ate exclusao solicitada pelo participante.
- Nomes capturados, respostas e resultados do quiz: excluir ate 30 dias apos o encerramento do evento, salvo necessidade administrativa documentada.
- Submissoes de catalogo e auditoria de moderacao: manter por 180 dias apos a decisao; depois anonimizar o nome e conservar apenas o registro tecnico necessario.
- A equipe deve registrar o `event_key`, a data de encerramento e qualquer extensao de prazo na operacao do evento.

## Conta administrativa do evento

A moderacao exige uma conta autenticada no Supabase com `app_metadata.role` igual a `moderator` ou `admin`. O papel deve ser concedido somente pela equipe responsavel pelo projeto. A chave `service_role` fica restrita a migrations, importacao idempotente e rotinas administrativas; ela nunca deve ser enviada ao navegador ou configurada como segredo de participante.

## Operacao e rollback

As flags de catalogo remoto, presets pessoais, PC Builder interativo e quiz devem poder ser desabilitadas individualmente. Com as flags desligadas, os loaders retornam aos JSONs locais e os calculos continuam disponiveis. Dados persistidos novos nao precisam ser removidos para executar o rollback.

Os instantes sao armazenados como `timestamptz` em UTC pelo Supabase. A apresentacao para o evento converte apenas a exibicao para `America/Sao_Paulo`.
