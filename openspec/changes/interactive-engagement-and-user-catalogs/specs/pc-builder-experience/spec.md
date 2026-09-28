## ADDED Requirements

### Requirement: Montagem guiada de PC
O PC Builder SHALL apresentar a montagem em etapas claras para componentes, perfil de uso e resultado, mantendo um resumo visível da configuração atual.

#### Scenario: Seleção de configuração
- **WHEN** o usuário escolhe CPU, GPU, memória, armazenamento, monitor e acessórios
- **THEN** o resumo atualiza os componentes selecionados sem perder as escolhas ao navegar entre as etapas

### Requirement: Feedback imediato de consumo
O PC Builder SHALL recalcular consumo e custo ao alterar componentes ou perfil, usando o serviço energético existente.

#### Scenario: Alteração de GPU
- **WHEN** o usuário troca a GPU
- **THEN** potência estimada, consumo mensal e custo são atualizados e a UI identifica o impacto da troca

### Requirement: Comparação de setups
O PC Builder SHALL permitir comparar duas configurações e destacar diferenças de potência, kWh e custo.

#### Scenario: Comparação concluída
- **WHEN** o usuário confirma dois setups válidos
- **THEN** o sistema mostra os indicadores de ambos e a diferença absoluta de consumo e custo

### Requirement: Componentes pessoais controlados
Componentes pessoais SHALL ser utilizáveis pelo próprio autor e componentes sugeridos SHALL aparecer globalmente somente após aprovação.

#### Scenario: Componente pessoal no builder
- **WHEN** o autor seleciona um componente pessoal aprovado para sua conta
- **THEN** o componente pode participar do cálculo sem alterar o catálogo de outros usuários