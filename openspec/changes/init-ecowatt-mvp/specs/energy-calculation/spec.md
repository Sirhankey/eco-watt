## ADDED Requirements

### Requirement: Cálculo de Consumo em kWh
The system SHALL calculate energy consumption in kWh based on power in Watts, daily hours, and days per month using `(power_watts / 1000) * hours_per_day * days_per_month`.

#### Scenario: Cálculo de consumo mensal padrão
- **WHEN** uma potência de 1000 W for utilizada por 2 horas ao dia durante 30 dias
- **THEN** o consumo calculado DEVE ser exatamente 60,0 kWh

#### Scenario: Validação de entradas não-negativas
- **WHEN** qualquer parâmetro (potência, horas ou dias) for menor ou igual a zero ou horas excederem 24
- **THEN** o sistema DEVE levantar uma exceção com mensagem clara e amigável

### Requirement: Cálculo de Custo Financeiro
The system SHALL calculate financial cost in R$ across daily, monthly, and annual periods based on user-provided tariff in R$/kWh.

#### Scenario: Projeção de custo mensal e anual
- **WHEN** o consumo mensal for de 60 kWh e a tarifa for R$ 0,80/kWh
- **THEN** o custo mensal DEVE ser R$ 48,00 e o custo anual DEVE ser R$ 576,00
