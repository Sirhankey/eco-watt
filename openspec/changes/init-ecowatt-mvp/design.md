## Context

O EcoWatt é um aplicativo educacional para projetos escolares sobre consumo e economia de energia elétrica. O objetivo técnico é fornecer uma aplicação visualmente rica e fluida em Streamlit, mas rigorosamente desacoplada em serviços puros de Python e arquivos JSON para dados de referência, garantindo 100% de testabilidade via pytest e facilidade de apresentação em sala de aula através de cenários pré-configurados (presets) e um validador de fatura real.

## Goals / Non-Goals

**Goals:**
- Implementar uma arquitetura de 3 camadas estritas: Apresentação (Streamlit), Regras de Negócio (Services puros em Python) e Dados/Modelos (JSON + Dataclasses).
- Suportar todas as funcionalidades do MVP: Dashboard, Calculadora, Comparador, Minha Casa, PC Energy Builder e Eficiência Energética.
- Disponibilizar presets (cenários didáticos prontos) e validador de conta real (Consumo Calculado vs Fatura Real).
- Cobertura de testes unitários para todas as fórmulas de consumo, custo, perdas e perfis de hardware.
- Interface responsiva com identidade visual moderna (cards, métricas, ícones, gráficos Plotly).

**Non-Goals:**
- Não implementar banco de dados relacional ou NoSQL (manter 100% offline em JSON).
- Não implementar autenticação de usuários ou perfis na nuvem.
- Não implementar integração com hardware real (smart plugs ou IoT).
- Não inventar tarifas ou fatores de emissão como se fossem oficiais da ANEEL sem rotulá-los como estimativa didática.

## Decisions

### 1. Separação Estrita de Serviços Puros
- **Decisão:** Colocar toda a matemática de energia em `ecowatt/services/` sem nenhuma dependência de `streamlit` ou bibliotecas gráficas.
- **Alternativa Considerada:** Implementar as fórmulas diretamente nos callbacks do Streamlit.
- **Justificativa:** Funções puras (`energy_calculator.py`, `pc_energy_service.py`) permitem testes unitários instantâneos com `pytest` e reutilização futura em apps mobile ou CLI.

### 2. Streamlit Multi-page com Gerenciamento de Estado Centralizado
- **Decisão:** Utilizar a estrutura nativa de páginas do Streamlit (`pages/1_⚡_Calculadora.py`, etc.) com um módulo utilitário para garantir que `st.session_state` persista os aparelhos da casa e os componentes do PC entre navegações.
- **Alternativa Considerada:** Uma única página gigantesca com abas (`st.tabs`).
- **Justificativa:** Páginas separadas organizam a experiência visual e facilitam a apresentação temática sem poluição visual.

### 3. Presets Didáticos e Validador de Conta Real em JSON
- **Decisão:** Criar `data/presets.json` contendo perfis prontos ("Casa Sustentável", "Casa Típica", "Quarto Gamer") e um componente de validação comparando o consumo estimado contra o valor pago na fatura de energia.
- **Alternativa Considerada:** Forçar o usuário a digitar tudo do zero a cada execução.
- **Justificativa:** Numa apresentação escolar curta, poder carregar um cenário com um clique poupa tempo e engaja a turma imediatamente.

### 4. Ponderação Realista no PC Energy Builder
- **Decisão:** O cálculo de energia do computador não usará a soma simples dos TDPs em 100%, mas sim um modelo ponderado de consumo por atividade (ex: Estudo = 25% da carga, Jogos = 85% da carga, Standby = ~5W).
- **Alternativa Considerada:** Assumir consumo constante no TDP máximo.
- **Justificativa:** É mais preciso didaticamente e ensina que a potência nominal não é o consumo contínuo.

## Risks / Trade-offs

- [Reset de Session State no Streamlit ao recarregar página (F5)] → Mitigação: inicialização defensiva de valores padrão e opção de recarregar preset com um clique.
- [Valores de potência informados inválidos (negativos ou zero)] → Mitigação: validações estritas nos serviços levantando `ValueError` com mensagens amigáveis na UI.
- [Percepção de que os dados são tarifas oficiais] → Mitigação: badges e notas de rodapé claras informando que são valores médios/estimativos e permitindo edição livre pelo usuário.
