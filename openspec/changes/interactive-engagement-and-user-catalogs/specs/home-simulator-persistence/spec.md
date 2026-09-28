## ADDED Requirements

### Requirement: Catálogos persistentes com fallback
O simulador SHALL carregar catálogos persistidos quando o backend estiver configurado e SHALL continuar funcionando com os JSONs locais quando o backend estiver indisponível.

#### Scenario: Backend disponível
- **WHEN** o Supabase está configurado e retorna o catálogo válido
- **THEN** o simulador utiliza os registros oficiais publicados e os itens privados do usuário

#### Scenario: Backend indisponível
- **WHEN** a consulta ao backend falha durante uma apresentação
- **THEN** o simulador mantém os cálculos locais e informa que a persistência não foi concluída

### Requirement: Itens duplicados no simulador
O simulador SHALL validar duplicidade antes de adicionar aparelhos ou salvar presets pessoais.

#### Scenario: Aparelho já existente no inventário
- **WHEN** o usuário tenta adicionar novamente o mesmo item identificado no inventário atual
- **THEN** o sistema bloqueia a operação ou solicita confirmação explícita para uma segunda unidade

### Requirement: Preservação dos presets oficiais
Presets oficiais SHALL ser somente leitura para participantes e SHALL manter seus identificadores e dados durante a migração dos JSONs.

#### Scenario: Tentativa de editar preset oficial
- **WHEN** um participante tenta salvar alterações sobre um preset oficial
- **THEN** o sistema cria uma cópia pessoal e não altera o registro oficial