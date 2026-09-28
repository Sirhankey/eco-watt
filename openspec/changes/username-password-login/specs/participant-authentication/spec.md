## ADDED Requirements

### Requirement: Cadastro com nome de usuário único
O sistema SHALL permitir que um participante crie uma conta usando nome de usuário ASCII de 3 a 24 caracteres (`a-z`, `0-9`, ponto, sublinhado ou hífen) e senha de 6 a 128 caracteres, sem exigir e-mail, e SHALL atribuir um identificador interno imutável à conta. O username SHALL ser normalizado sem diferenciar maiúsculas/minúsculas.

#### Scenario: Nome de usuário disponível
- **WHEN** o participante envia um nome de usuário válido ainda não cadastrado e uma senha válida
- **THEN** o sistema cria a conta e retorna a identidade associada ao ID interno, sem armazenar a senha em texto puro

#### Scenario: Nome de usuário já utilizado
- **WHEN** o participante tenta cadastrar um nome que já existe após normalização case-insensitive
- **THEN** o sistema rejeita o cadastro e informa que o nome não está disponível

#### Scenario: Cadastros concorrentes
- **WHEN** duas requisições tentam cadastrar simultaneamente o mesmo nome normalizado
- **THEN** no máximo uma conta é criada e a outra recebe uma resposta de nome indisponível

### Requirement: Login sem e-mail
O sistema SHALL autenticar participantes por nome de usuário e senha e SHALL validar credenciais sem expor se uma senha armazenada está correta por comparação insegura.

#### Scenario: Credenciais válidas
- **WHEN** um participante envia nome de usuário e senha corretos
- **THEN** o sistema inicia uma sessão autenticada associada ao ID interno da conta

#### Scenario: Credenciais inválidas
- **WHEN** um participante envia credenciais incorretas
- **THEN** o sistema não inicia sessão e apresenta uma mensagem que não revela qual campo corresponde a uma conta existente

### Requirement: Sessão autenticada persistente
O sistema SHALL restaurar uma sessão autenticada após recarga e navegação em novas abas do mesmo navegador por até 30 dias, salvo revogação antecipada, e SHALL permitir logout com revogação da sessão.

#### Scenario: Recarregar a aplicação
- **WHEN** um participante autenticado atualiza a página enquanto sua sessão não expirou
- **THEN** o sistema restaura a conta autenticada e o acesso aos dados vinculados ao seu ID

#### Scenario: Abrir outra aba
- **WHEN** um participante autenticado abre outra aba da aplicação no mesmo navegador
- **THEN** a nova aba reconhece a sessão válida sem solicitar novo login

#### Scenario: Sessão expirada ou revogada
- **WHEN** o token de sessão expirou, foi revogado ou não corresponde a uma sessão persistida
- **THEN** o sistema remove a autenticação local e solicita novo login

#### Scenario: Logout
- **WHEN** o participante escolhe sair
- **THEN** o sistema revoga a sessão persistida, remove o cookie e retorna ao fluxo de login

### Requirement: Segredos de autenticação protegidos
O sistema SHALL armazenar somente hashes de senhas e tokens de sessão, SHALL manter credenciais administrativas exclusivamente no servidor e SHALL impedir que credenciais ou tokens de sessão sejam escritos em query parameters ou logs.

#### Scenario: Persistência de credenciais
- **WHEN** uma conta ou sessão é criada
- **THEN** o banco armazena hash com algoritmo apropriado e nunca o valor original da senha ou token

#### Scenario: Identidade fora da URL
- **WHEN** a aplicação cria ou restaura uma sessão autenticada
- **THEN** URL e query parameters não contêm senha, token de sessão ou payload de identidade autenticada

### Requirement: Reset administrativo sem e-mail
O sistema SHALL fornecer à equipe um procedimento/script administrativo para redefinir a senha temporariamente a partir do nome de usuário, sem expor a nova senha em logs, e SHALL exigir a troca da senha temporária no próximo login.

#### Scenario: Reset de conta existente
- **WHEN** a equipe executa o reset para um nome de usuário existente
- **THEN** a senha é substituída por um hash temporário e a conta deve escolher nova senha antes de continuar

#### Scenario: Reset de conta inexistente
- **WHEN** a equipe executa o reset para um nome de usuário inexistente
- **THEN** o script informa que nenhuma conta foi alterada e não cria usuário implicitamente

### Requirement: Identidade estável e sessão de visita distintas
O sistema SHALL associar dados pertencentes ao participante ao ID interno imutável da conta e SHALL manter esse ID distinto do identificador de uma sessão de analytics/visita.

#### Scenario: Registrar evento analítico
- **WHEN** um participante autenticado gera um evento
- **THEN** o evento pode ser associado ao ID interno do participante e registra separadamente o ID da sessão de visita

#### Scenario: Reutilizar identidade entre páginas
- **WHEN** o participante navega entre páginas da aplicação durante uma sessão autenticada
- **THEN** cada página usa o mesmo ID interno validado para escopo dos dados do participante

### Requirement: Tentativa de quiz vinculada ao participante
O sistema SHALL persistir tentativas do quiz vinculadas ao ID interno do participante e SHALL recuperar a tentativa existente após recarga, permitindo no máximo uma tentativa por participante, por quiz e evento. Cada quiz SHALL estar associado a um evento identificável.

#### Scenario: Retomar quiz incompleto
- **WHEN** o participante atualiza a página com uma tentativa incompleta já persistida
- **THEN** o sistema restaura as respostas e o progresso da tentativa existente

#### Scenario: Restaurar quiz concluído
- **WHEN** o participante autenticado retorna após concluir o quiz
- **THEN** o sistema apresenta a tentativa e nota existentes e não permite criar outra tentativa dentro do escopo configurado

### Requirement: Encerramento e retenção de contas
O sistema SHALL fornecer um procedimento administrativo de encerramento que permita inspecionar os dados que serão removidos, revogar sessões e apagar credenciais e dados pessoais de contas após a apresentação, mantendo resultados pseudonimizados até uma ação explícita de limpeza pela equipe.

#### Scenario: Simular limpeza
- **WHEN** a equipe executa o procedimento em modo de simulação
- **THEN** o sistema lista os registros e contagens que seriam removidos sem alterar dados

#### Scenario: Remover contas após a apresentação
- **WHEN** a equipe confirma a limpeza após a apresentação
- **THEN** sessões e credenciais são revogadas/removidas e dados pessoais associados são removidos, enquanto resultados pseudonimizados permanecem até a equipe solicitar sua limpeza