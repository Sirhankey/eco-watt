## 1. Modelo de dados e segurança

- [x] 1.1 Definir migrations Supabase para catálogos oficiais, itens pessoais, submissões, presets pessoais, quizzes, tentativas e resultados.
- [x] 1.2 Adicionar `timestamptz`, autoria, status, consentimento e índices de escopo em todas as tabelas aplicáveis.
- [x] 1.3 Criar políticas RLS para leitura pública de itens publicados, acesso privado do autor e operações administrativas de moderação.
- [x] 1.4 Criar restrições/índices de unicidade para impedir duplicidades concorrentes por escopo.
- [x] 1.5 Documentar retenção, visibilidade de nomes e decisão sobre conta administrativa do evento.

## 2. Camada de catálogo e migração

- [x] 2.1 Implementar modelos e validadores para aparelhos, componentes, facts, presets e submissões.
- [x] 2.2 Implementar normalização de nomes e validação de limites numéricos, texto e conteúdo inseguro.
- [x] 2.3 Implementar repositórios/loaders que leiam o Supabase quando configurado e usem os JSONs como fallback.
- [x] 2.4 Criar script idempotente de importação dos quatro JSONs, preservando IDs e marcando registros como oficiais.
- [x] 2.5 Implementar criação de item pessoal e envio opcional para moderação, com mensagens de duplicidade compreensíveis.
- [x] 2.6 Implementar aprovação, rejeição, arquivamento e auditoria de submissões por moderador.
- [x] 2.7 Adicionar testes unitários para normalização, validação, deduplicação e fallback offline.

## 3. Presets pessoais e simulador residencial

- [x] 3.1 Implementar serviço para salvar snapshot do inventário, tarifa, kWh mensal e metadados do preset pessoal.
- [x] 3.2 Integrar carregamento de presets pessoais à sessão sem alterar presets oficiais.
- [x] 3.3 Adicionar controles de nome, visibilidade e consentimento de comparação na página “Minha Casa”.
- [x] 3.4 Implementar confirmação para segunda unidade de um aparelho equivalente e bloquear duplicatas acidentais.
- [x] 3.5 Implementar consulta de menor/maior consumo por evento com rótulo pseudônimo e filtros de autorização.
- [x] 3.6 Adicionar testes para snapshots, privacidade, aplicação de cópia pessoal e ranking vazio/empatado.

## 4. PC Builder interativo

- [x] 4.1 Refatorar a página para fluxo guiado de componentes, perfil de uso e resultado, preservando a acessibilidade dos controles.
- [x] 4.2 Criar resumo persistente da configuração e feedback visual de potência, kWh e custo ao alterar entradas.
- [x] 4.3 Integrar componentes pessoais do usuário e componentes oficiais publicados sem duplicar lógica de cálculo.
- [x] 4.4 Implementar comparação de dois setups com deltas absolutos e indicação didática do impacto.
- [x] 4.5 Adicionar estados de carregamento, erro, catálogo vazio e fallback para uso offline.
- [x] 4.6 Cobrir o fluxo com testes dos serviços e uma verificação manual/responsiva da interface.

## 5. Quiz e premiação simbólica

- [x] 5.1 Criar modelo e serviço para quizzes, perguntas aprovadas, alternativas, explicações e configuração do evento.
- [x] 5.2 Implementar uma tentativa por quiz e sessão, com respostas, pontuação e timestamps persistidos.
- [x] 5.3 Criar interface de quiz com ordem embaralhada, progresso, resultado e explicações pós-resposta.
- [x] 5.4 Gerar código de participação quando a premiação simbólica estiver habilitada, sem promessa de benefício material.
- [x] 5.5 Implementar exportação administrativa de resultados minimizados e opção de não expor ranking nominal.
- [x] 5.6 Adicionar testes para pontuação, repetição, quiz desabilitado, perguntas inválidas e falha de persistência.

## 6. Observabilidade e documentação

- [x] 6.1 Registrar eventos de criação, duplicidade, submissão, aprovação, preset salvo, quiz concluído e fallback sem dados sensíveis desnecessários.
- [x] 6.2 Atualizar documentação com configuração do Supabase, timezone, RLS, migração e operação do evento.
- [x] 6.3 Executar a suíte de testes, validação do schema e um ensaio offline da apresentação.
- [x] 6.4 Ativar funcionalidades por configuração/feature flag e documentar o plano de rollback para o evento.