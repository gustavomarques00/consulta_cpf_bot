# 📘 Documentação Técnica – Backend do Sistema

Este é o backend do sistema de extração e gerenciamento de dados, responsável por fornecer APIs seguras para autenticação, gerenciamento de planos e processamento de CPFs.

---

## 🔰 Sobre o Projeto

- API RESTful com autenticação JWT
- Controle de planos por usuário
- Integração com Google Sheets
- Extração de dados via API externa
- Processamento e rastreamento de requisições diárias
- Proteção por nível de acesso (usuário comum, operador, ADM)
- Executável automaticamente por script (modo madrugada)

---

## 🚀 Tecnologias Utilizadas

- Python 3.12+
- Flask
- PyJWT
- gspread
- MySQL
- python-dotenv
- Flasgger
- Pytest
- Black
- Pre-commit Hook

---

## 📁 Estrutura do Projeto

```
backend/
├── core/
├── routes/
├── services/
├── utils/
├── middlewares/
├── scripts/
├── docs/
├── main.py
├── start_extraction.py
└── requirements.txt
```

---

## 🧪 Testes Automatizados

- Usando pytest
- Cobrem rotas, autenticação, tokens, extração, requisições e planilhas

```bash
pytest
```

---

## 🧼 Pre-Commit Hook

Validações automáticas antes de cada commit:

- ✅ Testes automatizados
- ✅ Validação de formatação com black

---

## ⚙️ Como Rodar o Projeto

1. Acesse a pasta backend  
2. Crie e ative o ambiente virtual:

```
python -m venv venv
call venv\Scripts\activate
```

3. Instale as dependências:

```
pip install -r requirements.txt
```

4. Configure o .env  
5. Execute o app:

```
python main.py
```

---

## 🔐 Autenticação

- Tokens JWT com access_token e refresh_token
- Tokens armazenados e controlados via banco
- Revogação de tokens e controle de blacklist
- Middlewares:
  - @token_required
  - @only_super_admin

---

## 🗓️ Execução Programada

- Script start_madrugada.bat roda a extração noturna
- Logs em logs/
- Controle de requisições em logs/requests/

---

## 📚 Documentação da API

Acesse:

```
http://localhost:5000/apidocs
```

---

## 👨‍💻 Autor

Desenvolvido por Gustavo Marques  
Email: gustavomarquesmm@gmail.com  
GitHub: [https://github.com/gustavomarques00](https://github.com/gustavomarques00)
