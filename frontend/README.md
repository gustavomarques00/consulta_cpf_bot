# Sistema de Autenticação - Frontend

Este é o frontend de um sistema de autenticação completo com funcionalidade de login, registro, e painel de controle. Ele permite o gerenciamento de dados de usuários, como CPFs, e fornece visualizações em forma de tabelas com exportação para o Google Sheets.

## Funcionalidades

- **Login e Registro**: Permite que os usuários façam login e se registrem no sistema.
- **Painel de Controle**: Dashboard com informações sobre usuários e CPFs.
- **Busca e Exibição de CPFs**: Os usuários podem buscar dados de CPFs e exibir os resultados em tabelas.
- **Exportação para o Google Sheets**: Permite exportar os dados buscados diretamente para o Google Sheets.

## Tecnologias Utilizadas

- **Next.js 15.2.2**: Framework React para renderização do lado do servidor e criação de páginas.
- **React**: Biblioteca JavaScript para construção da interface de usuário.
- **Tailwind CSS**: Framework de CSS para estilização rápida e responsiva.
- **React Hook Form**: Biblioteca para controle e validação de formulários.
- **Axios**: Biblioteca para fazer requisições HTTP para o backend.
- **Next Font**: Para otimização de fontes com Next.js.

## Como Rodar o Projeto

### 1. Clonar o Repositório

Primeiro, clone o repositório para o seu ambiente local:

```bash
git clone <URL_DO_REPOSITORIO>
cd frontend
```
### 2. Instalar as Dependências

Execute o seguinte comando para instalar todas as dependências do projeto:

```bash
npm install
```

### 3. Executar o Projeto Localmente

Após instalar as dependências, você pode iniciar o servidor de desenvolvimento executando o comando:

```bash
npm run dev
```

Isso iniciará o servidor na URL http://localhost:3001 (ou em uma porta diferente se a 3000 estiver em uso).

### 4. Acessar o Projeto

Abra o navegador e acesse http://localhost:3001. Você verá a página inicial do sistema de autenticação, onde poderá explorar todas as funcionalidades.

## Estrutura de Pastas

Aqui está a estrutura básica de pastas do projeto:

```bash
/frontend
  /app
    /dashboard      # Página do painel de controle
    /login          # Página de login
    /register       # Página de registro
    /search         # Página para busca de CPFs
    /settings       # Página de configurações
  /components       # Componentes reutilizáveis
    /InputField.tsx # Componente para campos de entrada
    /EmailInput.tsx # Componente para email
    /PasswordInput.tsx # Componente para senha
    /ConfirmPasswordInput.tsx # Componente para confirmação de senha
    /ErrorMessage.tsx # Componente para exibição de erro
  /public
    /assets         # Imagens e outros assets estáticos
  /styles
    /globals.css    # Arquivo de estilo global
  next.config.js     # Arquivo de configuração do Next.js
  package.json       # Dependências e scripts do projeto
  tsconfig.json      # Configuração do TypeScript
```

## Como Contribuir

1. Faça um fork do repositório.
2. Crie uma branch para sua feature (git checkout -b feature/nome-da-feature).
3. Faça suas alterações e commit (git commit -am 'Adicionando nova feature').
4. Push para a branch (git push origin feature/nome-da-feature).
5. Abra um Pull Request no repositório original.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para mais detalhes.

## Funcionalidade do Sistema

O sistema de autenticação que você está implementando oferece as seguintes funcionalidades principais:

### 1. Login e Registro de Usuários

A página de login permite que os usuários entrem com suas credenciais, enquanto a página de registro permite que novos usuários se cadastrem no sistema. O backend processa as requisições para verificar credenciais ou criar novos registros.

### 2. Painel de Controle

O painel de controle (dashboard) é a área principal do sistema, onde o usuário pode acessar e interagir com os dados, como buscar informações associadas aos CPFs e visualizar os resultados em uma tabela.

### 3. Busca de CPFs e Exibição dos Resultados

Na página de busca, os usuários podem fornecer um ou mais CPFs e, ao clicar em "Buscar", o sistema consulta o backend e retorna as informações associadas aos CPFs. Os dados são exibidos em uma tabela organizada.

### 4. Exportação para o Google Sheets

Após buscar os dados, o usuário tem a opção de exportar os resultados para o Google Sheets, facilitando o gerenciamento e armazenamento dos dados coletados.

## Como Funciona a Busca de CPFs

1. O usuário insere um ou mais CPFs no campo de busca, separados por vírgulas ou linhas.
2. O sistema envia os CPFs para o backend, onde as informações associadas são buscadas e retornadas.
3. As informações retornadas são exibidas em uma tabela no frontend.
4. O usuário pode optar por exportar os dados para o Google Sheets para facilitar a gestão.

## Exemplo de Dados Exibidos na Tabela

A tabela exibe as seguintes colunas com os dados dos CPFs:

- **CPF**: O número do CPF.
- **Nome**: Nome do titular do CPF.
- **Email**: O email associado ao CPF.
- **Telefone**: O telefone associado ao CPF.
- **Status**: O status da operação, como "Processado", "Aguardando", etc.

## Feedback Visual e Validação de Formulários

O sistema conta com validação avançada para garantir que os dados inseridos pelo usuário sejam válidos:

- **Validação de CPF**: Verifica se o CPF fornecido segue o formato correto (com ou sem máscara).
- **Validação de Campos Obrigatórios**: Garante que todos os campos obrigatórios sejam preenchidos antes de permitir a submissão do formulário.
- **Mensagens de Erro**: Mensagens de erro são exibidas caso o usuário insira dados inválidos ou deixe de preencher campos obrigatórios.

## Personalização e Tema Escuro

O layout do sistema permite a alternância entre os modos claro e escuro, com a opção de salvar a preferência do usuário no armazenamento local.

## 

Nota: Este é um projeto em desenvolvimento. Para quaisquer problemas ou sugestões, fique à vontade para abrir uma issue ou enviar um pull request.