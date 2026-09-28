## ADDED Requirements

### Requirement: Separação entre catálogo oficial e conteúdo do usuário
O sistema SHALL manter itens oficiais, itens privados do usuário e sugestões para publicação em escopos distintos.

#### Scenario: Item pessoal não aparece no catálogo global
- **WHEN** um usuário cria um aparelho ou componente para sua própria simulação
- **THEN** o item fica associado ao usuário e não aparece nos seletores globais de outros usuários

#### Scenario: Sugestão aguarda aprovação
- **WHEN** um usuário envia um item para publicação
- **THEN** o sistema registra a sugestão como `pending` e não a disponibiliza como item oficial até uma aprovação

### Requirement: Autoria e timestamps auditáveis
Cada item persistido SHALL registrar o identificador do autor, o nome capturado no momento da criação e `created_at`/`updated_at` como `timestamptz`.

#### Scenario: Registro de autoria
- **WHEN** um item é criado
- **THEN** o registro contém `created_by_user_id`, `created_by_name` e o instante de criação gerado pelo banco

#### Scenario: Exibição no fuso do evento
- **WHEN** a aplicação mostra a data de criação para um participante no Brasil
- **THEN** converte o instante para `America/Sao_Paulo` sem alterar o valor armazenado em UTC

### Requirement: Validação de duplicidade
O sistema SHALL impedir a criação de itens duplicados dentro do mesmo escopo, usando comparação normalizada e proteção de unicidade no banco.

#### Scenario: Duplicata evidente
- **WHEN** o usuário tenta cadastrar um item com nome e dados equivalentes a um item já existente no mesmo escopo
- **THEN** a operação é rejeitada e a interface informa que o item já foi criado

#### Scenario: Nomes com diferenças irrelevantes
- **WHEN** o nome recebido difere apenas por maiúsculas, espaços extras ou pontuação simples
- **THEN** o sistema trata os nomes como equivalentes para a verificação de duplicidade

### Requirement: Validação e moderação de conteúdo
Itens recebidos SHALL respeitar limites de tamanho, valores numéricos válidos e ausência de HTML/script; somente moderadores SHALL publicar sugestões.

#### Scenario: Dados inválidos
- **WHEN** uma submissão contém potência negativa, texto acima do limite ou conteúdo HTML/script
- **THEN** o sistema rejeita a submissão antes de persistir o item publicável

#### Scenario: Aprovação administrativa
- **WHEN** um moderador aprova uma sugestão válida
- **THEN** o sistema cria ou promove o registro oficial, mantém o autor e registra `approved_by` e `approved_at`