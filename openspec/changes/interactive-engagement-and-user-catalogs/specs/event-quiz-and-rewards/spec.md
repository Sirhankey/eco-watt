## ADDED Requirements

### Requirement: Quiz educativo configurável
O sistema SHALL oferecer quizzes compostos por perguntas e respostas mantidas pela equipe, com explicação educativa para cada resposta.

#### Scenario: Início do quiz
- **WHEN** o participante inicia um quiz ativo do evento
- **THEN** o sistema apresenta perguntas aprovadas em ordem embaralhada e registra a tentativa

### Requirement: Uma tentativa por sessão
O sistema SHALL limitar cada participante a uma tentativa por quiz e sessão de evento.

#### Scenario: Tentativa repetida
- **WHEN** o participante tenta iniciar novamente um quiz já concluído na mesma sessão
- **THEN** o sistema mostra o resultado anterior e não cria uma nova pontuação

### Requirement: Resultado e recompensa simbólica
Ao finalizar, o sistema SHALL calcular a pontuação, mostrar acertos e explicações e gerar um código de participação quando a premiação estiver habilitada.

#### Scenario: Quiz finalizado
- **WHEN** o participante responde todas as perguntas
- **THEN** o sistema salva pontuação e timestamp, mostra o resultado e informa o código simbólico de participação

#### Scenario: Premiação desabilitada
- **WHEN** o quiz está ativo sem premiação configurada
- **THEN** o sistema mostra o resultado educativo sem gerar promessa ou benefício material