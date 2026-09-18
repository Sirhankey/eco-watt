## 1. Setup e Estrutura Inicial

- [x] 1.1 Criar requirements.txt com streamlit, plotly e pytest
- [x] 1.2 Criar estrutura de diretórios (`ecowatt/`, `components/`, `services/`, `models/`, `data/`, `pages/`, `tests/`)
- [x] 1.3 Criar arquivos de dados iniciais (`data/appliances.json`, `data/pc_components.json`, `data/presets.json`, `data/facts.json`)

## 2. Modelos e Motor de Cálculo (Core Services)

- [x] 2.1 Implementar dataclasses em `models/appliance.py` e `models/pc_component.py`
- [x] 2.2 Implementar `services/energy_calculator.py` com funções puras de kWh (dia, mês, ano) e validações defensivas
- [x] 2.3 Implementar `services/cost_calculator.py` para cálculos de tarifa e projeções financeiras
- [x] 2.4 Implementar `services/comparison_service.py` para deltas entre aparelhos e PCs
- [x] 2.5 Implementar `services/pc_energy_service.py` com cálculo de consumo ponderado por perfil de atividade
- [x] 2.6 Implementar `services/preset_service.py` para carregamento de presets e validador de fatura real
- [x] 2.7 Escrever suíte de testes unitários em `tests/` cobrindo todos os cálculos e validações

## 3. Componentes Visuais e Utilitários de Interface

- [x] 3.1 Implementar `components/cards.py` com cards de métricas, badges e caixas de "Você sabia?"
- [x] 3.2 Implementar `components/charts.py` com gráficos Plotly (barras, pizza/donut de distribuição da casa e evolução temporal)
- [x] 3.3 Implementar `utils/session.py` para inicialização e manutenção segura do `st.session_state`

## 4. Páginas e Telas da Aplicação

- [x] 4.1 Implementar `app.py` com Dashboard principal, boas-vindas e resumo interativo
- [x] 4.2 Implementar `pages/1_⚡_Calculadora.py` para análise individual de aparelhos
- [x] 4.3 Implementar `pages/2_🔄_Comparador.py` para comparação direta entre 2 aparelhos
- [x] 4.4 Implementar `pages/3_🏠_Minha_Casa.py` com inventário residencial, ranking, presets e validador de fatura real
- [x] 4.5 Implementar `pages/4_🖥️_PC_Builder.py` com montador de PC, perfis de uso e comparador de setups
- [x] 4.6 Implementar `pages/5_🏷️_Eficiencia.py` com guia de eficiência energética e conteúdo didático
- [x] 4.7 Implementar `pages/6_🎤_Modo_Apresentacao.py` para demonstrações rápidas de 30 segundos em sala de aula

## 5. Documentação e Polimento Final

- [x] 5.1 Criar README.md completo e didático com conceitos de W, kW, kWh, R$/kWh e guia de execução
- [x] 5.2 Executar suite de testes pytest e validação geral da interface Streamlit
