import os
from telethon import TelegramClient, events

# ========== CONFIGURAÇÕES DO BOT ==========
API_ID = 24458905  # O mesmo ID do script principal
API_HASH = '76c15cf009ecffbfa917c8c2423a412d'  # O mesmo HASH do script principal
BOT_TOKEN = '7567654568:AAGx5eJ_ok9Iyd4gbo7danG6I2sk3rL3bIQ'  # Insira o token do bot gerado no BotFather

# Criar cliente do bot
bot = TelegramClient('orientacao_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ========== FUNÇÕES AUXILIARES ==========
def verificar_ambiente():
    """Verifica se os arquivos e pacotes necessários estão instalados corretamente."""
    problemas = []

    # Verifica se o arquivo de credenciais existe
    if not os.path.exists("credenciais.json"):
        problemas.append("❌ O arquivo `credenciais.json` não foi encontrado!")

    # Verifica se os pacotes necessários estão instalados
    try:
        import gspread
        import oauth2client
        import telethon
    except ImportError:
        problemas.append("❌ Alguns pacotes necessários não estão instalados! Use o comando: `pip install gspread oauth2client telethon`")

    return problemas

# ========== COMANDOS DO BOT ==========
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Mensagem de boas-vindas e introdução aos comandos."""
    await event.respond(
        "🤖 **Bem-vindo ao Bot de Orientação!**\n\n"
        "Eu te guiarei na configuração e uso do script de consulta de CPFs.\n\n"
        "🔹 **Comandos disponíveis:**\n"
        "📌 `/instalacao` - Como instalar os pacotes necessários.\n"
        "📌 `/configuracao` - Como configurar o script corretamente.\n"
        "📌 `/execucao` - Como rodar o script.\n"
        "📌 `/verificar` - Verifica se o ambiente está pronto.\n"
        "📌 `/suporte` - Solução de problemas comuns.\n\n"
        "Digite um comando para continuar! 🚀"
    )

@bot.on(events.NewMessage(pattern='/instalacao'))
async def instalacao(event):
    """Explica como instalar os pacotes necessários."""
    await event.respond(
        "🔧 **INSTALAÇÃO DOS PACOTES NECESSÁRIOS** 🔧\n\n"
        "Antes de rodar o script, você precisa instalar alguns pacotes. Execute este comando no terminal:\n"
        "```\n"
        "pip install gspread oauth2client telethon\n"
        "```\n"
        "Depois que os pacotes forem instalados, você pode configurar o script digitando `/configuracao`."
    )

@bot.on(events.NewMessage(pattern='/configuracao'))
async def configuracao(event):
    """Explica como configurar o script corretamente."""
    await event.respond(
        "⚙ **CONFIGURAÇÃO DO SCRIPT** ⚙\n\n"
        "1️⃣ **Baixe o script e coloque-o na sua pasta de trabalho.**\n"
        "2️⃣ **Coloque o arquivo `credenciais.json` na mesma pasta do script.**\n"
        "3️⃣ **Verifique as configurações do Telegram dentro do código:**\n"
        "   - API_ID e API_HASH\n"
        "   - Seu número de telefone\n"
        "   - Nome do bot\n"
        "4️⃣ **A planilha já está configurada, então você pode rodar o script!**\n\n"
        "Para saber como rodar, digite `/execucao`."
    )

@bot.on(events.NewMessage(pattern='/execucao'))
async def execucao(event):
    """Explica como rodar o script."""
    await event.respond(
        "▶ **EXECUTANDO O SCRIPT** ▶\n\n"
        "Agora você pode rodar o script com este comando no terminal:\n"
        "```\n"
        "python nome_do_script.py\n"
        "```\n"
        "Se tudo estiver certo, o bot começará a processar os CPFs e os dados aparecerão na planilha.\n"
        "Caso encontre problemas, digite `/suporte` para ver as soluções mais comuns."
    )

@bot.on(events.NewMessage(pattern='/verificar'))
async def verificar(event):
    """Verifica se o ambiente do usuário está pronto para rodar o script."""
    problemas = verificar_ambiente()

    if problemas:
        resposta = "⚠️ **Foram encontrados alguns problemas:**\n\n" + "\n".join(problemas)
    else:
        resposta = "✅ **Tudo está configurado corretamente!** Você pode rodar o script com `/execucao`."

    await event.respond(resposta)

@bot.on(events.NewMessage(pattern='/suporte'))
async def suporte(event):
    """Fornece soluções para problemas comuns."""
    await event.respond(
        "🛠 **SUPORTE E SOLUÇÃO DE PROBLEMAS** 🛠\n\n"
        "Caso enfrente algum problema, verifique:\n"
        "✅ O arquivo `credenciais.json` está na pasta correta?\n"
        "✅ O Python e os pacotes necessários estão instalados? (`pip install gspread oauth2client telethon`)\n"
        "✅ Você rodou o comando `python nome_do_script.py` corretamente?\n"
        "✅ Sua conexão com a internet está funcionando?\n\n"
        "Se ainda precisar de ajuda, entre em contato!"
    )

# Iniciar o bot
print("🚀 Bot de orientação iniciado!")
bot.run_until_disconnected()
