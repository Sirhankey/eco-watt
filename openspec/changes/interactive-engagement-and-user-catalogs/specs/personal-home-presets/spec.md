## ADDED Requirements

### Requirement: Salvamento de preset pessoal
O usuário SHALL poder salvar o inventário atual, tarifa, nome do cenário e snapshots dos valores usados em um preset pessoal.

#### Scenario: Salvar casa
- **WHEN** o usuário informa um nome válido e confirma o salvamento
- **THEN** o sistema persiste um preset privado associado ao usuário com seus itens e consumo mensal calculado

### Requirement: Reutilização sem alterar preset oficial
O sistema SHALL permitir carregar um preset pessoal para a sessão sem permitir edição dos presets oficiais.

#### Scenario: Aplicar preset pessoal
- **WHEN** o usuário seleciona um preset pessoal salvo
- **THEN** o inventário da sessão é preenchido pelos snapshots salvos e os presets oficiais permanecem inalterados

### Requirement: Comparação de consumo residencial
O sistema SHALL calcular comparações de menor e maior consumo entre presets autorizados usando kWh mensal.

#### Scenario: Ranking consentido
- **WHEN** o organizador habilita a comparação para um evento e existem presets com consentimento
- **THEN** o sistema identifica o menor e o maior consumo pelo kWh mensal e exibe rótulos pseudônimos

#### Scenario: Sem consentimento
- **WHEN** um preset não autoriza compartilhamento para comparação
- **THEN** o preset participa apenas da área privada do proprietário e não aparece no ranking