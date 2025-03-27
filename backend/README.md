# 💼 Backend - Gerenciamento de Planos com Flask + MySQL

Este projeto é uma API RESTful construída com **Flask** que permite o gerenciamento de usuários, planos e autenticação baseada em **JWT**, incluindo permissões especiais para super administradores (ADM).

---

## 🔰 Sobre o Projeto

- Cadastro de usuários com validações de email, telefone e senha
- Associação de usuários a planos
- Geração e armazenamento de tokens JWT
- Rotas protegidas por autenticação
- Permissões exclusivas para usuários com `cargo = ADM` (superadmin)
- Suporte a testes automatizados com **pytest**

---

## 🚀 Tecnologias Utilizadas

- ✅ Python 3.11+
- ✅ Flask
- ✅ MySQL (ou MariaDB)
- ✅ bcrypt (para senhas)
- ✅ PyJWT (tokens JWT)
- ✅ dotenv (variáveis de ambiente)
- ✅ pytest (testes automatizados)

---

## 🏗️ Estrutura do Projeto

backend/ 
    ├── app.py 
    ├── .env 
    ├── requirements.txt 
    ├── routes/ 
    │   ├──auth_routes.py 
    │   └── plans_routes.py 
    ├── middlewares/ 
    │   └── auth.py 
    ├──utils/ 
    │   ├── db.py 
    │   ├── validators.py 
    │   └── token.py 
    └── tests/ 
        └──test_routes.py

## ⚙️ Como Rodar Localmente

### 1. Clone o repositório: git clone
https://github.com/seu-usuario/seu-repo.git cd backend

### 2. Crie e ative o ambiente virtual: python -m venv venv source
venv/bin/activate (ou venv\\Scripts\\activate no Windows)

### 3. Instale as dependências: pip install -r requirements.txt

### 4. Crie o arquivo .env com:

DB_HOST=localhost 
DB_USER=root 
DB_PASSWORD=sua_senha
DB_NAME=sua_aplicacao 

JWT_SECRET=segredo_super_secreto
JWT_ALGORITHM=HS256 
JWT_EXPIRES=36000

### 5. Inicie o servidor: python app.py

### API disponível em: http://localhost:5000

## ⚙️ TESTES

TESTES MANUAIS (via Postman ou Insomnia): 

- POST /register → Cadastro de usuário 
- POST /api/generate-token → Geração de token JWT 
- GET  /api/plans → Listagem de planos 
- GET /api/user-plans → Plano do usuário autenticado 
- GET /api/superadmin/test → Acesso exclusivo ADM

TESTES AUTOMATIZADOS (com pytest):

- pytest tests/

### 📬 Endpoints Principais

| Método | Rota                   | Protegida?   | Descrição                              |
|--------|------------------------|--------------|----------------------------------------|
| POST   | /register              | ❌ Não        | Cadastro de usuário                    |
| POST   | /api/generate-token    | ❌ Não        | Gera token JWT                         |
| GET    | /api/plans             | ❌ Não        | Lista de planos disponíveis            |
| GET    | /api/user-plans        | ✅ Sim        | Plano do usuário logado                |
| GET    | /api/superadmin/test   | ✅ Sim (ADM)  | Rota exclusiva para Super Admins       |

---

### 🔐 Autenticação JWT

- O token JWT deve ser enviado no header:
- Authorization: Bearer SEU_TOKEN

- O token contém os campos: `user_id`, `cargo`, `exp` (expiração)

---

### 🧠 Boas Práticas Aplicadas

- Rotas organizadas em **Blueprints**
- Separação de responsabilidades (rotas, utilitários, middlewares)
- Proteção via decorators: `@token_required` e `@only_super_admin`
- Senhas criptografadas com `bcrypt`
- Testes automatizados com `pytest`

---

### 👤 Autor

- Desenvolvido por **Gustavo Marques**
- Contato: [gustavomarquesmn@gmail.com](mailto:gustavomarquesmn@gmail.com)
