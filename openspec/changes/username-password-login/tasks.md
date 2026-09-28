## 1. Confirmar políticas e modelo de dados

- [x] 1.1 Definir validade padrão da sessão autenticada e o evento/quiz usado como escopo de tentativa única.
- [x] 1.2 Definir quais resultados pseudonimizados podem permanecer após a limpeza pós-evento e por quanto tempo.
- [x] 1.3 Especificar normalização e limites de tamanho/caracteres para nome de usuário e senha, considerando digitação na feira.
- [x] 1.4 Mapear todas as tabelas e eventos que carregam identidade do participante, distinguindo `participant_id` de `analytics_session_id`.

## 2. Persistência e migrações

- [x] 2.1 Criar migration para participantes com UUID interno, username normalizado único, hash de senha, troca obrigatória e timestamps.
- [x] 2.2 Criar migration para sessões autenticadas com hash de token, expiração, revogação e índice de lookup.
- [x] 2.3 Adicionar vínculos de participante paralelos aos campos legados de `auth.users`, preservando registros sem associação inferida.
- [x] 2.4 Adicionar vínculo `participant_id` aos registros analíticos preservando o identificador independente da sessão de visita.
- [x] 2.5 Configurar constraints, índices, cascade/retention e políticas que neguem acesso anônimo a credenciais, sessões e dados privados.
- [x] 2.6 Validar aplicação sequencial das migrations em banco Supabase local limpo, incluindo as estruturas da change anterior.

## 3. Serviço de autenticação

- [x] 3.1 Adicionar dependência mantida para hash/verificação de senha com Argon2id e cobrir criação/verificação de hashes.
- [x] 3.2 Implementar repositório servidor para cadastro, consulta de disponibilidade, login e carregamento por username normalizado.
- [x] 3.3 Impor unicidade no banco e traduzir conflito concorrente em resposta de nome indisponível.
- [x] 3.4 Implementar tokens de sessão aleatórios, persistindo apenas hashes e validando expiração/revogação.
- [x] 3.5 Implementar logout, troca obrigatória da senha temporária e limites de tentativas/frequência de login.
- [x] 3.6 Adicionar testes unitários de cadastro, username case-insensitive, concorrência, login válido/inválido, expiração, revogação e troca de senha.

## 4. Fluxo Streamlit e identidade compartilhada

- [x] 4.1 Substituir identificação atual por telas/fluxo de cadastro e login integrados à inicialização comum da aplicação.
- [x] 4.2 Validar disponibilidade de username na interface sem depender dessa verificação para garantir unicidade.
- [x] 4.3 Persistir o token de sessão em cookie seguro compatível com o mecanismo escolhido e restaurar a identidade em F5 e novas abas.
- [x] 4.4 Remover identidade autenticada de query parameters e garantir que senhas/tokens não apareçam em URLs ou logs.
- [x] 4.5 Disponibilizar logout e exibir o username autenticado sem expor credenciais.
- [ ] 4.6 Atualizar testes de sessão e verificar o fluxo em páginas diferentes do aplicativo.

## 5. Vincular dados e persistir o quiz

- [x] 5.1 Atualizar logging/analytics para anexar `participant_id` validado mantendo `analytics_session_id` separado.
- [x] 5.2 Atualizar serviços de catálogo e presets pessoais para usar o ID autenticado e aplicar escopo de proprietário.
- [x] 5.3 Persistir tentativas e respostas do quiz no banco, usando a regra definida de unicidade por participante e quiz/evento.
- [x] 5.4 Restaurar tentativa incompleta/concluída após F5 e impedir nova tentativa dentro do escopo configurado.
- [x] 5.5 Adicionar testes de isolamento entre participantes e de restauração/bloqueio do quiz após recarga.

## 6. Operação administrativa e encerramento

- [x] 6.1 Criar script de reset de senha por username que use senha temporária configurada, grave hash e exija troca no próximo login.
- [x] 6.2 Garantir que o script não exponha a senha temporária em argumentos, logs ou mensagens de erro.
- [x] 6.3 Criar rotina de encerramento com modo dry-run, revogação de sessões e remoção de contas/dados pessoais conforme retenção aprovada.
- [x] 6.4 Documentar configuração de segredos, operação de reset, validade de sessão, migração e limpeza pós-evento.
- [x] 6.5 Testar reset para username existente/inexistente e limpeza em modo dry-run e execução controlada.

## 7. Validação e liberação

- [ ] 7.1 Executar a suíte de testes e validar as migrations/policies no ambiente de staging.
- [ ] 7.2 Fazer ensaio manual de cadastro, login, F5, nova aba, logout, reset de senha e retomada do quiz.
- [x] 7.3 Confirmar que modo offline/fallback não comunica falsamente que conta ou tentativa foram persistidas.
- [x] 7.4 Ativar a autenticação por configuração/flag e documentar rollback sem restaurar identidade em query parameters.