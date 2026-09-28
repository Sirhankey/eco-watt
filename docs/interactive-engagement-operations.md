# Operacao das funcionalidades interativas

## Configuracao

Configure `SUPABASE_URL` e `SUPABASE_ANON_KEY` para leitura do catalogo no aplicativo. `SUPABASE_SERVICE_ROLE_KEY` fica reservado ao importador e analytics administrativo; nunca deve ser exposta em paginas Streamlit.

As migrations em `supabase/migrations/` devem ser aplicadas antes do primeiro import. Para conferir o conteudo local sem acessar o backend:

```powershell
python scripts/import_catalogs.py --dry-run
```

Para importar em um ambiente autorizado, defina os dois segredos e execute o mesmo script sem `--dry-run`. O upsert preserva os IDs dos JSONs, todos os campos relevantes e os itens aninhados em `snapshot`, marca os registros como `source = migration` e cria um quiz inicial desabilitado com perguntas aprovadas.

O seed nao cria aparelhos, presets ou submissoes pessoais com UUID ficticio: essas tabelas referenciam `auth.users`. Para popular dados de demonstracao de uma conta existente, use a opcao explicita `--demo-user-id SEU_UUID_AUTH`; nunca use um UUID inventado.

Os timestamps sao armazenados como `timestamptz` em UTC. A exibicao do evento usa `America/Sao_Paulo`. RLS permite leitura somente de conteudo publicado, acesso de proprietario a dados pessoais e escrita administrativa para contas cujo `app_metadata.role` seja `moderator` ou `admin`.

## Feature flags

As flags podem ser definidas como variaveis de ambiente ou secrets Streamlit:

- `ECOWATT_FEATURE_CATALOG_REMOTE`
- `ECOWATT_FEATURE_PERSONAL_PRESETS`
- `ECOWATT_FEATURE_PC_BUILDER_V2`
- `ECOWATT_FEATURE_EVENT_QUIZ`

Desative as flags de banco, quiz ou interface para rollback. Os JSONs locais continuam sendo o fallback dos loaders e os calculos existentes permanecem disponiveis. Nenhum registro novo precisa ser apagado para voltar ao modo offline.

## Evento e privacidade

O quiz nao gera beneficio material. A exportacao administrativa omite nomes por padrao e a comparacao de casas exige consentimento e rotulo pseudonimo. Consulte [interactive-engagement-data-governance.md](interactive-engagement-data-governance.md) para retencao e visibilidade.