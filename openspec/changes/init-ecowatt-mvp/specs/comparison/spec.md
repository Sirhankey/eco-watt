## ADDED Requirements

### Requirement: Comparação Direta entre Dois Aparelhos
The system SHALL compare two appliances (A and B) displaying differences in monthly/annual consumption in kWh and cost in R$.

#### Scenario: Comparação com indicação de menor consumo
- **WHEN** o Aparelho A consome 60 kWh/mês e o Aparelho B consome 96 kWh/mês
- **THEN** o sistema DEVE indicar que o Aparelho A apresenta menor consumo com economia calculada de 36 kWh/mês e a diferença anual em reais

#### Scenario: Cuidado conceitual sobre eficiência
- **WHEN** os resultados da comparação forem apresentados
- **THEN** o sistema NÃO DEVE afirmar categoricamente que o aparelho de menor potência é mais eficiente sem ressaltar o contexto de trabalho e uso
