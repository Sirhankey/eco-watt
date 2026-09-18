## ADDED Requirements

### Requirement: Montagem de Configuração de Hardware
The system SHALL calculate total estimated PC power based on selected hardware components (CPU, GPU, RAM, storage, peripherals, monitor).

#### Scenario: Estimativa da potência instalada
- **WHEN** uma CPU de 65W e uma GPU de 160W forem selecionadas junto com componentes básicos
- **THEN** o sistema DEVE computar a potência nominal máxima estimada do sistema

### Requirement: Simulação de Perfis de Uso Ponderados
The system SHALL compute monthly consumption applying workload weighting factors according to activity hours (studies, gaming, light usage, standby).

#### Scenario: Consumo ponderado por carga
- **WHEN** o usuário informar 4h de jogos e 2h de estudos ao dia
- **THEN** o sistema DEVE aplicar os fatores de carga correspondentes para cada componente em vez de assumir TDP máximo constante
