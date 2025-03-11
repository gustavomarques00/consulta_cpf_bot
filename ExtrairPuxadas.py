import time
import re
import random
import os
import gspread
import dotenv
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaDocument
from oauth2client.service_account import ServiceAccountCredentials

# ========== CARREGANDO VARIÁVEIS DE AMBIENTE ==========
dotenv.load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
BOT_USERNAME = os.getenv("BOT_USERNAME")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credenciais.json")

SHEET_NAME = os.getenv("SHEET_NAME", "Operação JUVO")
WORKSHEET_DATA = os.getenv("WORKSHEET_DATA", "Dados")
WORKSHEET_CHECKER = os.getenv("WORKSHEET_CHECKER", "Checker")

DOWNLOAD_FOLDER = "downloads/"

# ========== VALIDAÇÕES INICIAIS ==========
if not API_ID or not API_HASH or not PHONE_NUMBER or not BOT_USERNAME:
    raise ValueError("❌ Erro: Configurações do Telegram não definidas corretamente no .env.")

if not os.path.exists(CREDENTIALS_FILE):
    raise FileNotFoundError(f"❌ O arquivo {CREDENTIALS_FILE} não foi encontrado! Verifique as credenciais do Google Sheets.")

# ========== FUNÇÕES AUXILIARES ==========
def autenticar_google_sheets():
    """Autentica no Google Sheets e retorna o objeto da planilha."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME)
    except Exception as e:
        print(f"❌ Erro na autenticação do Google Sheets: {e}")
        return None

def obter_data_hora():
    """Retorna a data e hora atual no formato 'DD/MM/YYYY HH:MM:SS'."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def extrair_info(pattern, resposta):
    """Extrai informação da resposta do bot usando regex de forma segura."""
    match = re.search(pattern, resposta)
    return match.group(1).strip() if match else "Não Informado"

def processar_arquivo_txt(caminho_arquivo):
    """Lê e processa as informações contidas no arquivo .txt enviado pelo bot."""
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as file:
            resposta = file.read()
        return resposta
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo {caminho_arquivo}: {e}")
        return None

def remover_linha_checker(sheet_checker, cpf_processo):
    """Remove apenas a linha correspondente ao CPF processado na aba 'Checker'."""
    try:
        dados_checker = sheet_checker.get_all_values()
        if len(dados_checker) <= 1:
            print("⚠️ Nenhum dado encontrado na aba 'Checker'.")
            return

        for i, linha in enumerate(dados_checker[1:], start=2):
            if linha[0] == cpf_processo:
                sheet_checker.delete_rows(i)
                print(f"✅ CPF {cpf_processo} removido da aba 'Checker'.")
                return
        print(f"⚠️ CPF {cpf_processo} não encontrado na aba 'Checker'.")
    except Exception as e:
        print(f"❌ Erro ao remover CPF {cpf_processo}: {e}")

def reagendar_cpf_checker(sheet_checker, cpf_falha):
    """Reinsere um CPF na aba 'Checker' em uma posição aleatória caso a resposta não tenha sido obtida."""
    try:
        dados_checker = sheet_checker.get_all_values()
        posicao_aleatoria = random.randint(2, max(len(dados_checker), 2))
        sheet_checker.insert_row([cpf_falha], posicao_aleatoria)
        print(f"🔄 CPF {cpf_falha} foi reagendado para a posição {posicao_aleatoria}.")
    except Exception as e:
        print(f"❌ Erro ao reagendar CPF {cpf_falha}: {e}")

# ========== PROCESSAMENTO ==========
def processar_cpfs():
    """Processa CPFs na aba 'Checker' de baixo para cima e insere os dados no Google Sheets."""
    sheet = autenticar_google_sheets()
    if sheet is None:
        return

    sheet_checker = sheet.worksheet(WORKSHEET_CHECKER)
    sheet_data = sheet.worksheet(WORKSHEET_DATA)

    # Obtém todas as linhas da aba 'Checker'
    dados_checker = sheet_checker.get_all_values()
    if len(dados_checker) <= 1:
        print("⚠️ Nenhum CPF encontrado na aba 'Checker'.")
        return

    lista_cpfs = [linha[0] for linha in dados_checker[1:]][::-1]

    with TelegramClient('session_name', API_ID, API_HASH) as client:
        client.start(PHONE_NUMBER)

        for cpf in lista_cpfs:
            client.send_message(BOT_USERNAME, f"/cpf {cpf}")
            time.sleep(10)  # Aguarda resposta

            resposta = None
            caminho_arquivo = f"{DOWNLOAD_FOLDER}dados_{cpf}.txt"

            for message in client.iter_messages(BOT_USERNAME, limit=1):
                print(f"🔎 Buscando CPF: {cpf}")

                if isinstance(message.media, MessageMediaDocument):
                    message.download_media(file=caminho_arquivo)
                    resposta = processar_arquivo_txt(caminho_arquivo)
                else:
                    resposta = message.text

                if not resposta:
                    print(f"⚠️ Falha ao obter dados para o CPF {cpf}. Reagendando...")
                    reagendar_cpf_checker(sheet_checker, cpf)
                    continue

                # Extração segura dos dados
                nome_info = extrair_info(r'Nome:\s+(.+)', resposta)
                cpf_info = extrair_info(r'CPF:\s+(\d+)', resposta)
                nascimento_info = extrair_info(r'Nascimento:\s+([\d-]+)', resposta)
                sexo_info = extrair_info(r'Sexo:\s+(\w)', resposta)
                renda_info = extrair_info(r'Renda Atual:\s+(\d+)', resposta)
                poder_aquisitivo_info = extrair_info(r'Poder aquisitivo:\s*([^\n\r]+)', resposta)

                # Define status conforme poder aquisitivo
                status = "Enviada" if poder_aquisitivo_info not in ["BAIXO", "MUITO BAIXO", "MEDIO BAIXO","Não Informado"] else "Não Enviada"

                # Inserir dados na planilha
                sheet_data.append_row([cpf_info, nascimento_info, nome_info, sexo_info, renda_info, poder_aquisitivo_info, status, obter_data_hora()])
                
                # Excluir arquivo após uso
                if os.path.exists(caminho_arquivo):
                    os.remove(caminho_arquivo)

            remover_linha_checker(sheet_checker, cpf)

if __name__ == "__main__":
    print("🚀 Iniciando Processamento")
    processar_cpfs()
    print("✅ Processamento Finalizado")
