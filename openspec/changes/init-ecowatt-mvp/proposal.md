## Why

O EcoWatt é um aplicativo educacional interativo criado para ensinar estudantes e famílias sobre consumo consciente de energia elétrica, custos reais na conta de luz e eficiência energética. É necessário estabelecer o MVP completo com interface moderna em Streamlit, desacoplada das regras de cálculo em Python puro, incluindo cenários pré-configurados (presets) e validador de conta real para viabilizar apresentações escolares ágeis e engajadoras sem necessidade de banco de dados.

## What Changes

- Criação da arquitetura desacoplada: interface Streamlit, motor de cálculos energéticos puros e modelos de dados.
- Módulo de **Calculadora de Consumo**: cálculo diário, mensal e anual em kWh e R$ com base na potência, tempo de uso e tarifa personalizada.
- Módulo de **Comparador de Aparelhos**: comparação direta entre dois aparelhos com projeção de economia anual.
- Módulo de **Simulador Residencial (Minha Casa)**: montagem do perfil da residência, ranking de vilões do consumo e gráficos de distribuição.
- Módulo de **PC Energy Builder**: estimativa de consumo de computadores por componentes e perfis de uso ponderados (estudos, jogos, leve, standby).
- Módulo de **Eficiência Energética e Educação**: guia visual de etiquetas, conceitos (W vs kWh) e cards "Você sabia?".
- Módulo de **Presets & Validador de Conta Real**: perfis e setups prontos em JSON para demonstração rápida em apresentações escolares e comparação do consumo estimado versus a conta de luz real da casa.
- Bateria de testes unitários com pytest para garantir precisão e robustez dos cálculos.

## Capabilities

### New Capabilities
- `energy-calculation`: Motor central de cálculos de potência (W), energia (kWh), tarifas (R$), períodos e comparações com tratamento rigoroso de valores inválidos.
- `appliance-calculator`: Interface e serviço para cálculo individual de aparelhos elétricos e projeções de custo.
- `comparison`: Comparador de dois aparelhos ou dois setups de PC destacando diferenças de consumo e custo.
- `home-simulator`: Simulador da residência com lista de aparelhos, percentuais de contribuição e ranking de consumo.
- `pc-energy-builder`: Dimensionador didático de computadores considerando TDP de componentes e perfis de atividade.
- `energy-education`: Conteúdo educativo sobre potência vs consumo, etiquetas de eficiência e dicas de economia.
- `presets-and-validation`: Catálogo de cenários pré-configurados (JSON) para demonstrações ágeis e ferramenta de validação do consumo estimado contra a fatura real de energia.

### Modified Capabilities
*(Nenhuma - projeto greenfield)*

## Impact
- Adição de dependências: `streamlit`, `plotly`, `pytest`.
- Estrutura de código em `ecowatt/` com separação estrita entre UI, services, models e data.
- Totalmente executável offline sem dependências de infraestrutura de banco de dados.
