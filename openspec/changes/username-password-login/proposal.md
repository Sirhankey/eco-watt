## Why

A identificação atual depende de dados mantidos no estado do navegador e não fornece uma identidade de usuário persistente para vincular tentativas do quiz e demais dados entre recargas e dispositivos. Um login simples por nome de usuário único e senha permite retomar a sessão e relacionar os registros a um identificador estável, sem exigir e-mail.

## What Changes

- Introduzir cadastro e login por nome de usuário único e senha, sem e-mail.
- Manter uma sessão autenticada entre recargas e navegação por abas, com opção de sair.
- Associar os dados e eventos da aplicação a um ID interno estável do usuário, mantendo a sessão de visita como conceito separado.
- Adicionar reset administrativo de senha por script, usando o nome de usuário e uma senha temporária definida pela equipe; não haverá recuperação automática por e-mail.
- Permitir encerrar/remover os dados de conta após a apresentação, conforme procedimento operacional documentado.
- Migrar a identificação atual para o novo fluxo sem expor credenciais ou identidade em parâmetros de URL.

## Capabilities

### New Capabilities
- `participant-authentication`: Cadastro e login de participantes sem e-mail, sessão autenticada persistente, identidade estável para associação de dados e reset administrativo de senha.

### Modified Capabilities

## Impact

- Fluxo de identificação em `ecowatt/utils/session.py` e inicialização compartilhada pelas páginas Streamlit.
- Persistência Supabase: novas tabelas para contas/sessões e referências por usuário em tentativas de quiz, eventos e outros dados aplicáveis, com políticas de acesso correspondentes.
- Serviços de autenticação e repositórios, script administrativo de reset e configuração de segredos exclusivamente no servidor.
- Remoção gradual da identidade atual derivada de nome/turma e de sua cópia em query parameters.
- Testes de cadastro, unicidade concorrente, autenticação, persistência de sessão, reset e associação de registros.