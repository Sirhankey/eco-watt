## Why

O EcoWatt já demonstra cálculos de energia, mas as áreas de maior interesse para jovens ainda podem ser mais participativas e memoráveis. Precisamos modernizar o PC Builder, criar uma atividade curta com recompensa simbólica e permitir que participantes salvem suas próprias simulações sem transformar dados pessoais em catálogo oficial sem revisão.

## What Changes

- Modernizar o PC Builder com montagem mais visual, feedback imediato, comparação de configurações e interação adequada para apresentações.
- Criar um quiz/jogo educativo com pontuação, resultado final e premiação simbólica configurável para o evento.
- Criar catálogo de itens do usuário separado do catálogo oficial, com autoria, status, timestamps em UTC e exibição em `America/Sao_Paulo`.
- Validar duplicidade antes de inserir aparelhos, componentes ou sugestões de catálogo, considerando identificador e combinação normalizada de campos relevantes.
- Permitir salvar presets pessoais da página “Minha Casa”, mantendo presets oficiais controlados pela equipe.
- Exibir avaliações comparativas das casas salvas, como menor e maior consumo, sem expor dados pessoais além do necessário.
- Manter fatos, presets oficiais, aparelhos oficiais e componentes de PC publicados sob controle da equipe; contribuições públicas passam por aprovação.

## Capabilities

### New Capabilities

- `user-catalog-and-moderation`: Itens privados do usuário, sugestões para catálogo público, autoria, deduplicação, moderação e governança dos dados.
- `pc-builder-experience`: Experiência visual e interativa para montar, comparar e entender o consumo de configurações de PC.
- `event-quiz-and-rewards`: Quiz educativo com perguntas controladas, pontuação, encerramento e reconhecimento simbólico no evento.
- `personal-home-presets`: Salvamento de cenários residenciais pessoais, histórico básico e comparação de consumo entre casas autorizadas.
- `home-simulator-persistence`: Integração de itens pessoais e presets salvos ao simulador residencial, preservando os cenários oficiais.

### Modified Capabilities
*(Nenhuma - os contratos existentes ainda não foram promovidos para `openspec/specs/`.)*

## Impact

- Novas tabelas persistentes para itens oficiais, itens do usuário, sugestões, presets pessoais, respostas do quiz e resultados do evento.
- Alterações nas páginas `Minha Casa` e `PC Builder`, nos serviços de catálogo/preset e no gerenciamento de sessão.
- Necessidade de política de acesso e moderação no Supabase, além de índices para detectar duplicidades.
- O motor de cálculo existente deve continuar puro e compatível com modelos carregados do banco ou dos JSONs durante a migração.
- Será necessário definir retenção e visibilidade de nome do participante, especialmente por o uso ocorrer em contexto escolar.