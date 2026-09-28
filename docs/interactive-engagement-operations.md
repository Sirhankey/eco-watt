# Operacao das funcionalidades interativas

## Configuracao

Configure `SUPABASE_URL` e `SUPABASE_ANON_KEY` para leitura do catálogo público. `SUPABASE_SERVICE_ROLE_KEY` é necessária no servidor Streamlit para autenticação e persistência privada de participantes/quiz, além dos scripts administrativos. Ela deve existir somente em secrets do servidor; nunca a envie a componentes do navegador nem a registre em logs.

As migrations em `supabase/migrations/` devem ser aplicadas antes do primeiro import. Para conferir o conteudo local sem acessar o backend:

```powershell
python scripts/import_catalogs.py --dry-run
```

Para importar em um ambiente autorizado, defina os dois segredos e execute o mesmo script sem `--dry-run`. O upsert preserva os IDs dos JSONs, todos os campos relevantes e os itens aninhados em `snapshot`, marca os registros como `source = migration` e cria um quiz inicial desabilitado com perguntas aprovadas.

O seed não cria aparelhos, presets ou submissões pessoais com UUID fictício. Registros administrativos (`created_by_user_id` e `moderator_id`) continuam referenciando `auth.users`; contas de participantes usam UUID interno próprio.

Os timestamps são armazenados como `timestamptz` em UTC. A exibição do evento usa `America/Sao_Paulo`. Tabelas de credenciais e sessões não têm políticas de acesso anônimo; o repositório de autenticação acessa dados privados apenas no servidor.

### Contas e sessões

Após aplicar as migrations, habilite o quiz (`event_quizzes.enabled = true`) para o evento correspondente. A conta exige username único e senha de 6 a 128 caracteres; o login persiste por 30 dias no mesmo navegador e não usa e-mail. O cookie é `Secure` e `SameSite=Strict`; o componente atual não fornece `HttpOnly`, por isso não renderize conteúdo de participante como HTML não sanitizado.

O cadastro/login exige `SUPABASE_SERVICE_ROLE_KEY` no servidor. Sem backend privado, a aplicação bloqueia a autenticação e não simula que a tentativa foi persistida.

### Reset de senha

Execute no servidor autorizado; o script solicita a senha temporária sem mostrá-la na tela ou nos argumentos do processo e revoga sessões ativas. A pessoa deverá escolher uma nova senha ao entrar:

```powershell
python scripts/manage_participant_accounts.py reset-password --username aluno01
```

### Encerramento e retenção

O comando padrão é somente uma simulação. Ele mostra contagens e mantém tentativas pseudonimizadas, removendo contas, sessões e dados pessoais apenas com `--execute`:

```powershell
python scripts/manage_participant_accounts.py cleanup
python scripts/manage_participant_accounts.py cleanup --execute
```

Para apagar também tentativas e respostas pseudonimizadas, solicite explicitamente a remoção:

```powershell
python scripts/manage_participant_accounts.py cleanup --execute --purge-results
```

Revise o dry-run e exporte qualquer resultado autorizado antes de executar uma remoção. A limpeza de contas não apaga resultados pseudonimizados; eles permanecem sem username até a equipe solicitar a limpeza correspondente.

## Feature flags

As flags podem ser definidas como variaveis de ambiente ou secrets Streamlit:

- `ECOWATT_FEATURE_CATALOG_REMOTE`
- `ECOWATT_FEATURE_PERSONAL_PRESETS`
- `ECOWATT_FEATURE_PC_BUILDER_V2`
- `ECOWATT_FEATURE_EVENT_QUIZ`
- `ECOWATT_FEATURE_PARTICIPANT_AUTH`

Desative a flag de autenticação para bloquear acesso autenticado; isso não restaura o fluxo antigo nem identidade em query parameters. Para rollback de código, retorne à versão anterior e preserve os registros novos até uma migração deliberada. Os JSONs locais continuam sendo fallback apenas para conteúdo público e cálculos; contas e tentativas não têm fallback offline.

## Evento e privacidade

O quiz nao gera beneficio material. A exportacao administrativa omite nomes por padrao e a comparacao de casas exige consentimento e rotulo pseudonimo. Consulte [interactive-engagement-data-governance.md](interactive-engagement-data-governance.md) para retencao e visibilidade das contas e resultados.
