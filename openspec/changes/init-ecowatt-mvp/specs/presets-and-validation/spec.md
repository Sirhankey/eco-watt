## ADDED Requirements

### Requirement: Carregamento de Cenários Pré-configurados (Presets)
The system SHALL load pre-configured educational scenarios from JSON files to populate the simulator with one click.

#### Scenario: Aplicação instantânea de preset
- **WHEN** o usuário seleciona um preset e clica em aplicar
- **THEN** os aparelhos e parâmetros correspondentes DEVEM ser carregados imediatamente na simulação ativa

### Requirement: Validador de Conta Real vs Consumo Estimado
The system SHALL compare the simulated household consumption against a user-provided real electricity bill and explain discrepancies.

#### Scenario: Comparação com fatura real
- **WHEN** o usuário informa o valor de sua fatura real
- **THEN** o sistema DEVE calcular a diferença em kWh e R$ e sugerir possíveis explicações didáticas (consumo fantasma/standby, perdas ou hábitos não mapeados)
