## Context

O aplicativo é uma aplicação Streamlit com estado de sessão em memória. A identificação atual é restaurada por cookie e query parameter, e o `user_id` é derivado de nome e turma; isso não fornece cadastro único com credenciais nem um ID relacional confiável. O serviço do quiz também mantém tentativas apenas em memória, e a migration anterior referencia `auth.users`, embora os participantes não usem Supabase Auth.

A nova change introduz contas locais ao aplicativo, sem e-mail. As credenciais e sessões devem ser manipuladas somente no servidor Streamlit; conteúdo público continua acessível pelos loaders existentes. O uso inicial é uma feira escolar, com operação administrativa simples e limpeza planejada ao fim da apresentação.

## Goals / Non-Goals

**Goals:**

- Permitir cadastro com nome de usuário único e senha e login sem e-mail.
- Reutilizar um ID interno imutável para associar tentativas, eventos e dados pessoais às páginas do aplicativo.
- Preservar autenticação após recarga e entre abas no mesmo navegador, com logout explícito.
- Persistir tentativas do quiz vinculadas ao usuário, para restaurar progresso/resultado após F5 e impedir uma segunda tentativa conforme a regra do quiz.
- Permitir à equipe redefinir a senha de uma conta por nome de usuário usando um script administrativo.
- Documentar uma rotina de encerramento e remoção dos dados de conta/sessão após a apresentação.

**Non-Goals:**

- Recuperação automática de senha por e-mail, telefone ou perguntas de segurança.
- Supabase Auth, login social, múltiplos papéis/permissões de organização ou autenticação corporativa.
- Implementar ranking nesta change; os resultados devem apenas permanecer vinculáveis pelo ID durante o período de retenção definido.
- Garantir que uma pessoa não crie mais de uma conta ou impedir compartilhamento voluntário de credenciais.

## Decisions

### 1. Contas próprias do aplicativo

Criar uma tabela privada de participantes com UUID interno, nome de usuário normalizado e único, hash de senha, indicador de troca obrigatória de senha e timestamps. Username terá de 3 a 24 caracteres ASCII (`a-z`, `0-9`, ponto, sublinhado ou hífen), será normalizado com trim e minúsculas, e a constraint única no banco será a autoridade contra cadastros concorrentes. Senha terá de 6 a 128 caracteres, sem regra de composição adicional.

Alternativas consideradas: manter a identidade derivada de nome/turma não autentica o participante nem impede colisões; exigir e-mail/Supabase Auth contraria o fluxo sem e-mail definido para a feira.

### 2. Senha e reset administrativo

Armazenar somente hashes produzidos por Argon2id (ou biblioteca mantida equivalente), com parâmetros recomendados pela biblioteca. O reset será um script de operador executado no servidor, que recebe o nome de usuário e define uma senha temporária configurada para a feira, armazenando apenas seu hash e marcando a conta para troca no próximo login. A senha temporária não será impressa em logs nem passada como argumento visível de processo.

Alternativa considerada: gravar uma senha padrão comum sem troca obrigatória é mais simples operacionalmente, mas permite que qualquer pessoa que conheça um usuário tome a conta. A troca obrigatória mantém o procedimento simples e reduz esse risco.

### 3. Sessão autenticada persistente

Após autenticação, emitir um token aleatório opaco, persistir somente seu hash em uma tabela de sessões e colocar o token no cookie do navegador com validade limitada ao período da feira/configuração. Em cada execução, validar o token no servidor e carregar o UUID e nome de usuário para `st.session_state`. Logout revoga a sessão no banco e remove o cookie. O token e as credenciais nunca serão gravados em query parameters.

Uma sessão de analytics/visita permanece separada: ela identifica uma visita e pode mudar após nova conexão, enquanto `participant_id` permanece estável. A validade padrão do login será de 30 dias, configurável e revogável no encerramento do evento. O `streamlit-cookies-controller` atual suporta `Secure` e `SameSite`, mas não `HttpOnly`; nesta frente será usado um token aleatório opaco, cookie `Secure` em HTTPS com `SameSite=Strict`, persistência somente do hash no banco, expiração curta configurável e revogação no logout. O token será acessível a JavaScript, portanto a aplicação não deve inserir conteúdo não confiável como HTML e deve manter o escaping/sanitização das entradas. Se for necessário garantir `HttpOnly`, será preciso introduzir um endpoint/proxy de autenticação separado em uma frente posterior.

Alternativas consideradas: guardar o ID do usuário diretamente no cookie não prova autenticação; depender apenas de `st.session_state` perde a sessão em F5; colocar token na URL o expõe em histórico e logs.

### 4. Escopo de acesso e vínculo dos dados

Criar repositório de autenticação usado exclusivamente pelo código servidor e nunca enviar credenciais privilegiadas ao navegador. As consultas e mutações devem receber o ID validado da sessão e filtrar os registros por proprietário. Migrar as relações que hoje apontam para `auth.users` para o UUID da tabela própria, incluindo tentativas do quiz e dados pessoais aplicáveis. Analytics devem registrar `participant_id` pseudônimo e manter `analytics_session_id` separado.

Como o app Streamlit executa acesso ao banco no servidor, qualquer chave privilegiada usada por esse repositório deve permanecer em secrets do servidor. A política de acesso do banco deve negar acesso anônimo às tabelas privadas; operações privilegiadas devem ficar encapsuladas no repositório/RPC necessário, evitando consultas genéricas sem escopo.

### 5. Retenção e encerramento da feira

Fornecer procedimento administrativo de encerramento que revogue sessões e remova credenciais/contas e dados pessoais após a apresentação. Resultados do quiz podem permanecer pseudonimizados até uma decisão explícita de limpeza pela equipe; hashes de senha e tokens nunca são retidos. O procedimento deve suportar simulação/listagem do que será removido antes da execução efetiva e oferecer limpeza separada dos resultados pseudonimizados.

## Risks / Trade-offs

- [Senha fraca ou compartilhada] → Exigir comprimento mínimo razoável, guardar hash Argon2id e limitar tentativas de login; a equipe pode redefinir senha temporária.
- [Enumeração de nomes durante cadastro/login] → Responder com mensagens neutras onde a existência do usuário não precisa ser revelada e limitar frequência de consultas/tentativas.
- [Token de sessão roubado] → Token aleatório de alta entropia, hash no banco, validade curta alinhada ao evento, logout/revogação e cookie seguro.
- [Service key contorna RLS] → Manter apenas no servidor, centralizar acesso em repositório pequeno, filtrar por ID autenticado e negar consultas privadas pela chave anônima.
- [Mudança quebra dados existentes ligados a `auth.users`] → Criar migration compatível, mapear ou manter registros legados sem associação quando não houver correspondência verificável; não inferir identidade por nome.
- [Remoção encerra possibilidade de ranking nominal] → Remover credenciais e sessões, manter resultados pseudonimizados até limpeza manual explícita e executar limpeza com dry-run.
- [Cookie JavaScript-readable pode ser roubado por XSS] → Usar Secure/SameSite, token aleatório revogável e expirável, não renderizar conteúdo não confiável como HTML e migrar para endpoint/proxy com HttpOnly caso o modelo de ameaça exija.

## Migration Plan

1. Criar tabela de participantes, constraint de username normalizado, tabela de sessões e políticas/mecanismos privados de acesso.
2. Atualizar relações de tentativas e dados pessoais para o novo UUID; adicionar `participant_id` aos registros analíticos sem confundir com ID de sessão.
3. Implementar autenticação e sessão persistente no servidor; remover o ID/objeto de identidade de query parameters e migrar a inicialização compartilhada das páginas.
4. Integrar o serviço do quiz para carregar, gravar e bloquear tentativas por usuário e quiz, mantendo a regra de tentativa acordada.
5. Adicionar script administrativo de reset e procedimento de limpeza com dry-run; testar em ambiente de staging antes do evento.
6. Liberar por flag/configuração. Em rollback, desativar cadastro/login novo e preservar dados já gravados para migração posterior; não voltar a expor identidade em URLs.

## Resolved Policies

- Login persistente por 30 dias, com revogação no encerramento do evento.
- Uma tentativa por participante, por quiz e evento; cada `quiz_id` identifica o quiz/evento no modelo atual.
- Após a apresentação, apagar credenciais e sessões; manter resultados pseudonimizados até a equipe solicitar sua limpeza.
- Username ASCII de 3 a 24 caracteres (`a-z`, `0-9`, ponto, sublinhado ou hífen), normalizado sem diferenciar maiúsculas/minúsculas; senha de 6 a 128 caracteres.

## Identity Data Map

- `st.session_state.user_id`, cookie `ecowatt_identity` e query parameter `participant` representam a identidade atual derivada de nome/turma; o query parameter precisa ser removido no novo fluxo.
- `analytics_events.user_id` liga eventos à identidade atual e `analytics_events.session_id` liga eventos à visita; a nova conta preencherá `participant_id` estável e manterá o ID de visita separado.
- `personal_appliances.owner_user_id`, `personal_presets.owner_user_id`, `catalog_submissions.submitted_by` e `quiz_attempts.participant_user_id` são os principais vínculos de participante existentes e hoje apontam para `auth.users` na migration.
- `quiz_attempts.session_id` e `QuizService.attempts[(quiz_id, session_id)]` limitam tentativas à sessão em memória, não à conta persistida.
- `created_by_user_id` dos catálogos oficiais e `moderator_id` são referências administrativas a `auth.users`; devem permanecer distintas das contas de participante.