📘 Documentação Técnica - Frontend do Sistema

Este é o frontend do sistema de extração e gerenciamento de dados de usuários, integrado à API backend. A interface é responsável pela visualização e interação com dados extraídos, planos e permissões.

🔰 Sobre o Projeto

Interface para operadores e administradores

Consulta de status de extrações

Visualização de dados por CPF

Painel de controle para usuários e planos (em construção)

Comunicação com o backend via API REST

🚀 Tecnologias Utilizadas

HTML5 / CSS3 / JavaScript

React.js ou Next.js (dependendo do setup atual)

Axios (requisições HTTP)

Bootstrap ou Tailwind CSS (opcional para UI)

dotenv (variáveis de ambiente)

npm / yarn (gerenciador de pacotes)

📁 Estrutura Sugerida

frontend/

public/ → Arquivos estáticos

src/

components/ → Componentes reutilizáveis

pages/ → Páginas e rotas da aplicação

services/ → Integração com a API

styles/ → CSS ou Tailwind

utils/ → Helpers e validações

.env.local → Configurações do ambiente local

⚙️ Como Rodar Localmente

Acesse a pasta do frontend:

cd frontend

Instale as dependências:

npm install
ou
yarn install

Configure o ambiente no arquivo .env.local:

API_URL=http://localhost:5000
NODE_ENV=development

Execute a aplicação:

npm run dev
ou
yarn dev

A aplicação estará disponível em: http://localhost:3000

🔐 Autenticação

O frontend utiliza tokens JWT fornecidos pelo backend para autenticação. Os tokens devem ser armazenados com segurança (ex: localStorage, context, cookies com HttpOnly).

Authorization: Bearer TOKEN

É possível proteger rotas usando React Router ou middleware no Next.js

📬 Integração com Backend

Todos os endpoints da API estão disponíveis via configuração API_URL no .env.local

Utiliza axios como client HTTP

As chamadas para login, refresh token, listagem de planos e extrações seguem os mesmos endpoints definidos no backend

📦 Scripts Disponíveis

npm run dev → Inicia o servidor de desenvolvimento
npm run build → Gera a versão de produção
npm run start → Inicia a versão buildada
npm run lint → (opcional) Valida padrões de código

🧠 Boas Práticas Aplicadas

Organização modular por página e componente

Requisições centralizadas em services

Autenticação persistente por token JWT

Variáveis de ambiente isoladas por ambiente

Componentes reutilizáveis com props claras

Estrutura preparada para crescimento e manutenção

👤 Autor

Desenvolvido por Gustavo Marques
Contato: 