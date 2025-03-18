from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import os
from datetime import datetime
from threading import Thread
import random
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import Config  # Importando a classe de configuração
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaDocument

app = Flask(__name__)
CORS(app)  # Permitir CORS para o frontend React

# ========== FUNÇÕES AUXILIARES ==========

def autenticar_google_sheets():
    """Autentica no Google Sheets e retorna a planilha."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(Config.CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        return client.open(Config.SHEET_NAME)
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
            return file.read()
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

# Função real para processar CPFs
def processar_cpf(cpf, sheet_data, sheet_checker):
    """Processa o CPF na aba 'Checker' de baixo para cima e insere os dados no Google Sheets."""
    # Enviar mensagem para o bot Telegram
    with TelegramClient('session_name', Config.API_ID, Config.API_HASH) as client:
        client.start(Config.PHONE_NUMBER)
        client.send_message(Config.BOT_USERNAME, f"/cpf {cpf}")
        time.sleep(10)

        resposta = None
        caminho_arquivo = os.path.join(Config.DOWNLOAD_FOLDER, f"dados_{cpf}.txt")

        # Definindo o tempo máximo de espera
        tempo_maximo_espera = 30
        tempo_inicio = time.time()

        while time.time() - tempo_inicio < tempo_maximo_espera:
            for message in client.iter_messages(Config.BOT_USERNAME, limit=1):
                if isinstance(message.media, MessageMediaDocument):
                    message.download_media(file=caminho_arquivo)
                    resposta = processar_arquivo_txt(caminho_arquivo)
                else:
                    resposta = message.text

                if resposta:
                    break

        if not resposta:
            print(f"⚠️ Falha ao obter dados para {cpf}. Reagendando...")
            reagendar_cpf_checker(sheet_checker, cpf)
            return

        # Extração de dados
        nome_info = extrair_info(r'Nome:\s+(.+)', resposta)
        cpf_info = extrair_info(r'CPF:\s+(\d+)', resposta)
        nascimento_info = extrair_info(r'Nascimento:\s+([\d-]+)', resposta)
        sexo_info = extrair_info(r'Sexo:\s+(\w)', resposta)
        renda_info = extrair_info(r'Renda Atual:\s+(\d+)', resposta)
        poder_aquisitivo_info = extrair_info(r'Poder aquisitivo:\s*([^\n\r]+)', resposta)

        sexo_map = {"M": "Masculino", "F": "Feminino", "I": "Indefinido"}
        sexo_info = sexo_map.get(sexo_info, "Indefinido")

        if nascimento_info != "Não Informado":
            try:
                nascimento_info = datetime.strptime(nascimento_info, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                nascimento_info = "Não Informado"

        telefone_info = re.findall(r'Telefone:\s+\((\d{2})\)(9\d{8})', resposta)
        telefone_final = f"({telefone_info[0][0]}){telefone_info[0][1]}" if telefone_info else "Não Informado"

        email_info = re.findall(r'Email:\s+([^\s]+)', resposta)
        email_final = email_info[0] if email_info else "Não Informado"

        nome_split = nome_info.split()
        nome = nome_split[0] if nome_split else "Não Informado"
        sobrenome = " ".join(nome_split[1:]) if len(nome_split) > 1 else "Não Informado"

        status = "Enviada" if "BAIXO" not in poder_aquisitivo_info.upper() and poder_aquisitivo_info != "Não Informado" else "Não Enviada"
        data_hora_extracao = obter_data_hora()

        sheet_data.append_row([
            cpf_info, nascimento_info, email_final, nome, sobrenome,
            telefone_final, sexo_info, renda_info, poder_aquisitivo_info,
            status, data_hora_extracao
        ])

        try:
            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)
        except Exception as e:
            print(f"⚠️ Erro ao excluir {caminho_arquivo}: {e}")

        remover_linha_checker(sheet_checker, cpf)

# Endpoint para iniciar o processamento de CPFs
@app.route('/processar', methods=['POST'])
def processar_cpfs_request():
    cpfs = request.json.get("cpfs")
    if not cpfs:
        return jsonify({"error": "CPFs não fornecidos"}), 400

    try:
        sheet = autenticar_google_sheets()
        if sheet is None:
            return jsonify({"error": "Erro na autenticação do Google Sheets!"}), 500

        sheet_checker = sheet.worksheet(Config.WORKSHEET_CHECKER)
        sheet_data = sheet.worksheet(Config.WORKSHEET_DATA)
    except Exception as e:
        return jsonify({"error": f"Erro ao acessar planilhas: {str(e)}"}), 500

    resultados = []

    # Iniciar threads para processamento de cada CPF
    def processar_em_thread(cpf):
        processar_cpf(cpf, sheet_data, sheet_checker)

    threads = []
    for cpf in cpfs:
        thread = Thread(target=processar_em_thread, args=(cpf,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return jsonify({"message": "Processamento concluído!"})

if __name__ == '__main__':
    app.run(debug=True)
