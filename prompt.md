# ⚡ EcoWatt — Prompt Mestre para GitHub Copilot

## 1. Contexto do projeto

Desenvolva um aplicativo educacional chamado **EcoWatt**, criado para um projeto escolar sobre **economia de energia elétrica e consumo consciente**.

O objetivo do aplicativo é ensinar, de forma visual e interativa, como diferentes aparelhos elétricos consomem energia, quanto esse consumo representa na conta de luz e como escolhas mais eficientes podem gerar economia.

O aplicativo deve parecer um **produto real**, moderno e bem acabado, e não apenas uma calculadora escolar.

O projeto também deve ser suficientemente simples e didático para que um estudante de 14 anos consiga entender os principais conceitos e apresentar o funcionamento do aplicativo na escola.

---

# 2. Objetivos

O EcoWatt deve:

* ensinar conceitos básicos de energia elétrica;
* calcular consumo de aparelhos;
* estimar custos;
* permitir comparar aparelhos;
* demonstrar eficiência energética;
* permitir simular o consumo de uma residência;
* mostrar gráficos;
* demonstrar como hábitos de uso impactam o consumo;
* possuir um módulo especial para estimar o consumo de computadores;
* possuir arquitetura preparada para futuras funcionalidades.

O foco principal é **educação + interatividade + visualização de dados**.

---

# 3. Stack tecnológica

Utilize inicialmente:

* Python
* Streamlit
* Plotly para gráficos
* JSON ou estruturas Python simples para dados iniciais
* Python type hints
* pytest para testes

Evite adicionar banco de dados, autenticação ou infraestrutura complexa no MVP.

A arquitetura deve, entretanto, permitir que essas funcionalidades sejam adicionadas futuramente.

---

# 4. Princípios do projeto

## 4.1 Simplicidade

O código deve ser compreensível por um estudante que está aprendendo programação.

Prefira:

```python
def calculate_energy_consumption(...):
    ...
```

a soluções excessivamente abstratas.

Evite:

* overengineering;
* frameworks desnecessários;
* padrões complexos sem necessidade;
* abstrações criadas apenas para "parecer arquitetura".

---

## 4.2 Separação de responsabilidades

Mesmo sendo um projeto pequeno, não coloque toda a lógica dentro do `app.py`.

Organize aproximadamente assim:

```text
ecowatt/
│
├── app.py
│
├── pages/
│   ├── calculator.py
│   ├── comparison.py
│   ├── home_simulator.py
│   ├── pc_builder.py
│   └── efficiency.py
│
├── components/
│   ├── cards.py
│   ├── charts.py
│   ├── forms.py
│   └── metrics.py
│
├── services/
│   ├── energy_calculator.py
│   ├── cost_calculator.py
│   ├── comparison_service.py
│   └── pc_energy_service.py
│
├── data/
│   ├── appliances.json
│   ├── pc_components.json
│   └── efficiency.json
│
├── models/
│   ├── appliance.py
│   └── pc_component.py
│
├── utils/
│   └── formatting.py
│
├── tests/
│
├── requirements.txt
├── README.md
└── AGENTS.md
```

A estrutura pode ser adaptada caso exista uma solução tecnicamente melhor, mas preserve a separação entre:

**interface → regras de negócio → dados.**

---

# 5. Identidade visual

O EcoWatt deve ter aparência de aplicativo moderno de sustentabilidade/tecnologia.

Estilo:

* moderno;
* limpo;
* amigável;
* tecnológico;
* educativo;
* visualmente agradável;
* responsivo dentro das limitações do Streamlit.

Evitar aparência de:

* formulário empresarial;
* sistema administrativo;
* página cheia de tabelas;
* projeto escolar simples.

Utilizar:

* cards;
* ícones;
* métricas;
* gráficos;
* badges;
* barras de progresso;
* indicadores;
* mensagens educativas;
* boa hierarquia visual.

A tela inicial deve imediatamente comunicar:

> ⚡ Quanto você consome?
> 💰 Quanto isso custa?
> 🌱 Como economizar?

---

# 6. Dashboard principal

A página inicial deve ser um dashboard.

Exemplo conceitual:

```text
┌────────────────────────────────────────────────────┐
│ ⚡ EcoWatt                              🌱 Consumo │
├────────────────────────────────────────────────────┤
│                                                    │
│       Entenda e reduza seu consumo de energia     │
│                                                    │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐      │
│ │ ⚡ 142 kWh │ │ 💰 R$135   │ │ 🌱 -18%    │      │
│ │ consumo    │ │ estimado   │ │ potencial  │      │
│ └────────────┘ └────────────┘ └────────────┘      │
│                                                    │
│ 🔌 Calculadora                                     │
│ Descubra quanto cada aparelho consome              │
│                                                    │
│ 🏠 Minha casa                                      │
│ Simule o consumo da sua residência                │
│                                                    │
│ 🔄 Comparar aparelhos                              │
│ Descubra qual opção é mais eficiente               │
│                                                    │
│ 🖥️ PC Energy Builder                              │
│ Monte seu computador e estime o consumo            │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

# 7. MVP — Funcionalidades obrigatórias

## 7.1 ⚡ Calculadora de consumo

Permitir informar:

* nome do aparelho;
* potência em Watts;
* horas de uso por dia;
* dias de uso por mês;
* tarifa em R$/kWh.

Calcular:

```text
Consumo diário
Consumo mensal
Consumo anual
Custo diário
Custo mensal
Custo anual
```

Fórmula principal:

```text
consumo_kwh =
    (potencia_watts / 1000)
    * horas_por_dia
    * dias_por_mes
```

Custo:

```text
custo = consumo_kwh * tarifa
```

Não assumir que a tarifa é universal.

Permitir que o usuário informe a tarifa.

---

# 8. 💰 Cálculo de custo

Mostrar os resultados de maneira visual.

Exemplo:

```text
⚡ Consumo mensal
72,5 kWh

💰 Custo estimado
R$ 68,88

📅 Custo anual
R$ 826,56
```

Também mostrar uma explicação simples:

> "Esse aparelho representa aproximadamente R$ 68,88 por mês considerando os dados informados."

Adicionar opção de alterar:

* horas de uso;
* dias de uso;
* tarifa.

O resultado deve atualizar imediatamente.

---

# 9. 📊 Gráficos

Utilizar Plotly.

Criar pelo menos:

### Gráfico 1 — Consumo mensal

Barras comparando aparelhos.

### Gráfico 2 — Distribuição da casa

Exemplo:

```text
Ar-condicionado  42%
Chuveiro         31%
Computador       12%
Geladeira         8%
TV                4%
Outros            3%
```

### Gráfico 3 — Evolução do custo

Mostrar:

```text
Dia
Semana
Mês
Ano
```

Sempre utilizar visualizações simples e fáceis de interpretar.

---

# 10. 🏷️ Eficiência energética

Criar uma página educativa:

## "Entenda a eficiência energética"

Explicar de maneira simples:

* o que significa eficiência energética;
* por que dois aparelhos podem executar a mesma função consumindo quantidades diferentes de energia;
* como interpretar informações de consumo;
* como comparar produtos.

Não afirmar que uma letra específica é universal para todos os produtos.

Deixar claro que:

> A classificação e os critérios da etiqueta podem variar de acordo com a categoria do produto e as regras aplicáveis.

Mostrar visualmente uma escala de eficiência.

Criar cards explicativos:

```text
💡 Potência
Quanto o aparelho demanda quando está funcionando.

⚡ Consumo
Quanto de energia ele utiliza durante determinado período.

💰 Custo
Quanto esse consumo representa na tarifa informada.

🌱 Eficiência
Quanto trabalho o aparelho realiza em relação à energia utilizada.
```

---

# 11. 🔄 Comparador de aparelhos

Permitir selecionar dois aparelhos.

Exemplo:

```text
APARELHO A              APARELHO B

500 W                   800 W

4 h/dia                 4 h/dia

60 kWh/mês              96 kWh/mês

R$ 57/mês               R$ 91,20/mês
```

Mostrar:

```text
⚡ Diferença de consumo
36 kWh/mês

💰 Diferença de custo
R$ 34,20/mês

📅 Diferença anual
R$ 410,40
```

Adicionar uma conclusão automática:

> "O aparelho A apresenta menor consumo considerando os parâmetros informados."

Nunca declarar que um aparelho é "mais eficiente" apenas porque possui menor potência. Considerar o contexto de uso e, quando aplicável, os dados de consumo da categoria.

---

# 12. 🏠 Simulador de uma casa

Criar uma experiência onde o usuário possa adicionar diversos aparelhos.

Exemplo:

```text
Minha casa

☑ Chuveiro
☑ Geladeira
☑ TV
☑ Computador
☑ Ar-condicionado
☑ Iluminação
☑ Ventilador
☑ Máquina de lavar
```

Cada aparelho deve possuir:

```text
Nome
Potência
Horas/dia
Dias/mês
Tarifa
```

Calcular o consumo total da residência.

Mostrar:

```text
🏠 Consumo estimado

156 kWh/mês

💰 R$ 148,20/mês
💰 R$ 1.778,40/ano
```

Criar ranking:

```text
🥇 Ar-condicionado
🥈 Chuveiro
🥉 Computador
4º Geladeira
5º TV
```

Mostrar percentual de participação de cada aparelho.

---

# 13. 🖥️ PC Energy Builder

Esta é uma funcionalidade especial.

Criar um modo onde o usuário possa montar um computador.

Componentes:

### CPU

Exemplos:

* Ryzen 5 5600G
* Ryzen 5 7600
* Ryzen 7
* Core i5
* Core i7

### GPU

Exemplos:

* integrada;
* GPU dedicada de baixo consumo;
* GPU intermediária;
* GPU de alto desempenho.

### Outros

* placa-mãe;
* memória RAM;
* SSD;
* HDD;
* fans;
* periféricos;
* monitor.

Não é necessário ter uma base completa de hardware no MVP.

Começar com alguns componentes fictícios/didáticos e deixar a estrutura preparada para expansão.

---

# 14. 🖥️ Perfil de utilização do PC

Permitir informar:

### Estudos

Exemplo:

```text
2 horas/dia
```

### Jogos

```text
4 horas/dia
```

### Uso leve

```text
2 horas/dia
```

### Stand-by

```text
restante do dia
```

Calcular consumo aproximado.

Mostrar:

```text
🖥️ Potência estimada
350 W

⚡ Consumo mensal
42 kWh

💰 Custo mensal
R$ 39,90

💰 Custo anual
R$ 478,80
```

Deixar explícito que é uma **estimativa**, pois o consumo real depende da carga de trabalho, configuração, eficiência da fonte, monitor e outros fatores.

---

# 15. 🎮 Comparação de computadores

Permitir salvar duas configurações:

```text
PC Gamer A
PC Gamer B
```

Comparar:

```text
Potência estimada
Consumo mensal
Custo mensal
Custo anual
```

Mostrar:

> "A configuração B pode consumir aproximadamente X kWh a mais por ano."

---

# 16. 🧠 Modo educativo

Sempre que possível, o aplicativo deve explicar o resultado.

Não apenas:

```text
72 kWh
```

Mas:

> 💡 Você utilizou um aparelho de 1.200 W durante aproximadamente 2 horas por dia. Isso representa cerca de 72 kWh por mês.

Adicionar pequenos "Você sabia?"

Exemplos:

```text
💡 Você sabia?

Potência é medida em Watts (W),
enquanto o consumo de energia elétrica
é normalmente medido em kWh.

```

Outro:

```text
💡 Economizar alguns minutos todos os dias
pode parecer pouco, mas o efeito acumulado
ao longo de um ano pode ser significativo.
```

---

# 17. 🔮 FUNCIONALIDADES FUTURAS

A arquitetura deve ser preparada para implementar posteriormente:

## Fase 2 — Economia

### 💰 Economia anual

Mostrar:

```text
Se reduzir o uso em 30 minutos por dia:

Economia mensal: R$ XX
Economia anual: R$ XXX
```

Permitir testar diferentes cenários.

---

## Fase 3 — Desafios

Criar desafios:

### 🚿 Desafio do banho

> Reduza 5 minutos do banho durante 7 dias.

### 💡 Desafio das luzes

> Evite deixar luzes acesas em ambientes vazios.

### 🖥️ Desafio do computador

> Desligue o PC quando não estiver utilizando.

O usuário poderia acompanhar:

```text
🔥 4 dias consecutivos
⚡ 8,4 kWh economizados
💰 R$ 7,98 economizados
```

---

# 18. 🏆 Ranking

Criar futuramente:

```text
🏆 Ranking de economia

🥇 Lucas       - 32 kWh
🥈 Ana         - 27 kWh
🥉 Pedro       - 21 kWh
```

Para o MVP não implementar usuários ou ranking online.

Criar somente a arquitetura necessária para que isso possa existir futuramente.

---

# 19. 🌱 Impacto ambiental

Futuramente permitir converter energia economizada em indicadores ambientais.

Exemplo:

```text
Você economizou:

120 kWh

Isso representa uma redução
estimada de X kg de CO₂,
dependendo do fator de emissão utilizado.
```

O fator utilizado deverá ser configurável e baseado em fonte confiável.

Não inventar fatores ambientais.

---

# 20. 📈 Simulador "E se?"

Criar futuramente uma ferramenta:

## "E se eu mudar meu hábito?"

Exemplo:

```text
Uso atual:
Ar-condicionado
4h/dia

Novo uso:
3h/dia
```

Resultado:

```text
⚡ Energia economizada
36 kWh/mês

💰 Economia
R$ 34,20/mês

💰 Economia anual
R$ 410,40
```

Mostrar gráfico:

```text
ANTES ███████████████
DEPOIS ███████████
```

---

# 21. 🏠 Perfil completo da residência

Futuramente permitir salvar:

```text
Minha casa

Número de moradores
Quantidade de quartos
Cidade/UF
Tarifa
Aparelhos
Hábitos
```

Criar um perfil energético.

---

# 22. 📷 Futuramente — leitura de etiquetas

Criar arquitetura para futuramente permitir:

> "Tire uma foto da etiqueta do aparelho."

O sistema poderia utilizar OCR/IA para identificar:

* consumo;
* potência;
* modelo;
* informações da etiqueta.

Não implementar no MVP.

Criar apenas uma área preparada para essa funcionalidade.

---

# 23. 🤖 Futuramente — assistente EcoWatt

Criar posteriormente um assistente educativo:

> "Qual aparelho está gastando mais na minha casa?"

O sistema analisaria os dados cadastrados e responderia:

> "O ar-condicionado representa aproximadamente 42% do consumo estimado. Reduzir o uso em 1 hora por dia poderia representar aproximadamente X kWh por mês."

O assistente deve trabalhar inicialmente com os dados do próprio aplicativo.

---

# 24. 📱 Futuramente — aplicativo mobile

A arquitetura deve evitar dependência excessiva de componentes específicos do Streamlit.

Futuramente poderemos criar:

```text
EcoWatt Web
EcoWatt Mobile
```

compartilhando:

```text
Energy Calculation
Cost Calculation
Comparison
PC Energy
```

Ou seja:

```text
              ┌───────────────┐
              │ Energy Engine │
              └───────┬───────┘
                      │
          ┌───────────┴───────────┐
          ↓                       ↓
   Streamlit Web             Mobile App
```

---

# 25. 🗄️ Futuramente — banco de dados

No MVP utilizar JSON.

Posteriormente permitir:

* SQLite;
* PostgreSQL;
* usuários;
* casas;
* aparelhos;
* histórico;
* desafios;
* economia acumulada.

Não implementar banco no MVP sem necessidade.

---

# 26. 🌎 Futuramente — diferentes tarifas

Permitir futuramente:

* diferentes tarifas;
* distribuidoras;
* horários;
* tarifa branca;
* períodos diferentes;
* impostos e componentes configuráveis.

Não criar valores fictícios como se fossem tarifas oficiais.

---

# 27. 🔌 Futuramente — medidor real

Arquitetura futura para integrar dados de:

* smart plugs;
* medidores inteligentes;
* IoT.

Exemplo:

```text
Consumo estimado
       ↓
Consumo medido
       ↓
Comparação
```

Mostrar:

> Estimado: 42 kWh
> Medido: 47 kWh

E explicar possíveis diferenças.

---

# 28. 📚 Base educativa

Criar uma seção:

## "Aprenda"

Conteúdos curtos:

* O que é Watt?
* O que é kWh?
* O que é potência?
* O que é consumo?
* Como funciona uma conta de luz?
* O que significa eficiência energética?
* Como economizar energia?
* Por que aparelhos diferentes consomem quantidades diferentes de energia?

Os textos devem ser curtos, didáticos e adequados para estudantes.

---

# 29. 🧪 Testes

Criar testes para as principais fórmulas.

Exemplo:

```python
def test_energy_consumption():
    result = calculate_consumption(
        power=1000,
        hours_per_day=2,
        days_per_month=30
    )

    assert result == 60
```

Testar também:

* potência zero;
* valores negativos;
* horas inválidas;
* tarifa zero;
* arredondamentos;
* consumo mensal;
* consumo anual.

---

# 30. ⚠️ Validações

Nunca permitir silenciosamente:

```text
potência < 0
horas < 0
dias < 0
tarifa < 0
```

Exibir mensagens amigáveis.

Exemplo:

> ⚠️ Informe uma potência maior que zero.

---

# 31. 🎨 UX

O usuário deve conseguir realizar uma simulação sem precisar entender programação.

Utilizar:

* sliders quando fizer sentido;
* inputs numéricos;
* selects;
* cards;
* tooltips;
* explicações;
* resultados destacados.

Evitar telas excessivamente carregadas.

Cada página deve responder claramente:

> "O que eu preciso informar?"

e depois:

> "O que esse resultado significa?"

---

# 32. 📱 Responsividade

Priorizar uma boa experiência em:

* notebook;
* computador;
* tablet;
* navegador de celular.

O aplicativo será apresentado na escola, portanto a experiência em tela grande deve ser excelente.

---

# 33. 🎤 Modo apresentação

Criar futuramente um:

## "Modo apresentação"

Uma interface simplificada para demonstrar o projeto na escola.

Exemplo:

```text
⚡ ECOWATT

Quanto custa deixar
esse aparelho ligado?

[ CHUVEIRO ]

5.500 W

30 min/dia

↓

⚡ 82,5 kWh/mês

💰 R$ 78,38/mês
```

A ideia é permitir que o estudante demonstre o conceito em poucos segundos.

---

# 34. 📊 Página "Meu impacto"

Futuramente:

```text
🌱 Meu impacto

⚡ Energia economizada
248 kWh

💰 Dinheiro economizado
R$ 235

📅 Período
6 meses

🔥 Sequência
18 dias
```

---

# 35. 🧩 Requisitos de código

O código deve:

* ser limpo;
* ser legível;
* possuir nomes de variáveis claros;
* possuir funções pequenas;
* utilizar type hints;
* evitar duplicação;
* possuir comentários apenas quando agregarem valor;
* separar regras de negócio da interface;
* possuir testes das regras principais.

Não adicionar dependências sem necessidade.

---

# 36. 📖 README

Criar README contendo:

1. O que é o EcoWatt
2. Objetivo educacional
3. Funcionalidades do MVP
4. Como executar
5. Estrutura do projeto
6. Fórmulas utilizadas
7. Exemplos
8. Tecnologias
9. Roadmap
10. Ideias futuras
11. Como contribuir

O README também deve explicar os conceitos de:

```text
W
kW
kWh
R$/kWh
```

de maneira didática.

---

# 37. 🚨 Regra importante sobre dados

Não inventar informações apresentadas como oficiais.

Quando forem necessários dados de:

* tarifas;
* consumo de aparelhos;
* eficiência;
* fatores ambientais;
* especificações de hardware;

usar dados explicitamente identificados como:

```text
Exemplo
Estimativa
Valor informado pelo usuário
Fonte oficial
```

O aplicativo deve deixar claro quando um cálculo é uma estimativa.

---

# 38. 🗺️ Roadmap

Organizar o desenvolvimento:

## MVP — versão escolar

* [x] Dashboard
* [x] Calculadora
* [x] Cálculo de custo
* [x] Gráficos
* [x] Eficiência energética
* [x] Comparador
* [x] Simulador da casa
* [x] PC Energy Builder
* [x] Conteúdo educativo

## V2

* [ ] Economia anual
* [ ] Simulador "E se?"
* [ ] Histórico
* [ ] Mais aparelhos
* [ ] Mais componentes de PC

## V3

* [ ] Desafios
* [ ] Ranking
* [ ] Perfil da residência
* [ ] Gamificação

## V4

* [ ] Conta de usuário
* [ ] Banco de dados
* [ ] Histórico online
* [ ] Aplicativo mobile

## V5

* [ ] OCR de etiquetas
* [ ] Assistente EcoWatt
* [ ] Integração com smart plugs
* [ ] Consumo real vs. estimado
* [ ] Impacto ambiental

---

# 39. 🎯 Regra principal para o Copilot

Não implemente todas as funcionalidades futuras agora.

O objetivo inicial é entregar um **MVP excelente, bonito, funcional e apresentável na escola**.

Porém, desenvolva o código de forma que as futuras funcionalidades possam ser adicionadas sem precisar reescrever completamente o projeto.

Prioridade:

```text
1. Experiência do usuário
2. Correção dos cálculos
3. Visualização
4. Clareza educativa
5. Código simples
6. Arquitetura extensível
```

Sempre que houver conflito entre "arquitetura sofisticada" e "código simples e didático", prefira a solução simples.

---

# 40. 🚀 Primeira tarefa do Copilot

Antes de escrever código:

1. Analise este documento.
2. Proponha a estrutura final do projeto.
3. Explique brevemente as decisões arquiteturais.
4. Identifique possíveis riscos.
5. Crie o roadmap de implementação do MVP.
6. Aguarde a confirmação antes de implementar tudo de uma vez.

Após a aprovação:

### Sprint 1

Criar:

* estrutura do projeto;
* dashboard;
* identidade visual;
* calculadora;
* motor de cálculo;
* testes;
* README inicial.

### Sprint 2

Criar:

* gráficos;
* comparador;
* eficiência energética;
* simulador da casa.

### Sprint 3

Criar:

* PC Energy Builder;
* conteúdo educativo;
* refinamento visual;
* validações;
* testes;
* preparação para apresentação.

### Sprint 4

Realizar:

* revisão de UX;
* revisão de código;
* correção de bugs;
* melhoria dos textos;
* preparação do modo apresentação;
* documentação final.

---

# 41. Resultado esperado

Ao final do MVP, o usuário deverá abrir o EcoWatt e imediatamente entender:

> **"Este aplicativo me ajuda a descobrir quanto de energia eu consumo, quanto isso custa e como posso economizar."**

O aplicativo deve ser suficientemente bonito para ser apresentado como um **produto real**, suficientemente simples para ser explicado por um estudante de 14 anos e suficientemente bem estruturado para evoluir futuramente.
