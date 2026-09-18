# ⚡ EcoWatt — Guia Didático e Documentação

O **EcoWatt** é um aplicativo educacional interativo criado para ensinar sobre consumo consciente de energia elétrica, cálculo de custos na fatura de luz e eficiência energética. Desenvolvido com uma abordagem didática, visual e moderna, foi concebido tanto para uso pessoal em casa quanto para apresentações escolares e feiras de ciências por estudantes de todas as idades.

---

## 🎯 Conceitos Fundamentais de Energia

Para entender como funciona a conta de energia elétrica, quatro grandezas são essenciais:

1. **Watt (W) — Potência Instantânea:**
   Representa a quantidade de energia que o aparelho demanda no instante em que está ligado.
   *Exemplo:* Uma lâmpada consome 10 W, enquanto um chuveiro demanda 5.500 W.

2. **Quilowatt (kW):**
   É simplesmente 1.000 Watts ($1\text{ kW} = 1.000\text{ W}$). É usado para simplificar números grandes.

3. **Quilowatt-hora (kWh) — Consumo de Energia:**
   É a energia total consumida ao longo do tempo. É calculada multiplicando a potência pelo tempo que o aparelho ficou ligado.
   $$\text{Consumo (kWh)} = \frac{\text{Potência (W)}}{1000} \times \text{Horas/dia} \times \text{Dias/mês}$$

4. **Tarifa (R$/kWh) — O Custo Financeiro:**
   É o valor cobrado pela concessionária por cada kWh consumido.
   $$\text{Custo (R\$)} = \text{Consumo (kWh)} \times \text{Tarifa (R\$/kWh)}$$

---

## 🚀 Funcionalidades do EcoWatt

- **⚡ Dashboard Inicial:** Visão consolidada do consumo mensal da casa, projeção anual, custo estimado e gráfico de distribuição por cômodo.
- **⚡ Calculadora Individual:** Permite analisar qualquer eletrodoméstico informando potência em Watts, horas de uso e dias no mês.
- **🔄 Comparador de Aparelhos:** Coloca 2 produtos ou hábitos lado a lado e mostra a diferença em kWh e reais poupados no ano.
- **🏠 Simulador "Minha Casa":** Inventário com presets didáticos prontos ("Casa Típica", "Casa Sustentável", "Quarto Gamer"), ranking dos aparelhos vilões e **Validador de Conta Real**.
- **🖥️ PC Energy Builder:** Montador de computador interativo (CPU, GPU, RAM, Monitor) com cálculo ponderado por perfil de uso (estudo, jogos, ocioso, standby) e impacto da certificação da fonte (80 Plus).
- **🏷️ Eficiência Energética:** Cartilha didática explicando a etiqueta nacional (Selo Procel/Inmetro) e dicas práticas de economia.
- **🎤 Modo Apresentação:** Interface minimalista em tela cheia pensada para apresentações rápidas de 30 segundos em sala de aula.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+** (com type hints e dataclasses)
- **Streamlit** (interface web interativa e fluida)
- **Plotly** (gráficos interativos de barras, donuts e linhas temporais)
- **JSON** (banco de dados didático offline para aparelhos, hardware e presets)
- **Pytest** (suíte de testes unitários para o motor de cálculos)

---

## 💻 Como Executar o Projeto

1. **Instalar as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Executar a aplicação:**

   ```bash
   streamlit run app.py
   ```

3. **Executar os testes unitários:**

   ```bash
   pytest tests/
   ```

---

## 📂 Estrutura do Projeto

```text
eco-watt/
├── app.py                     # Dashboard Principal
├── requirements.txt           # Dependências
├── README.md                  # Guia Didático e Documentação
│
├── ecowatt/
│   ├── models/                # Dataclasses tipadas (Appliance, PCComponent)
│   ├── services/              # Funções matemáticas puras e desacopladas
│   ├── components/            # Componentes visuais (cards, métricas, gráficos)
│   ├── data/                  # Catálogos em JSON (presets, aparelhos, fatos)
│   └── utils/                 # Gerenciamento de sessão
│
├── pages/                     # Páginas nativas do Streamlit
│   ├── 1_⚡_Calculadora.py
│   ├── 2_🔄_Comparador.py
│   ├── 3_🏠_Minha_Casa.py
│   ├── 4_🖥️_PC_Builder.py
│   ├── 5_🏷️_Eficiencia.py
│   └── 6_🎤_Modo_Apresentacao.py
│
└── tests/                     # Testes automatizados com pytest
```
