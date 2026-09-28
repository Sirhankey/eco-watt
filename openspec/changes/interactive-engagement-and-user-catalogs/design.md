## Context

O EcoWatt hoje carrega `appliances.json`, `pc_components.json`, `facts.json` e `presets.json` localmente. O simulador residencial mantém aparelhos em `st.session_state`, enquanto o PC Builder transforma o catálogo inteiro em seletores e passa os componentes aos serviços puros de cálculo. O projeto já possui identificação de participante e persistência opcional de analytics no Supabase.

Esta change reúne persistência de conteúdo, contribuição de usuários, uma experiência mais atraente para jovens e uma atividade de encerramento do evento. O contexto escolar exige cuidado com exposição de nomes, moderação e resultados que possam ser interpretados como competição oficial.

## Goals / Non-Goals

**Goals:**

- Separar catálogo oficial, itens privados do usuário e sugestões públicas pendentes.
- Garantir autoria, auditoria e timestamps como instantes UTC, exibidos em `America/Sao_Paulo`.
- Bloquear duplicidades antes do insert e também proteger contra concorrência no banco.
- Modernizar a interação do PC Builder sem mover fórmulas para a UI.
- Oferecer quiz curto, educativo, auditável e com premiação simbólica.
- Permitir salvar, reutilizar e comparar presets residenciais com controles de privacidade.

**Non-Goals:**

- Não permitir edição pública direta de facts, presets oficiais ou componentes publicados.
- Não criar ranking público nominal por padrão.
- Não transformar a pontuação do quiz em prêmio financeiro, crédito ou benefício permanente.
- Não substituir o cálculo energético existente por estimativas de terceiros ou lógica no frontend.
- Não migrar todo o histórico de analytics para as novas tabelas nesta etapa.

## Decisions

### 1. Três níveis de conteúdo

Usar catálogo oficial (`published`/`archived`), conteúdo pessoal privado e submissão para moderação (`pending`/`approved`/`rejected`). Itens pessoais podem ser usados nos cálculos do próprio usuário, mas só itens publicados aparecem no catálogo global. Isso é preferível a um único campo `is_public`, porque preserva revisão, histórico e motivo de rejeição.

### 2. Modelo persistente separado por domínio

Criar tabelas para aparelhos, componentes de PC, facts, presets e itens de preset; tabelas de usuário para aparelhos pessoais e presets pessoais; e uma fila de submissões com `kind`, `payload`, `submitted_by`, `status` e decisão de moderador. Presets pessoais referenciam snapshots dos valores usados, evitando que uma futura alteração do catálogo mude silenciosamente uma simulação salva.

### 3. Identidade e tempo

Usar `user_id` pseudônimo/UUID como chave de autoria e guardar `created_by_name` apenas como snapshot administrativo. Colunas temporais serão `timestamptz` com `default now()` no Supabase. A aplicação converte para `ZoneInfo("America/Sao_Paulo")` apenas na apresentação.

### 4. Deduplicação em duas camadas

Normalizar texto para comparação (trim, casefold, espaços e pontuação irrelevante) e verificar duplicidade na aplicação para feedback imediato. Criar índices ou restrições únicas adequadas no banco para impedir duplicatas concorrentes. Para aparelhos e componentes, a chave de comparação combinará proprietário/escopo, nome normalizado, categoria e os campos de potência; para facts e presets, nome/título normalizado dentro do escopo.

### 5. PC Builder como fluxo guiado

Organizar a montagem em etapas visuais (componentes, perfil de uso, resultado), exibir resumo persistente da configuração, consumo e custo em tempo real, permitir comparar dois setups e usar feedback visual de impacto. A UI chamará `calculate_pc_energy` e permanecerá sem regras matemáticas próprias. Componentes pessoais só entram nos seletores do proprietário até aprovação.

### 6. Quiz controlado pelo evento

Perguntas e respostas corretas serão conteúdo administrado, não contribuição livre. Cada sessão terá uma tentativa por quiz, respostas e pontuação persistidas com timestamp; o resultado exibirá acertos, explicações e um identificador/código de participação. O organizador poderá habilitar um modo de premiação simbólica e exportar resultados, sem ranking nominal obrigatório.

### 7. Presets pessoais e comparação responsável

Salvar uma cópia do inventário, tarifa e metadados da simulação em um preset pessoal. A comparação de “mais econômica” e “maior consumo” usará kWh mensal calculado, poderá filtrar por evento/período e exibirá nomes pseudônimos ou rótulos fornecidos pelo usuário apenas com consentimento. Presets oficiais continuam somente leitura.

## Risks / Trade-offs

- [Dados escolares identificáveis] → Minimizar nome exibido, usar `user_id` pseudônimo no ranking e oferecer consentimento explícito para compartilhamento.
- [Usuário cria conteúdo inadequado] → Validar campos, limitar tamanho, bloquear HTML/script, manter item privado e exigir moderação para publicação.
- [Duplicata criada por duas requisições simultâneas] → Aplicar restrição/índice único no banco além da checagem na aplicação.
- [Ranking incentiva comparação indevida] → Tornar comparação opt-in, usar linguagem didática e não exibir ranking nominal por padrão.
- [Falha ou indisponibilidade do Supabase durante apresentação] → Manter fallback local/session state para cálculos e sinalizar claramente quando o salvamento não ocorreu.
- [Migração altera resultados salvos] → Armazenar snapshots dos valores no preset e manter os JSONs como fallback durante a transição.
- [Quiz vazado ou respondido repetidamente] → Uma tentativa por sessão/quiz, janela de evento e perguntas embaralhadas a partir de conjunto aprovado.

## Migration Plan

1. Criar tabelas, índices, políticas de acesso e funções de normalização no Supabase sem remover os JSONs.
2. Importar os quatro catálogos atuais como registros oficiais com `source = migration` e preservar os IDs existentes.
3. Alterar os loaders para preferir o banco quando configurado e cair para JSON quando não estiver configurado.
4. Liberar primeiro itens pessoais e presets pessoais; depois habilitar submissões para moderação.
5. Ativar a nova interface do PC Builder e o quiz por configuração de evento.
6. Monitorar erros de duplicidade, falhas de persistência e uso do fallback antes de aposentar os JSONs como fonte primária.

Rollback: desabilitar as flags de banco, quiz e UI nova; os loaders retornam aos JSONs e cálculos existentes. Nenhum dado salvo novo precisa ser apagado para realizar rollback.

## Open Questions

- O organizador do evento terá uma conta/admin autenticada ou a moderação será feita por um usuário técnico fixo?
- O quiz terá um único conjunto de perguntas ou conjuntos diferentes por turma/sessão?
- O ranking entre casas será apenas durante o evento ou ficará disponível depois?
- Qual é o prazo de retenção para nomes, respostas do quiz e presets pessoais?