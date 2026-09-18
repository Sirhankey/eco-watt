## ADDED Requirements

### Requirement: Calculadora Interativa de Aparelhos
The system SHALL allow the user to select an existing appliance or enter custom name, power in Watts, hours/day, days/month, and tariff in R$/kWh.

#### Scenario: Atualização imediata dos resultados
- **WHEN** o usuário ajusta qualquer parâmetro na interface
- **THEN** o sistema DEVE atualizar imediatamente os valores de consumo diário, mensal, anual e seus respectivos custos em R$

#### Scenario: Explicação didática do resultado
- **WHEN** um cálculo for exibido na calculadora
- **THEN** o sistema DEVE apresentar uma frase explicativa amigável contextualizando o impacto daquele aparelho
