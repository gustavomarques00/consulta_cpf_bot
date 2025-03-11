# **Consulta CPF Bot** 🤖🔍  
Automatiza consultas de CPFs via Telegram e armazena os resultados no Google Sheets.  

---

## **📌 Funcionalidades**
✅ **Consulta Automatizada:** O bot envia CPFs para consulta no Telegram.  
✅ **Armazenamento Seguro:** Os dados são automaticamente registrados no **Google Sheets**.  
✅ **Reagendamento Inteligente:** Se um CPF não receber resposta, ele será reagendado para nova tentativa.  
✅ **Gerenciamento de Arquivos:** Arquivos temporários são excluídos automaticamente após processamento.  
✅ **Monitoramento de Progresso:** Exibe quantos CPFs foram processados e o tempo estimado restante.  
✅ **Bot de Orientação:** Um segundo bot auxilia na configuração e execução do sistema.  

---

## **📚 Pré-requisitos**
1. **Python 3.8+** instalado ([Baixar Python](https://www.python.org/downloads/))
2. **Git** instalado ([Baixar Git](https://git-scm.com/downloads))
3. **Chave de API do Telegram** (Gerada no [BotFather](https://t.me/BotFather))
4. **Credenciais do Google Sheets** (Criadas no [Google Cloud](https://console.cloud.google.com/))

---

## **🚀 Como Configurar e Executar**
### **1️⃣ Clonar o Repositório**
```bash
git clone https://github.com/gustavomarques00/consulta_cpf_bot.git
cd consulta_cpf_bot
```

### **2️⃣ Criar e Configurar o Arquivo `.env`**
Crie um arquivo `.env` na raiz do projeto e adicione:

```
API_ID=SEU_API_ID
API_HASH=SEU_API_HASH
PHONE_NUMBER=+55XXXXXXXXXXX
BOT_USERNAME=@SeuBot
CREDENTIALS_FILE=credenciais.json
SHEET_NAME=Operação JUVO
WORKSHEET_DATA=Dados
WORKSHEET_CHECKER=Checker
```

> **⚠️ Importante:** **Substitua os valores acima** pelos seus dados reais.

### **3️⃣ Instalar as Dependências**
```bash
pip install -r requirements.txt
```

### **4️⃣ Executar o Script de Consulta**
```bash
python ExtrairPuxadas.py
```

### **5️⃣ Executar o Bot de Orientação**
Para receber orientações sobre o uso do sistema via Telegram, execute:
```bash
python BotOrientacao.py
```

---

## **🛠 Solução de Problemas**
Se encontrar problemas, tente:  
- Verificar se o **arquivo `credenciais.json`** está na pasta correta.  
- Confirmar se o **Google Sheets** foi configurado corretamente.  
- Certificar-se de que **as bibliotecas necessárias** foram instaladas (`pip install -r requirements.txt`).  
- Conferir se o **bot do Telegram** está ativo e autorizado para o número de telefone.  

Se precisar de mais ajuda, execute o comando `/suporte` no **Bot de Orientação**.

---

## **🛠️ Tecnologias Utilizadas**
- **Python 3.8+**  
- **Telethon** → Para comunicação com o Telegram  
- **Google Sheets API** → Para armazenar os dados  
- **OAuth2Client** → Para autenticação segura  
- **Dotenv** → Para gerenciamento de variáveis de ambiente  

---

## **📝 Licença**
Este projeto está sob a **licença MIT**. Sinta-se livre para usar e modificar conforme necessário.

---

### **🎯 Melhorias Futuras**
- 🔹 Criar uma interface gráfica para facilitar o uso.  
- 🔹 Implementar notificações automáticas via Telegram ao concluir as consultas.  
- 🔹 Melhorar logs e relatórios do processamento.

---

🚀 **Agora tudo pronto para rodar!**  
Se tiver dúvidas, use o **Bot de Orientação** ou consulte este README.  

🔥 **Contribuições são bem-vindas!**  