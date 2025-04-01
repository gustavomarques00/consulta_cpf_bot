# 📦 Changelog

Todas as alterações importantes deste projeto serão listadas aqui.

---

## [v1.0.0] - 2024-04-01

### ✨ Features

- Adicionado controle de autenticação JWT com access/refresh tokens
- Integração com Google Sheets via gspread
- Processamento de CPFs com controle de extração
- Middleware para proteção de rotas por cargo (Operador, ADM)
- Execução automática noturna via `start_madrugada.bat`

### 🛠 Refatorações

- Reorganização completa da estrutura do projeto por domínio
- Separação de responsabilidades: routes, services, middlewares, utils
- Modularização de `request_tracker` e `processador_cpfs`

### 🧪 Testes

- Adicionados testes unitários e de integração com Pytest
- Testes para geração, renovação e revogação de tokens
- Testes para verificação de CPFs e interação com Google Sheets

### 📚 Documentação

- Criado `README.md` técnico em `backend/docs/`
- Adicionado `CONTRIBUTING.md` com guia de contribuição
- Criado guia de branching em `docs/git-flow.txt`
- Estrutura do projeto documentada com requisitos e instruções

### 📦 Dependências

- Adicionado `requirements.txt` com categorização por grupo
- Incluído suporte a `black`, `pre-commit`, `pytest`, `flasgger`

---

## 🔜 Em planejamento

- Painel administrativo web para visualização dos dados
- Exportação automática dos resultados
- Suporte a múltiplos usuários e permissões avançadas
- Integração com webhooks externos

---

🔖 Versão atual: **v1.0.0**
