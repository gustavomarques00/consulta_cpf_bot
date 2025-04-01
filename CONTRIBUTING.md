# 🤝 Contribuindo para o Projeto

Obrigado por contribuir! Este projeto segue um fluxo de desenvolvimento padronizado para facilitar manutenção, qualidade e colaboração.

---

## 🔁 Fluxo de Branches

| Tipo     | Nome                                   |
|----------|----------------------------------------|
| Produção | `main`                                 |
| Dev      | `develop`                              |
| Feature  | `feature/nome-da-funcionalidade`       |
| Correção | `hotfix/descricao-do-problema`         |

---

## 🧩 Commits semânticos

Siga este padrão para manter o histórico legível:

```
tipo: descrição breve

Exemplos:
feat: adiciona filtro por CPF
fix: corrige bug de autenticação JWT
refactor: simplifica função de extração
docs: atualiza README com novos endpoints
test: adiciona cobertura de teste para planos
```

---

## 🧪 Testes e Validação

Antes de qualquer `commit`, são executadas automaticamente:

- ✅ `pytest` (testes unitários e integrados)
- ✅ `black --check` (formatação)

❌ Se algum passo falhar, o commit é bloqueado.

---

## 🚀 Regras para criar Pull Requests

- Sempre crie PRs da sua branch para `develop`
- Inclua descrição clara e link para a tarefa (se houver)
- Confirme que o PR:
  - [x] Passa nos testes
  - [x] Está formatado com black
  - [x] Atualiza a documentação, se necessário

---

## 🏷️ Versionamento

Este projeto usa **semver** (https://semver.org):

- `MAJOR`: Mudanças incompatíveis na API
- `MINOR`: Novas funcionalidades compatíveis
- `PATCH`: Correções de bugs

Tags de release são criadas no formato: `v1.0.0`, `v1.1.0`, `v1.1.1`...

---

## 🧠 Ajuda

Se tiver dúvidas, abra uma issue ou envie uma pergunta para o mantenedor.

---

Obrigado por contribuir! 🚀
