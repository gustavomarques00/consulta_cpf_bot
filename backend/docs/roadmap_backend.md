# 📋 Roadmap Técnico - Backend do SaaS (BRSMM)

## ✅ Concluído
- [x] Autenticação com JWT (access + refresh)
- [x] Middleware de proteção de rotas
- [x] Rotas para planos e superadmin
- [x] Integração com API da BRSMM
- [x] Serviço `BrsmmService` centralizado
- [x] Envio de tráfego com registro de pedidos
- [x] Agendamento de envio diário (`send_daily_brsmm.py`)
- [x] Logs automáticos por execução
- [x] Histórico de envios via API
- [x] Exportação de envios para CSV
- [x] Swagger documentando todas as rotas
- [x] Testes automatizados com pytest (100% cobrindo tráfego, auth, tokens)
- [x] Ajustes nas rotas de tráfego para garantir que pedidos sejam validados corretamente
- [x] Correção na lógica de retorno para pedidos não encontrados
- [x] Atualização nos testes para validar comportamento correto de múltiplos pedidos
- [x] Alterações nas mensagens de erro para refletir a falta de pedidos em múltiplos IDs

---

## 🚧 Em Andamento
- [ ] Painel do cliente: listagem de pedidos enviados
- [ ] Filtrar histórico por status, data e link
- [ ] Endpoint para status de pedido por ID
- [ ] Filtro com múltiplos pedidos da BRSMM (batch status)
- [ ] Adição do ID do usuário no log do pedido

---

## 🛠️ A Fazer
- [ ] Sistema de precificação com margem de lucro sobre a BRSMM
- [ ] Rota pública para listar serviços disponíveis + preço final
- [ ] Controle de saldo do cliente (créditos)
- [ ] Geração de fatura mensal (PDF ou JSON)
- [ ] Painel administrativo com CRUD de usuários
- [ ] Cadastro de clientes com cargos definidos
- [ ] Implementar limites de pedidos por cliente (por plano)
- [ ] Logs de erros com notificação automática (e-mail, Telegram)
- [ ] Webhook para atualizar status dos pedidos em tempo real (opcional)

---

## 💡 Sugestões Futuras
- [ ] Painel Web completo (Next.js/React)
- [ ] Dashboard de tráfego e estatísticas por cliente
- [ ] API pública com chave por cliente
- [ ] Multi-admin e times (equipes)
- [ ] Plugin de revenda (white-label)

---

## 📦 Diretórios Relevantes
- `backend/services/brsmm_service.py` → Integração com API
- `backend/scripts/send_daily_brsmm.py` → Script automático
- `backend/routes/trafego_routes.py` → Rota principal de tráfego
- `backend/logs/brsmm/` → Logs dos envios realizados
- `tests/trafego/` → Testes da feature
