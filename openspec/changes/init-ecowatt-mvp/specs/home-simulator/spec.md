## ADDED Requirements

### Requirement: Montagem do Inventário Residencial
The system SHALL allow users to add, edit, and remove multiple household appliances to calculate aggregate monthly kWh and financial cost.

#### Scenario: Cálculo do consumo total da casa
- **WHEN** múltiplos aparelhos estiverem ativos no simulador da casa
- **THEN** o sistema DEVE somar o consumo individual e calcular o consumo mensal total em kWh e o custo total em R$

### Requirement: Ranking e Distribuição Percentual
The system SHALL sort appliances by consumption in descending order and compute the percentage contribution of each appliance.

#### Scenario: Visualização do ranking dos maiores consumidores
- **WHEN** a casa possuir aparelhos como ar-condicionado e lâmpada LED
- **THEN** o sistema DEVE ordenar e destacar o ar-condicionado no topo do ranking com seu respectivo percentual
