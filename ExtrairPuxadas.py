import time
import re
import random
import os
import gspread
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaDocument
from oauth2client.service_account import ServiceAccountCredentials

# ========== CONFIGURAÇÕES ==========
API_ID = 24458905
API_HASH = '76c15cf009ecffbfa917c8c2423a412d'
PHONE_NUMBER = '+5513991729587'
BOT_USERNAME = '@HashiroSearchProBot'

SHEET_NAME = "Operação JUVO"
WORKSHEET_DATA = "Dados"
WORKSHEET_CHECKER = "Checker"
CREDENTIALS_FILE = "credenciais.json"
DOWNLOAD_FOLDER = "downloads/"  # Pasta onde os arquivos .txt serão salvos

# ========== FUNÇÕES AUXILIARES ==========
def autenticar_google_sheets():
    """Autentica no Google Sheets e retorna o objeto da planilha."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME)
    except Exception as e:
        print(f"Erro na autenticação do Google Sheets: {e}")
        return None

def obter_data_hora():
    """Retorna a data e hora atual no formato 'DD/MM/YYYY HH:MM:SS'."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def extrair_info(pattern, resposta):
    """Extrai informação da resposta do bot usando regex."""
    match = re.search(pattern, resposta)
    return match.group(1).strip() if match else "Não Informado"

def processar_arquivo_txt(caminho_arquivo):
    """Lê e processa as informações contidas no arquivo .txt enviado pelo bot."""
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as file:
            resposta = file.read()
        return resposta
    except Exception as e:
        print(f"Erro ao ler o arquivo {caminho_arquivo}: {e}")
        return None

def remover_linha_checker(sheet_checker, cpf_processo):
    """Remove apenas a linha correspondente ao CPF processado na aba 'Checker'."""
    try:
        dados_checker = sheet_checker.get_all_values()
        if not dados_checker or len(dados_checker) <= 1:
            print("Nenhum dado encontrado na aba 'Checker' para remover.")
            return

        for i, linha in enumerate(dados_checker[1:], start=2):  # Começa a contagem a partir da segunda linha
            if linha[0] == cpf_processo:
                sheet_checker.delete_rows(i)  # Remove a linha correta
                print(f"✅ Linha com CPF {cpf_processo} removida da aba 'Checker'.")
                return

        print(f"⚠️ CPF {cpf_processo} não encontrado na aba 'Checker'. Nenhuma linha foi removida.")

    except Exception as e:
        print(f"❌ Erro ao remover CPF {cpf_processo} da aba 'Checker': {e}")

def reagendar_cpf_checker(sheet_checker, cpf_falha):
    """Reinsere um CPF na aba 'Checker' em uma posição aleatória caso a resposta não tenha sido obtida."""
    try:
        dados_checker = sheet_checker.get_all_values()
        total_linhas = len(dados_checker)  # Conta quantas linhas já existem

        # Define uma posição aleatória (mínimo 2 para não sobrescrever o cabeçalho)
        posicao_aleatoria = random.randint(2, total_linhas + 1)

        # Insere o CPF de volta na aba "Checker" em uma posição aleatória
        sheet_checker.insert_row([cpf_falha], posicao_aleatoria)

        print(f"🔄 CPF {cpf_falha} foi reagendado para a posição {posicao_aleatoria} na aba 'Checker'.")
    except Exception as e:
        print(f"❌ Erro ao reagendar CPF {cpf_falha}: {e}")

def contabilizar_progresso(sheet_checker, sheet_data, tempo_medio_por_cpf=40):
    """
    Contabiliza o progresso do processamento de CPFs:
    - Quantos já foram processados
    - Quantos ainda faltam
    - Tempo médio estimado para concluir a fila
    
    :param sheet_checker: Planilha do Google Sheets - Aba "Checker"
    :param sheet_data: Planilha do Google Sheets - Aba "Dados"
    :param tempo_medio_por_cpf: Tempo médio (em segundos) para processar um CPF
    """
    try:
        # Obtém quantos CPFs ainda estão na aba "Checker" (pendentes)
        dados_checker = sheet_checker.get_all_values()
        total_pendentes = len(dados_checker) - 1 if len(dados_checker) > 1 else 0  # Remove o cabeçalho

        # Obtém quantos CPFs já foram processados na aba "Dados"
        dados_processados = sheet_data.get_all_values()
        total_processados = len(dados_processados) - 1 if len(dados_processados) > 1 else 0  # Remove o cabeçalho

        # Calcula o tempo estimado para concluir a fila pendente
        tempo_estimado_min = (total_pendentes * tempo_medio_por_cpf) // 60
        tempo_estimado_seg = (total_pendentes * tempo_medio_por_cpf) % 60

        print(f"📊 Progresso do Processamento:")
        print(f"✅ CPFs Processados: {total_processados}")
        print(f"⏳ CPFs Pendentes: {total_pendentes}")
        print(f"⏱️ Tempo estimado restante: {tempo_estimado_min} min {tempo_estimado_seg} seg")

        return total_processados, total_pendentes, tempo_estimado_min, tempo_estimado_seg

    except Exception as e:
        print(f"❌ Erro ao contabilizar progresso: {e}")
        return 0, 0, 0, 0  # Retorna valores padrão caso ocorra erro

# ========== PROCESSAMENTO ==========
def processar_cpfs():
    """Processa CPFs na aba 'Checker' de baixo para cima e insere os dados no Google Sheets."""
    sheet = autenticar_google_sheets()
    if sheet is None:
        return

    sheet_checker = sheet.worksheet(WORKSHEET_CHECKER)
    sheet_data = sheet.worksheet(WORKSHEET_DATA)

    # Exibir progresso inicial
    total_proc, total_pend, tempo_min, tempo_seg = contabilizar_progresso(sheet_checker, sheet_data)
    print("\n=== INICIANDO PROCESSAMENTO ===")
    print(f"✅ Processados: {total_proc} | ⏳ Pendentes: {total_pend} | ⏱️ Tempo estimado: {tempo_min} min {tempo_seg} seg")
    
    # Obtém todas as linhas da aba 'Checker'
    dados_checker = sheet_checker.get_all_values()
    if not dados_checker or len(dados_checker) <= 1:
        print("Nenhum CPF encontrado na aba 'Checker'.")
        return

    # Processa os CPFs de baixo para cima
    lista_cpfs = [linha[0] for linha in dados_checker[1:]][::-1]

    with TelegramClient('session_name', API_ID, API_HASH) as client:
        client.start(PHONE_NUMBER)

        for cpf in lista_cpfs:
            client.send_message(BOT_USERNAME, f"/cpf {cpf}")
            time.sleep(10)  # Aguarda resposta

            resposta = None
            caminho_arquivo = f"{DOWNLOAD_FOLDER}dados_{cpf}.txt"

            for message in client.iter_messages(BOT_USERNAME, limit=1):
                print(f"\n=== Buscando CPF: {cpf} ===")

                if isinstance(message.media, MessageMediaDocument):
                    message.download_media(file=caminho_arquivo)
                    print(f"📥 Arquivo {caminho_arquivo} baixado com sucesso!")
                    resposta = processar_arquivo_txt(caminho_arquivo)
                else:
                    resposta = message.text

                if not resposta:
                    print(f"⚠️ Falha ao obter dados para o CPF {cpf}. Reagendando para nova tentativa...")
                    reagendar_cpf_checker(sheet_checker, cpf)
                    continue

                # **Extração de dados**
                nome_info = extrair_info(r'Nome:\s+(.+)', resposta)
                cpf_info = extrair_info(r'CPF:\s+(\d+)', resposta)
                nascimento_info = extrair_info(r'Nascimento:\s+([\d-]+)', resposta)
                sexo_info = extrair_info(r'Sexo:\s+(\w)', resposta)
                poder_aquisitivo_info = extrair_info(r'Poder aquisitivo:\s*([^\n\r]+)', resposta)

                # **Correção da extração da Renda**
                renda_match = re.search(r'Renda Atual:\s+(\d+)', resposta)
                renda_info = renda_match.group(1) if renda_match else "Não Informado"

                # **Formatando Sexo**
                sexo_map = {"M": "Masculino", "F": "Feminino", "I": "Indefinido"}
                sexo_info = sexo_map.get(sexo_info, "Indefinido")

                # **Definir Status baseado no Poder Aquisitivo**
                if poder_aquisitivo_info in ["BAIXO", "MUITO BAIXO", "MEDIO BAIXO","Não Informado"]:
                    status = "Não Enviada"
                else:
                    status = "Enviada"

                # **Capturar primeiro número de celular**
                telefone_info = re.findall(r'Telefone:\s+\((\d{2})\)(9\d{8})', resposta)
                telefone_final = f"({telefone_info[0][0]}){telefone_info[0][1]}" if telefone_info else "Não Informado"

                # **Capturar email**
                email_info = re.findall(r'Email:\s+([^\s]+)', resposta)
                email_final = email_info[0] if email_info else "Não Informado"

                # **Separar nome e sobrenome**
                nome_split = nome_info.split()
                nome = nome_split[0] if nome_split else "Não Informado"
                sobrenome = " ".join(nome_split[1:]) if len(nome_split) > 1 else "Não Informado"

                # **Adiciona Data/Hora da Extração**
                data_hora_extracao = obter_data_hora()

                # **Inserir dados na planilha "Dados"**
                sheet_data.append_row([
                    cpf_info, nascimento_info, email_final, nome, sobrenome,
                    telefone_final, sexo_info, renda_info, poder_aquisitivo_info,
                    status, data_hora_extracao
                ])

                # **Excluir o arquivo após processar**
                try:
                    if os.path.exists(caminho_arquivo):
                        os.remove(caminho_arquivo)
                        print(f"🗑️ Arquivo {caminho_arquivo} excluído após processamento.")
                except Exception as e:
                    print(f"❌ Erro ao excluir arquivo {caminho_arquivo}: {e}")

                # Atualizar progresso após cada CPF processado
                total_proc, total_pend, tempo_min, tempo_seg = contabilizar_progresso(sheet_checker, sheet_data)
                print(f"📊 Atualização: ✅ Processados: {total_proc} | ⏳ Pendentes: {total_pend} | ⏱️ Tempo estimado: {tempo_min} min {tempo_seg} seg")

            # **Remover a linha processada do Checker**
            remover_linha_checker(sheet_checker, cpf)

    # Exibir status final do processamento
    total_proc, total_pend, tempo_min, tempo_seg = contabilizar_progresso(sheet_checker, sheet_data)
    print("\n=== PROCESSAMENTO FINALIZADO ===")
    print(f"✅ Processados: {total_proc} | ⏳ Pendentes: {total_pend} | ⏱️ Tempo estimado: {tempo_min} min {tempo_seg} seg")
# ========== EXECUÇÃO ==========
if __name__ == "__main__":
    print("=== Iniciando Processamento ===")

    processar_cpfs()

    print("=== Processamento Finalizado ===")
